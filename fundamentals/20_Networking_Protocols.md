# 🌐 Networking & Protocols cho DE

> Hiểu network để debug pipelines nhanh hơn, design systems tốt hơn

---

## 📋 Mục Lục

1. [Tại Sao DE Cần Biết Network?](#tại-sao-de-cần-biết-network)
2. [OSI Model cho DE](#osi-model-cho-de)
3. [HTTP/REST APIs](#httprest-apis)
4. [TCP vs UDP](#tcp-vs-udp)
5. [DNS, Load Balancing, CDN](#dns-load-balancing-cdn)
6. [Network trong Cloud & Distributed Systems](#network-trong-cloud--distributed-systems)
7. [Debugging Network Issues](#debugging-network-issues)

---

## Tại Sao DE Cần Biết Network?

```mermaid
flowchart TB
    Net[Network Knowledge]
    Net --> API[API Integration]
    Net --> Debug[Debug Pipeline Failures]
    Net --> Design[System Design]
    Net --> Security[Security]
    
    API --> A1[Ingest from REST/gRPC]
    Debug --> D1[Timeout, Connection Refused]
    Design --> S1[Choose right protocol]
    Security --> SE1[VPC, Firewall, TLS]
```

### Các tình huống DE gặp hàng ngày

| Tình huống | Cần biết network gì |
|------------|---------------------|
| API ingestion fails | HTTP status codes, retry logic |
| Pipeline timeout | TCP connections, keep-alive |
| Spark shuffle slow | Network bandwidth, data locality |
| Kafka lag increasing | Throughput, partitioning |
| Connection refused | Firewall, VPC, security groups |
| SSL certificate error | TLS/SSL handshake |
| DNS resolution fails | DNS, service discovery |

---

## OSI Model cho DE

### 7 Layers (Focus vào layers DE cần)

```
Layer 7: Application   ← HTTP, gRPC, JDBC     *** DE focus ***
Layer 6: Presentation  ← TLS/SSL, encoding
Layer 5: Session        ← Connection pooling
Layer 4: Transport      ← TCP, UDP              ** DE cần hiểu **
Layer 3: Network        ← IP, routing           * Cloud VPC *
Layer 2: Data Link      ← MAC address
Layer 1: Physical       ← Cables (không cần biết)
```

### Layer 4 - Transport (TCP vs UDP)

| | TCP | UDP |
|--|-----|-----|
| **Reliability** | Guaranteed delivery | Best-effort |
| **Order** | Ordered | No order guarantee |
| **Use case DE** | Database connections, API | Logging, metrics, streaming (some) |
| **Speed** | Slower (handshake, ACK) | Faster (fire-and-forget) |
| **Example** | `psycopg2.connect()` | StatsD metrics |

```python
# TCP Connection (most DE work)
import socket

def check_service_available(host: str, port: int, timeout: int = 5) -> bool:
    """Check if a service is reachable on TCP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.error:
        return False

# Common DE ports
services = {
    "PostgreSQL": ("db-host", 5432),
    "MySQL": ("db-host", 3306),
    "Redis": ("cache-host", 6379),
    "Kafka": ("kafka-host", 9092),
    "Airflow Webserver": ("airflow-host", 8080),
    "Spark Master": ("spark-host", 7077),
    "Spark UI": ("spark-host", 4040),
}
```

---

## HTTP/REST APIs

### HTTP Methods cho API Ingestion

| Method | Mục đích | Idempotent | DE Use Case |
|--------|----------|------------|-------------|
| GET | Lấy data | ✅ Yes | Fetch records from API |
| POST | Tạo mới | ❌ No | Send data, trigger webhooks |
| PUT | Replace | ✅ Yes | Upsert records |
| PATCH | Update partial | ❌ No | Update specific fields |
| DELETE | Xóa | ✅ Yes | Remove records |

### HTTP Status Codes DE CẦN BIẾT

```python
class APIIngestionHandler:
    """Handle HTTP responses properly in pipelines"""
    
    def fetch_with_retry(self, url: str, max_retries: int = 3) -> dict:
        for attempt in range(max_retries):
            response = requests.get(url)
            
            match response.status_code:
                # 2xx: Success
                case 200:
                    return response.json()
                case 201:
                    return response.json()  # Created
                case 204:
                    return {}  # No Content
                
                # 3xx: Redirect
                case 301 | 302:
                    url = response.headers["Location"]
                    continue
                
                # 4xx: Client errors - DON'T RETRY
                case 400:
                    raise ValueError(f"Bad request: {response.text}")
                case 401:
                    raise PermissionError("Invalid API key")
                case 403:
                    raise PermissionError("Access forbidden")
                case 404:
                    raise FileNotFoundError(f"Endpoint not found: {url}")
                case 422:
                    raise ValueError(f"Invalid data: {response.text}")
                
                # 429: Rate Limited - RETRY with backoff
                case 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    time.sleep(retry_after)
                    continue
                
                # 5xx: Server errors - RETRY
                case 500 | 502 | 503 | 504:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise ConnectionError(f"Server error after {max_retries} attempts")
        
        raise ConnectionError("Max retries exceeded")
```

### Key Rules

```
Rule 1: 4xx = Your problem (bad request/auth) → Fix code, DON'T retry
Rule 2: 429 = Rate limited → Respect Retry-After header
Rule 3: 5xx = Their problem → Retry with exponential backoff
Rule 4: Always set timeouts → Never hang indefinitely
Rule 5: Always check Content-Type → JSON vs XML vs CSV
```

### Pagination

```python
def fetch_all_pages(base_url: str) -> list[dict]:
    """
    Most APIs paginate results
    Common patterns: page-based, cursor-based, offset-based
    """
    all_records = []
    
    # Pattern 1: Page-based
    page = 1
    while True:
        response = requests.get(f"{base_url}?page={page}&per_page=100")
        data = response.json()
        all_records.extend(data["results"])
        
        if not data.get("next_page"):
            break
        page += 1
    
    # Pattern 2: Cursor-based (better for large datasets)
    cursor = None
    while True:
        params = {"limit": 100}
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(base_url, params=params)
        data = response.json()
        all_records.extend(data["results"])
        
        cursor = data.get("next_cursor")
        if not cursor:
            break
    
    return all_records
```

### Authentication

```python
# Common auth patterns for API ingestion

# 1. API Key (Header)
headers = {"X-API-Key": os.getenv("API_KEY")}
response = requests.get(url, headers=headers)

# 2. Bearer Token (OAuth2)
headers = {"Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"}
response = requests.get(url, headers=headers)

# 3. Basic Auth
response = requests.get(url, auth=("username", "password"))

# 4. OAuth2 flow (common for Google, Facebook APIs)
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

client = BackendApplicationClient(client_id=CLIENT_ID)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(token_url=TOKEN_URL, client_secret=CLIENT_SECRET)
response = oauth.get(url)
```

---

## Connection Pooling

> Mỗi connections tốn resources. Pool giúp reuse.

```python
# ❌ BAD: New connection per query
def query_bad(sql):
    conn = psycopg2.connect(host="...", port=5432, ...)
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    return result

# Mỗi lần: TCP handshake → Auth → Query → Close
# 1000 queries = 1000 connections = SLOW + DB overload

# ✅ GOOD: Connection pool
from psycopg2 import pool

connection_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    host="localhost",
    port=5432,
    dbname="warehouse",
    user="de_user",
    password=os.getenv("DB_PASS")
)

def query_good(sql):
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        connection_pool.putconn(conn)  # Return to pool, don't close!

# SQLAlchemy (recommended)
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host:5432/db",
    pool_size=10,          # Max connections in pool
    max_overflow=5,        # Extra connections allowed
    pool_timeout=30,       # Wait for available connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Check connection health before use
)
```

---

## DNS, Load Balancing, CDN

### DNS (Domain Name System)

```
Tại sao DE cần biết:
- API endpoints dùng domain names
- DNS failures → Pipeline fails
- DNS caching → Stale endpoints
- Service discovery in microservices
```

```python
# DNS Resolution
import socket

# What happens when you connect to "api.example.com"
ip = socket.gethostbyname("api.example.com")
# DNS lookup: "api.example.com" → "203.0.113.42"

# DNS TTL (Time To Live)
# - DNS records cached → Changes take time to propagate
# - If API changes IP, your pipeline might still use old IP
# - Solution: Don't cache DNS too long in your app

# Common DNS issues in DE:
# 1. "Could not resolve hostname" → DNS server down or wrong domain
# 2. Slow DNS → Add DNS caching or use IP directly
# 3. DNS-based load balancing → Different IPs each resolution
```

### Load Balancing

```
                ┌── Worker 1 (Spark executor)
Client ──→ LB ─┼── Worker 2 (Spark executor)
                └── Worker 3 (Spark executor)

DE encounters load balancers:
1. API endpoints (round-robin across servers)
2. Database read replicas 
3. Kafka brokers
4. Spark executors
```

```python
# When DE needs to handle load balancing
# Example: Read from multiple database replicas

class ReplicaRouter:
    def __init__(self, replicas: list[str]):
        self._replicas = replicas
        self._index = 0
    
    def get_read_connection(self) -> str:
        """Round-robin across read replicas"""
        replica = self._replicas[self._index % len(self._replicas)]
        self._index += 1
        return replica
    
    def get_write_connection(self) -> str:
        """Always write to primary"""
        return self._replicas[0]  # Primary is first

router = ReplicaRouter([
    "primary.db.example.com",
    "replica1.db.example.com",
    "replica2.db.example.com",
])
```

---

## Network trong Cloud & Distributed Systems

### VPC (Virtual Private Cloud)

```
VPC = Your private network in cloud

┌───────────────────── VPC (10.0.0.0/16) ─────────────────────┐
│                                                               │
│  ┌─── Public Subnet (10.0.1.0/24) ───┐                      │
│  │  Airflow Webserver (public access)  │                      │
│  │  API Gateway                        │                      │
│  └────────────────────────────────────┘                      │
│                                                               │
│  ┌─── Private Subnet (10.0.2.0/24) ──┐                      │
│  │  Spark Cluster (internal only)      │                      │
│  │  PostgreSQL (internal only)         │                      │
│  │  Kafka (internal only)              │                      │
│  └────────────────────────────────────┘                      │
│                                                               │
└──────────────────────────────────────────────────────────────┘

Rule: Databases và data processing → Private subnet
      Only entry points → Public subnet
```

### Security Groups (Firewall Rules)

```
DE thường gặp "Connection refused" vì security groups:

# Check: Port có mở không?
# PostgreSQL cần port 5432
# Kafka cần port 9092
# Spark cần ports 7077, 4040, etc.

Common mistakes:
1. Pipeline chạy ở server A, DB ở server B
   → Security group của B không allow inbound từ A
   
2. Spark workers cần communicate với nhau
   → Security group phải allow intra-cluster traffic

3. Output gửi ra ngoài (API call)
   → Need outbound rules (NAT Gateway for private subnet)
```

### Network trong Spark

```
Data Locality:
- Spark tries to process data where it resides
- Network transfer (shuffle) is EXPENSIVE

┌──────────────────────────┐
│  Shuffle = Network I/O   │
│                          │
│  Stage 1        Stage 2  │
│  ┌─────┐       ┌─────┐  │
│  │Map 1│──┐ ┌──│Red 1│  │
│  └─────┘  │ │  └─────┘  │
│  ┌─────┐  ├─┤  ┌─────┐  │
│  │Map 2│──┤ ├──│Red 2│  │
│  └─────┘  │ │  └─────┘  │
│  ┌─────┐  │ │  ┌─────┐  │
│  │Map 3│──┘ └──│Red 3│  │
│  └─────┘       └─────┘  │
│                          │
│  All-to-all = O(N × M)  │
│  This is why JOINs are   │
│  expensive!              │
└──────────────────────────┘
```

```python
# Spark network optimization
spark.conf.set("spark.sql.shuffle.partitions", 200)  # Default
# If data is small, reduce to avoid empty partitions
spark.conf.set("spark.sql.shuffle.partitions", 20)

# Broadcast JOIN (avoid shuffle for small tables)
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")
# small_df sent to ALL executors → No shuffle needed

# Data locality preference
spark.conf.set("spark.locality.wait", "3s")
```

### Network trong Kafka

```
Producer ──→ Broker 1 ──→ Consumer Group
             Broker 2 ──→ Consumer Group  
             Broker 3 ──→ Consumer Group

Key network concepts:
1. Replication: Data copied across brokers (network I/O)
2. Consumer lag: Network/processing bottleneck
3. Partition assignment: Balance network load
```

---

## Debugging Network Issues

### Toolkit cho DE

```bash
# 1. Check if host is reachable
ping api.example.com

# 2. Check if port is open (TCP)
nc -zv db.example.com 5432
# or
telnet db.example.com 5432

# 3. DNS lookup
nslookup api.example.com
dig api.example.com

# 4. Trace network path
traceroute api.example.com

# 5. Check HTTP endpoint
curl -v https://api.example.com/health

# 6. Check SSL certificate
openssl s_client -connect api.example.com:443

# 7. Monitor connections
netstat -an | grep 5432
ss -tuln | grep 5432

# 8. Check bandwidth
iperf3 -c target-host  # Between 2 servers
```

### Common DE Network Errors

```python
import requests
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
    TooManyRedirects,
)

def debug_api_connection(url: str):
    """Diagnose API connection issues"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"✅ Success: {response.status_code}")
    
    except ConnectionError as e:
        # Can't reach server at all
        print(f"🔴 Connection Error: {e}")
        print("Check: Is the server running? Firewall? VPN?")
        print("Try: ping/telnet to host and port")
    
    except Timeout:
        # Server didn't respond in time
        print("🔴 Timeout: Server took too long")
        print("Check: Server overloaded? Network slow? Increase timeout?")
    
    except HTTPError as e:
        # Server responded with error
        print(f"🟡 HTTP Error: {e.response.status_code}")
        if e.response.status_code == 401:
            print("→ Check API key/token")
        elif e.response.status_code == 429:
            print("→ Rate limited - add backoff")
        elif e.response.status_code >= 500:
            print("→ Server error - retry later")
```

### Python Connection Best Practices

```python
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def create_robust_session() -> requests.Session:
    """Production-grade HTTP session for pipelines"""
    session = requests.Session()
    
    # Retry strategy
    retry = Retry(
        total=3,
        backoff_factor=1,         # 1s, 2s, 4s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=10,      # Connection pool
        pool_maxsize=10,
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Default timeout
    session.request = functools.partial(session.request, timeout=30)
    
    return session

# Usage
session = create_robust_session()
response = session.get("https://api.example.com/data")
```

---

## gRPC vs REST

| | REST (HTTP/JSON) | gRPC (HTTP/2 + Protobuf) |
|--|------------------|--------------------------|
| **Format** | JSON (text) | Protobuf (binary) |
| **Speed** | Slower | 2-10x faster |
| **Size** | Larger | 5-10x smaller |
| **Streaming** | Workarounds | Native bi-directional |
| **Schema** | OpenAPI (optional) | Required (.proto) |
| **DE Use** | API ingestion | Inter-service, ML serving |

```protobuf
// Example: gRPC for ML feature serving
service FeatureStore {
    rpc GetFeatures(FeatureRequest) returns (FeatureResponse);
    rpc StreamFeatures(FeatureRequest) returns (stream FeatureResponse);
}

message FeatureRequest {
    string entity_id = 1;
    repeated string feature_names = 2;
}
```

---

## WebSockets & Streaming Protocols

```
DE streaming use cases:

1. WebSocket: Real-time data from APIs
   - Stock prices
   - Social media feeds
   - IoT sensor data

2. Server-Sent Events (SSE): One-way server → client
   - CDC change feeds
   - Log streaming

3. Kafka Protocol: High-throughput messaging
   - Event streaming
   - Log aggregation
```

```python
# WebSocket ingestion example
import websockets
import asyncio

async def ingest_websocket(url: str, callback):
    """Stream data from WebSocket API"""
    async with websockets.connect(url) as ws:
        # Subscribe to channel
        await ws.send(json.dumps({
            "type": "subscribe",
            "channels": ["orders"]
        }))
        
        # Continuous receive
        async for message in ws:
            data = json.loads(message)
            await callback(data)

# Usage: Real-time order ingestion
async def process_order(data):
    # Buffer and batch insert
    buffer.append(data)
    if len(buffer) >= 100:
        insert_batch(buffer)
        buffer.clear()
```

---

## Checklist

- [ ] Hiểu HTTP methods và status codes
- [ ] Implement retry logic với exponential backoff
- [ ] Hiểu TCP connections và connection pooling
- [ ] Biết debug network issues (curl, telnet, netstat)
- [ ] Hiểu VPC, security groups trong cloud
- [ ] Hiểu network impact trong Spark (shuffle, broadcast)
- [ ] Biết pagination patterns cho API ingestion
- [ ] Hiểu authentication (API key, OAuth2, Bearer token)

---

## Liên Kết

- [08_Data_Integration_APIs](08_Data_Integration_APIs.md) - Deep dive API integration
- [05_Distributed_Systems_Fundamentals](05_Distributed_Systems_Fundamentals.md) - Distributed networking
- [09_Security_Governance](09_Security_Governance.md) - TLS, encryption
- [10_Cloud_Platforms](10_Cloud_Platforms.md) - Cloud networking

---

*Hiểu network = Debug nhanh hơn + Design tốt hơn + Impress interviewer*
