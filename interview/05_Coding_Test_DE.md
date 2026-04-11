# 💻 Data Engineering Coding Test

> Bài tập coding thường gặp trong phỏng vấn DE - Focus thực tế, không deep algorithm

---

## 📋 Mục Lục

1. [Python Data Processing](#-python-data-processing)
2. [SQL Coding Challenges](#-sql-coding-challenges)
3. [Data Pipeline Tasks](#-data-pipeline-tasks)
4. [File Processing](#-file-processing)
5. [API Integration](#-api-integration)
6. [Testing & Validation](#-testing--validation)

---

## 🐍 Python Data Processing

### Task 1: Flatten Nested JSON

**Problem:**
```python
# Input: Nested API response
data = {
    "user_id": 123,
    "profile": {
        "name": "John",
        "contact": {
            "email": "john@example.com",
            "phone": "123456"
        }
    },
    "orders": [
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 200}
    ]
}

# Expected output: Flat dictionary ready for database
# {
#     "user_id": 123,
#     "profile_name": "John",
#     "profile_contact_email": "john@example.com",
#     "profile_contact_phone": "123456",
#     "orders": '[{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]'
# }
```

**Solution:**
```python
import json
from typing import Any

def flatten_json(data: dict, prefix: str = "") -> dict:
    """Flatten nested JSON to single level dict"""
    result = {}
    
    for key, value in data.items():
        new_key = f"{prefix}{key}" if prefix else key
        
        if isinstance(value, dict):
            # Recursively flatten nested dicts
            result.update(flatten_json(value, f"{new_key}_"))
        elif isinstance(value, list):
            # Lists get JSON serialized
            result[new_key] = json.dumps(value)
        else:
            result[new_key] = value
    
    return result

# Test
flattened = flatten_json(data)
print(flattened)
```

---

### Task 2: Deduplicate Events by Rules

**Problem:**
```python
# Input: Stream of events with potential duplicates
events = [
    {"event_id": "a1", "user_id": 1, "action": "click", "timestamp": 1000},
    {"event_id": "a2", "user_id": 1, "action": "click", "timestamp": 1001},  # Duplicate (same user, action, within 5s)
    {"event_id": "a3", "user_id": 1, "action": "purchase", "timestamp": 1002},
    {"event_id": "a1", "user_id": 1, "action": "click", "timestamp": 1003},  # Duplicate (same event_id)
    {"event_id": "a4", "user_id": 2, "action": "click", "timestamp": 1000},
]

# Rules:
# 1. Same event_id = duplicate
# 2. Same (user_id, action) within 5 seconds = duplicate
# Keep first occurrence
```

**Solution:**
```python
from collections import defaultdict
from typing import List, Dict

def deduplicate_events(
    events: List[Dict],
    window_seconds: int = 5
) -> List[Dict]:
    """Deduplicate events by rules"""
    
    seen_event_ids = set()
    user_action_last_time = {}  # (user_id, action) -> last_timestamp
    result = []
    
    for event in events:
        event_id = event["event_id"]
        user_id = event["user_id"]
        action = event["action"]
        timestamp = event["timestamp"]
        
        # Rule 1: Check event_id
        if event_id in seen_event_ids:
            continue
        
        # Rule 2: Check (user_id, action) within window
        key = (user_id, action)
        if key in user_action_last_time:
            if timestamp - user_action_last_time[key] <= window_seconds:
                continue
        
        # Not duplicate - keep it
        seen_event_ids.add(event_id)
        user_action_last_time[key] = timestamp
        result.append(event)
    
    return result

# Test
unique_events = deduplicate_events(events)
print(f"Original: {len(events)}, Unique: {len(unique_events)}")
# Output: Original: 5, Unique: 3
```

---

### Task 3: Implement Sliding Window Aggregation

**Problem:**
```python
# Calculate 7-day rolling average of daily revenue
daily_revenue = [
    {"date": "2024-01-01", "revenue": 100},
    {"date": "2024-01-02", "revenue": 150},
    {"date": "2024-01-03", "revenue": 200},
    # ... more days
    {"date": "2024-01-10", "revenue": 180},
]

# Expected: Each day has avg of last 7 days (or fewer if < 7 days data)
```

**Solution:**
```python
from collections import deque
from typing import List, Dict
from datetime import datetime, timedelta

def rolling_average(
    data: List[Dict],
    window_days: int = 7
) -> List[Dict]:
    """Calculate rolling average revenue"""
    
    # Sort by date
    sorted_data = sorted(data, key=lambda x: x["date"])
    
    window = deque()
    window_sum = 0
    result = []
    
    for record in sorted_data:
        current_date = datetime.strptime(record["date"], "%Y-%m-%d")
        revenue = record["revenue"]
        
        # Add current day
        window.append((current_date, revenue))
        window_sum += revenue
        
        # Remove days outside window
        while window and (current_date - window[0][0]).days >= window_days:
            _, old_revenue = window.popleft()
            window_sum -= old_revenue
        
        # Calculate average
        avg_revenue = window_sum / len(window)
        
        result.append({
            "date": record["date"],
            "revenue": revenue,
            "rolling_avg_7d": round(avg_revenue, 2),
            "days_in_window": len(window)
        })
    
    return result
```

---

### Task 4: Parse Log Files

**Problem:**
```python
# Parse Apache access logs
log_lines = [
    '192.168.1.1 - - [10/Jan/2024:10:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234',
    '192.168.1.2 - - [10/Jan/2024:10:00:01 +0000] "POST /api/orders HTTP/1.1" 201 567',
    '192.168.1.1 - - [10/Jan/2024:10:00:02 +0000] "GET /api/users/123 HTTP/1.1" 404 89',
]

# Extract: ip, timestamp, method, path, status, bytes
```

**Solution:**
```python
import re
from typing import List, Dict, Optional
from datetime import datetime

def parse_access_log(log_line: str) -> Optional[Dict]:
    """Parse Apache access log line"""
    
    pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) [^"]*" (\d+) (\d+)'
    
    match = re.match(pattern, log_line)
    if not match:
        return None
    
    ip, timestamp_str, method, path, status, bytes_sent = match.groups()
    
    # Parse timestamp
    timestamp = datetime.strptime(
        timestamp_str, 
        "%d/%b/%Y:%H:%M:%S %z"
    )
    
    return {
        "ip": ip,
        "timestamp": timestamp.isoformat(),
        "method": method,
        "path": path,
        "status": int(status),
        "bytes": int(bytes_sent)
    }

def process_logs(log_lines: List[str]) -> List[Dict]:
    """Process multiple log lines"""
    results = []
    errors = 0
    
    for line in log_lines:
        parsed = parse_access_log(line)
        if parsed:
            results.append(parsed)
        else:
            errors += 1
    
    print(f"Parsed: {len(results)}, Errors: {errors}")
    return results

# Usage
parsed_logs = process_logs(log_lines)
```

---

## 🗄️ SQL Coding Challenges

### Task 5: Find Running Total with Reset

**Problem:**
```sql
-- Calculate running total of orders per customer
-- Reset when a refund happens

-- Input table: orders
-- | order_id | customer_id | amount | order_type  | order_date |
-- |----------|-------------|--------|-------------|------------|
-- | 1        | 100         | 50     | purchase    | 2024-01-01 |
-- | 2        | 100         | 30     | purchase    | 2024-01-02 |
-- | 3        | 100         | -80    | refund      | 2024-01-03 |
-- | 4        | 100         | 100    | purchase    | 2024-01-04 |

-- Expected: Running total resets after refund
```

**Solution:**
```sql
WITH order_groups AS (
    -- Create group ID that increments on each refund
    SELECT 
        *,
        SUM(CASE WHEN order_type = 'refund' THEN 1 ELSE 0 END) 
            OVER (PARTITION BY customer_id ORDER BY order_date) AS refund_group
    FROM orders
),
running_totals AS (
    SELECT 
        order_id,
        customer_id,
        amount,
        order_type,
        order_date,
        refund_group,
        SUM(amount) OVER (
            PARTITION BY customer_id, refund_group 
            ORDER BY order_date
        ) AS running_total
    FROM order_groups
)
SELECT * FROM running_totals
ORDER BY customer_id, order_date;
```

---

### Task 6: Sessionization

**Problem:**
```sql
-- Group events into sessions
-- New session if gap > 30 minutes

-- Input: events table
-- | user_id | event_time          | event_type |
-- |---------|---------------------|------------|
-- | 1       | 2024-01-01 10:00:00 | page_view  |
-- | 1       | 2024-01-01 10:05:00 | click      |
-- | 1       | 2024-01-01 11:00:00 | page_view  | <- New session
```

**Solution:**
```sql
WITH time_gaps AS (
    SELECT 
        user_id,
        event_time,
        event_type,
        LAG(event_time) OVER (
            PARTITION BY user_id 
            ORDER BY event_time
        ) AS prev_event_time,
        TIMESTAMPDIFF(
            MINUTE,
            LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time),
            event_time
        ) AS gap_minutes
    FROM events
),
session_starts AS (
    SELECT 
        *,
        CASE 
            WHEN gap_minutes IS NULL OR gap_minutes > 30 THEN 1 
            ELSE 0 
        END AS is_session_start
    FROM time_gaps
),
sessions AS (
    SELECT 
        *,
        SUM(is_session_start) OVER (
            PARTITION BY user_id 
            ORDER BY event_time
        ) AS session_id
    FROM session_starts
)
SELECT 
    user_id,
    event_time,
    event_type,
    session_id,
    CONCAT(user_id, '_', session_id) AS session_key
FROM sessions
ORDER BY user_id, event_time;
```

---

### Task 7: SCD Type 2 Query

**Problem:**
```sql
-- Given SCD Type 2 table, find customer attributes at specific date

-- customers_history table:
-- | customer_id | name  | tier    | valid_from | valid_to   |
-- |-------------|-------|---------|------------|------------|
-- | 1           | John  | bronze  | 2023-01-01 | 2023-06-30 |
-- | 1           | John  | silver  | 2023-07-01 | 2024-01-01 |
-- | 1           | John  | gold    | 2024-01-02 | 9999-12-31 |

-- Find: What tier was customer 1 on 2023-08-15?
```

**Solution:**
```sql
-- Point-in-time lookup
SELECT 
    customer_id,
    name,
    tier,
    valid_from,
    valid_to
FROM customers_history
WHERE customer_id = 1
  AND '2023-08-15' >= valid_from
  AND '2023-08-15' < valid_to;
-- Result: silver

-- Join orders with customer tier at time of order
SELECT 
    o.order_id,
    o.customer_id,
    o.order_date,
    o.amount,
    c.tier AS customer_tier_at_order
FROM orders o
LEFT JOIN customers_history c 
    ON o.customer_id = c.customer_id
    AND o.order_date >= c.valid_from 
    AND o.order_date < c.valid_to;
```

---

### Task 8: Gap and Island Problem

**Problem:**
```sql
-- Find user activity streaks (consecutive days)

-- logins table:
-- | user_id | login_date |
-- |---------|------------|
-- | 1       | 2024-01-01 |
-- | 1       | 2024-01-02 |
-- | 1       | 2024-01-03 |
-- | 1       | 2024-01-05 | <- gap
-- | 1       | 2024-01-06 |
```

**Solution:**
```sql
WITH numbered AS (
    SELECT 
        user_id,
        login_date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn
    FROM logins
),
grouped AS (
    SELECT 
        user_id,
        login_date,
        rn,
        DATE_SUB(login_date, INTERVAL rn DAY) AS grp
    FROM numbered
)
SELECT 
    user_id,
    MIN(login_date) AS streak_start,
    MAX(login_date) AS streak_end,
    COUNT(*) AS streak_length
FROM grouped
GROUP BY user_id, grp
ORDER BY streak_length DESC;
```

---

## 🔧 Data Pipeline Tasks

### Task 9: Implement Incremental Load Logic

**Problem:**
```python
# Implement incremental load from source to destination
# Track high water mark, handle restarts
```

**Solution:**
```python
from datetime import datetime
from typing import Optional
import json

class IncrementalLoader:
    """Incremental data loader with checkpointing"""
    
    def __init__(
        self, 
        source_db, 
        target_db,
        checkpoint_path: str = "checkpoint.json"
    ):
        self.source = source_db
        self.target = target_db
        self.checkpoint_path = checkpoint_path
    
    def get_high_water_mark(self) -> Optional[datetime]:
        """Load last checkpoint"""
        try:
            with open(self.checkpoint_path, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data['high_water_mark'])
        except FileNotFoundError:
            return None
    
    def save_checkpoint(self, hwm: datetime):
        """Save checkpoint"""
        with open(self.checkpoint_path, 'w') as f:
            json.dump({'high_water_mark': hwm.isoformat()}, f)
    
    def load_incremental(self, table: str, timestamp_col: str):
        """Load data incrementally"""
        hwm = self.get_high_water_mark()
        
        # Build query
        if hwm:
            query = f"""
                SELECT * FROM {table}
                WHERE {timestamp_col} > '{hwm}'
                ORDER BY {timestamp_col}
            """
        else:
            query = f"SELECT * FROM {table} ORDER BY {timestamp_col}"
        
        # Extract
        data = self.source.execute(query)
        
        if not data:
            print("No new data")
            return 0
        
        # Load
        rows_loaded = self.target.bulk_insert(table, data)
        
        # Update checkpoint
        max_timestamp = max(row[timestamp_col] for row in data)
        self.save_checkpoint(max_timestamp)
        
        print(f"Loaded {rows_loaded} rows, new HWM: {max_timestamp}")
        return rows_loaded
```

---

### Task 10: Implement Retry with Exponential Backoff

**Problem:**
```python
# API calls fail sometimes, implement robust retry logic
```

**Solution:**
```python
import time
import random
from functools import wraps
from typing import Type, Tuple

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retry with exponential backoff"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        print(f"Max retries ({max_retries}) exceeded")
                        raise
                    
                    # Calculate delay
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Add jitter
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
def fetch_from_api(endpoint: str):
    """Fetch data from unreliable API"""
    response = requests.get(endpoint, timeout=30)
    response.raise_for_status()
    return response.json()
```

---

## 📁 File Processing

### Task 11: Process Large CSV in Chunks

**Problem:**
```python
# Process 10GB CSV file without loading all into memory
# Apply transformations and write to Parquet
```

**Solution:**
```python
import pandas as pd
from pathlib import Path

def process_large_csv(
    input_path: str,
    output_path: str,
    chunk_size: int = 100_000,
    transformation_func=None
):
    """Process large CSV in chunks to Parquet"""
    
    output_dir = Path(output_path)
    output_dir.mkdir(exist_ok=True)
    
    total_rows = 0
    chunk_num = 0
    
    for chunk in pd.read_csv(input_path, chunksize=chunk_size):
        # Apply transformations
        if transformation_func:
            chunk = transformation_func(chunk)
        
        # Write chunk as parquet partition
        chunk_path = output_dir / f"part-{chunk_num:05d}.parquet"
        chunk.to_parquet(chunk_path, index=False)
        
        total_rows += len(chunk)
        chunk_num += 1
        
        print(f"Processed chunk {chunk_num}: {len(chunk)} rows")
    
    print(f"Total: {total_rows} rows in {chunk_num} files")
    return total_rows

# Transformation function
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform data"""
    # Remove nulls
    df = df.dropna(subset=['id', 'date'])
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'])
    
    # Add columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    return df

# Usage
process_large_csv(
    "input.csv",
    "output_parquet/",
    chunk_size=100_000,
    transformation_func=transform
)
```

---

### Task 12: Merge Multiple Files with Schema Validation

**Problem:**
```python
# Merge CSV files from multiple sources
# Validate schemas match before merging
```

**Solution:**
```python
import pandas as pd
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class SchemaValidationResult:
    valid: bool
    errors: List[str]

def validate_schema(
    df: pd.DataFrame,
    expected_columns: List[str],
    expected_dtypes: Optional[dict] = None
) -> SchemaValidationResult:
    """Validate DataFrame schema"""
    errors = []
    
    # Check columns exist
    missing = set(expected_columns) - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {missing}")
    
    extra = set(df.columns) - set(expected_columns)
    if extra:
        errors.append(f"Extra columns: {extra}")
    
    # Check dtypes
    if expected_dtypes:
        for col, expected in expected_dtypes.items():
            if col in df.columns:
                actual = str(df[col].dtype)
                if actual != expected:
                    errors.append(f"Column {col}: expected {expected}, got {actual}")
    
    return SchemaValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )

def merge_files(
    file_pattern: str,
    expected_columns: List[str],
    output_path: str
) -> int:
    """Merge files with schema validation"""
    
    files = list(Path().glob(file_pattern))
    print(f"Found {len(files)} files")
    
    merged_dfs = []
    failed_files = []
    
    for file in files:
        try:
            df = pd.read_csv(file)
            
            # Validate schema
            result = validate_schema(df, expected_columns)
            if not result.valid:
                print(f"Schema error in {file}: {result.errors}")
                failed_files.append(file)
                continue
            
            # Select only expected columns in order
            df = df[expected_columns]
            merged_dfs.append(df)
            
        except Exception as e:
            print(f"Error processing {file}: {e}")
            failed_files.append(file)
    
    if not merged_dfs:
        raise ValueError("No valid files to merge")
    
    # Merge and write
    merged = pd.concat(merged_dfs, ignore_index=True)
    merged.to_parquet(output_path, index=False)
    
    print(f"Merged {len(merged_dfs)} files, {len(merged)} rows")
    print(f"Failed: {len(failed_files)} files")
    
    return len(merged)
```

---

## 🌐 API Integration

### Task 13: Paginated API Fetcher

**Problem:**
```python
# Fetch all data from paginated REST API
# Handle rate limits and errors
```

**Solution:**
```python
import requests
import time
from typing import Generator, Dict, Any

class PaginatedAPIFetcher:
    """Fetch all data from paginated API"""
    
    def __init__(
        self,
        base_url: str,
        page_size: int = 100,
        rate_limit_delay: float = 0.5
    ):
        self.base_url = base_url
        self.page_size = page_size
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
    
    def fetch_page(self, page: int) -> Dict[str, Any]:
        """Fetch single page"""
        params = {
            "page": page,
            "limit": self.page_size
        }
        
        response = self.session.get(
            self.base_url,
            params=params,
            timeout=30
        )
        
        # Handle rate limit
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited, sleeping {retry_after}s")
            time.sleep(retry_after)
            return self.fetch_page(page)
        
        response.raise_for_status()
        return response.json()
    
    def fetch_all(self) -> Generator[Dict, None, None]:
        """Fetch all pages as generator"""
        page = 1
        total_fetched = 0
        
        while True:
            result = self.fetch_page(page)
            data = result.get("data", [])
            
            if not data:
                break
            
            for item in data:
                yield item
                total_fetched += 1
            
            # Check if more pages
            has_next = result.get("has_next", len(data) == self.page_size)
            if not has_next:
                break
            
            page += 1
            time.sleep(self.rate_limit_delay)
        
        print(f"Fetched {total_fetched} items from {page} pages")

# Usage
fetcher = PaginatedAPIFetcher("https://api.example.com/orders")
for order in fetcher.fetch_all():
    process_order(order)
```

---

## 🧪 Testing & Validation

### Task 14: Data Validation Framework

**Problem:**
```python
# Create simple data validation framework
# Check nulls, ranges, uniqueness
```

**Solution:**
```python
from dataclasses import dataclass
from typing import List, Callable, Any
import pandas as pd

@dataclass
class ValidationRule:
    name: str
    check_func: Callable[[pd.DataFrame], bool]
    severity: str = "error"  # error, warning

@dataclass
class ValidationResult:
    rule_name: str
    passed: bool
    details: str

class DataValidator:
    """Simple data validation framework"""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule):
        self.rules.append(rule)
    
    def add_not_null(self, column: str):
        """Add not null check"""
        self.rules.append(ValidationRule(
            name=f"not_null_{column}",
            check_func=lambda df, col=column: df[col].notna().all(),
            severity="error"
        ))
    
    def add_unique(self, column: str):
        """Add uniqueness check"""
        self.rules.append(ValidationRule(
            name=f"unique_{column}",
            check_func=lambda df, col=column: df[col].is_unique,
            severity="error"
        ))
    
    def add_range(self, column: str, min_val=None, max_val=None):
        """Add range check"""
        def check(df, col=column, mn=min_val, mx=max_val):
            if mn is not None and (df[col] < mn).any():
                return False
            if mx is not None and (df[col] > mx).any():
                return False
            return True
        
        self.rules.append(ValidationRule(
            name=f"range_{column}_{min_val}_{max_val}",
            check_func=check,
            severity="error"
        ))
    
    def validate(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Run all validations"""
        results = []
        
        for rule in self.rules:
            try:
                passed = rule.check_func(df)
                results.append(ValidationResult(
                    rule_name=rule.name,
                    passed=passed,
                    details="OK" if passed else f"FAILED ({rule.severity})"
                ))
            except Exception as e:
                results.append(ValidationResult(
                    rule_name=rule.name,
                    passed=False,
                    details=f"ERROR: {str(e)}"
                ))
        
        return results

# Usage
validator = DataValidator()
validator.add_not_null("order_id")
validator.add_not_null("customer_id")
validator.add_unique("order_id")
validator.add_range("amount", min_val=0)

results = validator.validate(df)
for r in results:
    status = "✅" if r.passed else "❌"
    print(f"{status} {r.rule_name}: {r.details}")
```

---

## 🏃 Thử Kêu Gọi Live Coding Khét Lẹt

### Task 15: Merge Overlapping Event Sessions

**Problem:**
Trong DE Live Coding, câu hỏi kinh điển nhất là "Gộp phiên User": User click lắt nhắt nhưng nới lỏng cửa sổ. Đầu vào là list các khoảng thời gian Online `[start, end]`. Yêu cầu gộp các dải thời gian bị dẫm đạp (overlap) lên nhau, trả về chuỗi phiên độc lập.

```python
# Input:
sessions = [[1, 3], [2, 6], [8, 10], [15, 18], [9, 11]]
# Output:
# [[1, 6], [8, 11], [15, 18]]
```

**Solution:**
```python
def merge_sessions(intervals: list[list[int]]) -> list[list[int]]:
    """O(N log N) time, O(N) space"""
    if not intervals:
        return []
        
    # Bước 1: Sort by start_time
    intervals.sort(key=lambda x: x[0])
    
    merged = [intervals[0]]
    
    for current_start, current_end in intervals[1:]:
        last_interval = merged[-1]
        
        # Nếu start của hiện tại <= end của thằng trước -> Bị đè
        if current_start <= last_interval[1]:
            # Extend cái end dài nhất có thể
            last_interval[1] = max(last_interval[1], current_end)
        else:
            # Rời rạc -> Nạp nguyên bản
            merged.append([current_start, current_end])
            
    return merged
```

---

### Task 16: Top K Heavy Hitters in Stream (Trending Hashtags)

**Problem:**
Một mảng vô tận các từ khoá (hashtags) rót vô rào rào. Bắt bạn in ra 3 hashtags xuất hiện nhiều nhất (Top K). Yêu cầu: Không được sort `O(N log N)` bằng built-in Của Python vì N là vô cực. Bạn chỉ được dùng mâm Cổ `O(N log K)`.

**Solution:**
Sử dụng Hash Map đếm số lượng + Min Heap chặn cửa.

```python
from collections import Counter
import heapq

def top_k_hashtags(stream: list[str], k: int) -> list[str]:
    """Tìm Heavy Hitters O(N log K)"""
    counts = Counter(stream)
    
    # Min Heap duy trì giới hạn K elements
    min_heap = []
    
    for phrase, freq in counts.items():
        # Nhét tuple (freq, phrase) vào Heap
        heapq.heappush(min_heap, (freq, phrase))
        
        # Nếu mâm chật >> Bốc dẹp đứa nghèo khổ nhất (Tần suất nhỏ nhất)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
            
    # Kết quả văng ra trên Min Heap đang bị xáo trộn, phải lộn ngược
    result = [item[1] for item in sorted(min_heap, reverse=True)]
    return result
```

---

### Task 17: Flatten Organizational Hierarchy (Manager-Employee DAG)

**Problem:**
DE hay phải xử lý bảng Master Data, trong đó cấu trúc nhân sự lồng ghép Parent-Child. Hãy bóc ngang bảng Dọc để in ra chuỗi phả hệ theo định dạng `Boss -> Manager -> Staff`. Đề cho Format: `{"EmpCode": "ManagerCode"}`. CEO không có Manager (None).

```python
emp_mgr = {
    "C": "B",
    "D": "B",
    "B": "A",
    "A": None, # A là CEO
    "E": "D"
}
# Yêu cầu xuất cấu trúc từ Top-Down dạng in mảng string Path.
```

**Solution (DFS Traversal):**
```python
from collections import defaultdict

def build_hierarchy_paths(relations: dict) -> list[str]:
    # Xây rễ đồ thị (Parent trỏ tới list các Children)
    tree = defaultdict(list)
    ceo = None
    
    for emp, mgr in relations.items():
        if mgr is None:
            ceo = emp
        else:
            tree[mgr].append(emp)
            
    paths = []
    
    # DFS thọc sâu
    def dfs(node, current_path):
        current_path.append(node)
        
        # Nếu node không có đệ thì là mút cùng, chốt đường đi
        if node not in tree or not tree[node]:
            paths.append(" -> ".join(current_path))
        else:
            for child in tree[node]:
                dfs(child, current_path.copy()) # copy list để các nhánh không lấn nhau
                
    dfs(ceo, [])
    return paths

# Output: ['A -> B -> C', 'A -> B -> D -> E']
```

---

### Task 18: Stream Alignment Within Time Window (AsOf Join)

**Problem:**
Web server nhả Log Click. Payment Server nhả Log Trả Tiền. Cả 2 có Timestamp có thể Lệch nhau xíu xiu do độ trễ Mạng (vd 2 giây). Bạn được cấp 2 Array chứa các dòng theo thứ tự tăng dần Time. Viết hàm Two-Pointers để gộp dính "Click" và "Payment" nào xảy ra cùng 1 User trong vòng 3 Giây Tối Đa.

**Solution:**
```python
def align_streams(clicks: list[dict], payments: list[dict], window_ms=3000):
    """
    Two-Pointer ngầm trong Real-time streaming.
    Time O(N + M). 
    """
    aligned = []
    i, j = 0, 0
    
    while i < len(clicks) and j < len(payments):
        c = clicks[i]
        p = payments[j]
        
        # Nếu khác User id thì đuổi mũi nhọn (Sort by time)
        if c["user_id"] < p["user_id"]: # Giả lập user data đang xáo trộn by time (Thường đề bắt Key khớp)
            pass
            
        time_diff = abs(c["time"] - p["time"])
        
        # Lệch xíu -> Gom bắt 
        if c["user_id"] == p["user_id"] and time_diff <= window_ms:
            aligned.append({
                "user_id": c["user_id"],
                "click_id": c["id"],
                "payment_id": p["id"],
                "latency_ms": time_diff
            })
            i += 1
            j += 1
        else:
            # Thằng nào mốc thời gian cũ hơn thì Kéo nó đi trước bù mốc tương lai
            if c["time"] < p["time"]:
                i += 1
            else:
                j += 1
                
    return aligned
```

---

### Task 19: Anomaly Detection with Moving Z-Score

**Problem:**
Detect Dữ liệu chọc sàn: Stream đổ rầm rập Cột `Transaction_Amount`. Live Code phát hiện những Phi vụ quẹt thẻ có giá trị Lệch xa X3 lần Độ lệch chuẩn (3 Standard Deviations) trong cửa sổ 5 Lần quẹt gần nhất của Khách (Moving Z-Score). 

**Solution:**
```python
import math
from collections import deque, defaultdict

class AnomalyDetector:
    def __init__(self, window_size=5, threshold_z=3.0):
        self.window_size = window_size
        self.threshold = threshold_z
        self.user_history = defaultdict(deque)
        
    def _calculate_mean_std(self, data: list):
        if len(data) < 2:
            return sum(data)/len(data), 0
            
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1) # Mẫu n-1
        return mean, math.sqrt(variance)

    def process_event(self, user_id: str, amount: float) -> bool:
        """ Trả về True nếu Phi vụ này là Gian Lận """
        history = self.user_history[user_id]
        
        # Nếu chưa đủ data nòng cốt, nhắm mắt cho qua (Trust base)
        if len(history) < self.window_size:
            history.append(amount)
            return False
            
        mean, std_dev = self._calculate_mean_std(list(history))
        
        # Nếu std rỗng (dải số toàn đều tăm tắp bằng nhau) thì chặn mẫu Zero Division
        if std_dev == 0:
            is_anomaly = amount != mean
        else:
            z_score = abs(amount - mean) / std_dev
            is_anomaly = z_score > self.threshold
            
        # Cập nhật Sliding Window Window  
        history.popleft()
        history.append(amount)
        
        return is_anomaly

# Live Debug:
# detector = AnomalyDetector(window_size=3, threshold_z=2.0)
# detector.process_event("A", 10.0)
# detector.process_event("A", 12.0)
# detector.process_event("A", 11.0)
# print(detector.process_event("A", 999.0)) # True (Ra đòn Cảnh sát múc!)
```

---

## 📝 Quick Reference

### Common Patterns Checklist

```
Data Processing:
[ ] Flatten nested JSON
[ ] Deduplicate with rules
[ ] Sliding window aggregation
[ ] Parse log files

Live Coding DE (MỚI!):
[ ] Merge Overlapping Sessions (Mảng gộp)
[ ] K Heavy Hitters (Min-Heap / Hash)
[ ] Phân rã DAG Đồ Thị Cây (DFS/BFS)
[ ] Cân chỉnh dải Time Window 2 Mảng
[ ] Math & Stat (Z-Score detection)

SQL:
[ ] Window functions (running total, lag/lead)
[ ] Sessionization
[ ] SCD Type 2 queries
[ ] Gap and Island patterns

Pipeline:
[ ] Incremental load
[ ] Retry with backoff
[ ] Checkpoint/resume

Files:
[ ] Chunked processing
[ ] Schema validation
[ ] Multi-file merge

API:
[ ] Pagination handling
[ ] Rate limit handling
```

---

## 🔗 Liên Kết

- [SQL Deep Dive](02_SQL_Deep_Dive.md)
- [System Design](03_System_Design.md)
- [Behavioral Questions](04_Behavioral_Questions.md)
- [Python for DE](../fundamentals/13_Python_Data_Engineering.md)

---

*Cập nhật: February 2026*
