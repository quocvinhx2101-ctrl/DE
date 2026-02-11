# 🔰 Project 01: End-to-End Data Pipeline

> Build một data pipeline hoàn chỉnh từ ingestion đến visualization

---

## 📋 Project Overview

**Difficulty:** Beginner → Intermediate
**Time Estimate:** 2-3 weeks
**Skills Learned:** ETL, Python, SQL, Docker, Orchestration

### Mục Tiêu

Build một pipeline thu thập dữ liệu thời tiết, lưu vào database, transform và visualize.

```mermaid
graph LR
    A["\ud83c\udf26\ufe0f Weather API"] -->|requests| B["\ud83d\udc0d Python Extractor"]
    B -->|INSERT| C[("\ud83d\uddc4\ufe0f PostgreSQL\nRaw DB")]
    C --> D["\u2728 dbt\nTransform"]
    D --> E[("\ud83d\uddc4\ufe0f PostgreSQL\nAnalytics")]
    E --> F["\ud83d\udcca Grafana\nDashboard"]
    
    G["\u23f0 Airflow"] -.->|hourly schedule| B
    G -.->|trigger| D
    
    style A fill:#4ecdc4,color:#000
    style C fill:#336791,color:#fff
    style E fill:#336791,color:#fff
    style F fill:#f46800,color:#fff
    style G fill:#017cee,color:#fff
```

> **Infrastructure:** Toàn bộ chạy trên Docker Compose

---

## 🛠️ Tech Stack

- **Extract:** Python + requests
- **Load:** PostgreSQL
- **Transform:** dbt
- **Orchestrate:** Airflow
- **Visualize:** Grafana
- **Infrastructure:** Docker Compose

---

## 📂 Project Structure

```
weather-pipeline/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── airflow/
│   ├── dags/
│   │   └── weather_pipeline.py
│   └── plugins/
│
├── extractor/
│   ├── main.py
│   ├── weather_api.py
│   └── requirements.txt
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       │   └── stg_weather.sql
│       └── marts/
│           └── daily_weather_summary.sql
│
├── sql/
│   └── init.sql
│
└── grafana/
    └── dashboards/
        └── weather.json
```

---

## 🚀 Step-by-Step Implementation

### Step 1: Setup Infrastructure

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: weather
      POSTGRES_PASSWORD: weather123
      POSTGRES_DB: weather_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  airflow:
    image: apache/airflow:2.8.0
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://weather:weather123@postgres/weather_db
    volumes:
      - ./airflow/dags:/opt/airflow/dags
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - postgres

volumes:
  postgres_data:
  grafana_data:
```

### Step 2: Extract - Weather API

**extractor/weather_api.py:**
```python
import requests
from datetime import datetime
import os

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city: str) -> dict:
        """Get current weather for a city."""
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return {
            'city': city,
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'weather_condition': data['weather'][0]['main'],
            'collected_at': datetime.utcnow().isoformat()
        }
```

### Step 3: Load - Database

**sql/init.sql:**
```sql
CREATE TABLE IF NOT EXISTS raw_weather (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    temperature DECIMAL(5,2),
    humidity INTEGER,
    pressure INTEGER,
    wind_speed DECIMAL(5,2),
    weather_condition VARCHAR(50),
    collected_at TIMESTAMP NOT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_weather_city_date 
ON raw_weather(city, collected_at);
```

### Step 4: Transform - dbt Models

**dbt/models/staging/stg_weather.sql:**
```sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_weather') }}
),

cleaned AS (
    SELECT
        id,
        LOWER(TRIM(city)) AS city,
        temperature,
        humidity,
        pressure,
        wind_speed,
        weather_condition,
        collected_at,
        DATE(collected_at) AS collected_date,
        EXTRACT(HOUR FROM collected_at) AS collected_hour
    FROM source
    WHERE temperature IS NOT NULL
)

SELECT * FROM cleaned
```

**dbt/models/marts/daily_weather_summary.sql:**
```sql
WITH hourly_data AS (
    SELECT * FROM {{ ref('stg_weather') }}
),

daily_agg AS (
    SELECT
        city,
        collected_date,
        AVG(temperature) AS avg_temperature,
        MIN(temperature) AS min_temperature,
        MAX(temperature) AS max_temperature,
        AVG(humidity) AS avg_humidity,
        AVG(wind_speed) AS avg_wind_speed,
        MODE() WITHIN GROUP (ORDER BY weather_condition) AS most_common_condition,
        COUNT(*) AS readings_count
    FROM hourly_data
    GROUP BY city, collected_date
)

SELECT * FROM daily_agg
```

### Step 5: Orchestrate - Airflow DAG

**airflow/dags/weather_pipeline.py:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/extractor')

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'weather_pipeline',
    default_args=default_args,
    description='Collect weather data hourly',
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

def extract_and_load():
    from weather_api import WeatherAPI
    from db_loader import load_to_postgres
    
    api = WeatherAPI()
    cities = ['London', 'Paris', 'Tokyo', 'New York', 'Sydney']
    
    for city in cities:
        data = api.get_weather(city)
        load_to_postgres(data)

extract_task = PythonOperator(
    task_id='extract_weather',
    python_callable=extract_and_load,
    dag=dag
)

transform_task = BashOperator(
    task_id='run_dbt',
    bash_command='cd /opt/airflow/dbt && dbt run',
    dag=dag
)

extract_task >> transform_task
```

---

## ✅ Completion Checklist

### Phase 1: Infrastructure
- [ ] Docker Compose working
- [ ] PostgreSQL accessible
- [ ] Airflow UI accessible
- [ ] Grafana accessible

### Phase 2: Extract & Load
- [ ] Weather API key obtained
- [ ] Python extractor working
- [ ] Data loading to PostgreSQL
- [ ] Hourly schedule running

### Phase 3: Transform
- [ ] dbt project setup
- [ ] Staging models created
- [ ] Mart models created
- [ ] Tests passing

### Phase 4: Visualize
- [ ] Grafana connected to PostgreSQL
- [ ] Dashboard created
- [ ] Charts showing data

### Phase 5: Polish
- [ ] Error handling added
- [ ] Logging implemented
- [ ] Documentation complete
- [ ] README updated

---

## 🎯 Learning Outcomes

**After completing:**
- Understand full ETL lifecycle
- Experience with Python for data engineering
- PostgreSQL and SQL fundamentals
- dbt basics
- Airflow DAG creation
- Docker containerization
- Dashboard creation

---

## 🚀 Extensions

**Level Up:**
1. Add more cities dynamically
2. Implement incremental loading
3. Add data quality tests
4. Set up alerting for pipeline failures
5. Deploy to cloud (AWS/GCP)

---

## 🔗 Liên Kết

- [Next Project: Real-time Dashboard](02_Realtime_Dashboard.md)
- [Tools Reference](../tools/)
- [Fundamentals](../fundamentals/)

---

## 📦 Verified Resources Cho Project Này

**Datasets thay thế/bổ sung:**
- [NYC TLC Trip Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) — Parquet, GBs. Dùng thay Weather API nếu muốn data lớn hơn.
- [OpenWeatherMap API](https://openweathermap.org/api) — Free tier 1000 calls/day (dùng trong project này).

**Docker Images (verified, dùng trong docker-compose.yml):**
- `postgres:15` — [Docker Hub](https://hub.docker.com/_/postgres)
- `apache/airflow:2.8.0` — [Docker Hub](https://hub.docker.com/r/apache/airflow)
- `grafana/grafana:latest` — [Docker Hub](https://hub.docker.com/r/grafana/grafana)

**Tham khảo thêm:**
- [DataTalksClub/data-engineering-zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) — Project tương tự với Docker + Airflow + dbt
- [dbt-labs/jaffle-shop](https://github.com/dbt-labs/jaffle-shop) — Canonical dbt demo project

---

*Cập nhật: February 2026*
