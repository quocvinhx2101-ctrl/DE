# Python for Data Engineering - Complete Guide

## Core Python Skills, Libraries, và Best Practices cho Data Engineers

---

## PHẦN 1: PYTHON FUNDAMENTALS FOR DE

### 1.1 Why Python for Data Engineering?

Python là ngôn ngữ primary cho Data Engineering vì:
- **Rich ecosystem** - pandas, PySpark, Airflow, dbt
- **Easy to learn** - Clear syntax, rapid development
- **Integration** - Connects to everything
- **Community** - Extensive resources and support
- **Versatility** - ETL, APIs, ML, automation

### 1.2 Essential Python Concepts

```python
# 1. DATA STRUCTURES

# Lists - ordered, mutable
data = [1, 2, 3, 4, 5]
data.append(6)
filtered = [x for x in data if x > 3]

# Dictionaries - key-value pairs
record = {
    'id': 1,
    'name': 'Alice',
    'age': 30
}
record['email'] = 'alice@example.com'

# Sets - unique values
unique_ids = {1, 2, 3, 3, 4}  # {1, 2, 3, 4}

# Tuples - immutable
coordinates = (10.5, 20.3)

# Named tuples - readable tuples
from collections import namedtuple
User = namedtuple('User', ['id', 'name', 'email'])
user = User(1, 'Alice', 'alice@example.com')


# 2. COMPREHENSIONS

# List comprehension
squares = [x**2 for x in range(10)]

# Dict comprehension
word_lengths = {word: len(word) for word in ['apple', 'banana']}

# Set comprehension
unique_chars = {char for word in words for char in word}

# Generator expression (memory efficient)
sum_squares = sum(x**2 for x in range(1000000))


# 3. FUNCTIONS

def transform_record(record: dict, 
                     fields: list = None,
                     uppercase: bool = False) -> dict:
    """
    Transform a data record.
    
    Args:
        record: Input record
        fields: Fields to include (default: all)
        uppercase: Whether to uppercase string values
    
    Returns:
        Transformed record
    """
    if fields:
        record = {k: v for k, v in record.items() if k in fields}
    
    if uppercase:
        record = {
            k: v.upper() if isinstance(v, str) else v 
            for k, v in record.items()
        }
    
    return record


# Lambda functions
clean_string = lambda s: s.strip().lower()
get_value = lambda d, k: d.get(k, 'N/A')


# 4. GENERATORS (Memory efficient for large data)

def read_large_file(filepath):
    """Read file line by line, memory efficient"""
    with open(filepath, 'r') as f:
        for line in f:
            yield line.strip()

def batch_iterator(iterable, batch_size):
    """Yield batches from iterable"""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


# 5. CONTEXT MANAGERS

from contextlib import contextmanager

@contextmanager
def database_connection(connection_string):
    """Context manager for database connections"""
    conn = create_connection(connection_string)
    try:
        yield conn
    finally:
        conn.close()

# Usage
with database_connection('postgres://...') as conn:
    result = conn.execute('SELECT * FROM users')


# 6. DECORATORS

import functools
import time

def timer(func):
    """Decorator to measure execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

def retry(max_attempts=3, delay=1):
    """Decorator for retry logic"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@timer
@retry(max_attempts=3)
def fetch_data(url):
    # Fetch data from API
    pass
```

---

## PHẦN 2: PANDAS ESSENTIALS

### 2.1 DataFrame Operations

```python
import pandas as pd
import numpy as np

# READING DATA

# CSV
df = pd.read_csv('data.csv', 
                 dtype={'id': int, 'name': str},
                 parse_dates=['created_at'],
                 na_values=['', 'NULL', 'N/A'])

# Parquet (preferred for big data)
df = pd.read_parquet('data.parquet')

# Multiple files
import glob
files = glob.glob('data/*.csv')
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

# SQL
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@host:5432/db')
df = pd.read_sql('SELECT * FROM users', engine)


# EXPLORING DATA

df.head(10)           # First 10 rows
df.tail(10)           # Last 10 rows
df.shape              # (rows, columns)
df.dtypes             # Column types
df.info()             # Summary info
df.describe()         # Statistics
df.columns.tolist()   # Column names
df.nunique()          # Unique values per column
df['column'].value_counts()  # Value distribution


# SELECTING DATA

# Single column
df['name']

# Multiple columns
df[['name', 'email']]

# Filter rows
df[df['age'] > 30]
df[(df['age'] > 30) & (df['city'] == 'NYC')]
df[df['status'].isin(['active', 'pending'])]
df[df['name'].str.contains('john', case=False)]

# loc (label-based) and iloc (integer-based)
df.loc[df['id'] == 1, ['name', 'email']]
df.iloc[0:10, 0:3]

# Query method (readable filters)
df.query('age > 30 and city == "NYC"')
df.query('status in @valid_statuses')  # Use variable


# TRANSFORMING DATA

# New columns
df['full_name'] = df['first_name'] + ' ' + df['last_name']
df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 100],
                         labels=['child', 'young', 'middle', 'senior'])

# Apply function
df['name_clean'] = df['name'].apply(lambda x: x.strip().title())
df['processed'] = df.apply(lambda row: process_row(row), axis=1)

# Map values
status_map = {'A': 'Active', 'I': 'Inactive', 'P': 'Pending'}
df['status_full'] = df['status'].map(status_map)

# Rename columns
df = df.rename(columns={'old_name': 'new_name'})
df.columns = [col.lower().replace(' ', '_') for col in df.columns]

# Change types
df['id'] = df['id'].astype(int)
df['date'] = pd.to_datetime(df['date'])
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')


# HANDLING MISSING DATA

df.isnull().sum()           # Count nulls per column
df.dropna()                 # Drop rows with any null
df.dropna(subset=['name'])  # Drop if name is null
df.fillna(0)                # Fill with value
df.fillna({'age': 0, 'name': 'Unknown'})  # Fill specific columns
df['value'].fillna(df['value'].mean())    # Fill with mean
df.ffill()                  # Forward fill
df.bfill()                  # Backward fill
```

### 2.2 Aggregations và GroupBy

```python
# BASIC AGGREGATIONS

df['amount'].sum()
df['amount'].mean()
df['amount'].median()
df['amount'].std()
df['amount'].min()
df['amount'].max()

# Multiple aggregations
df.agg({
    'amount': ['sum', 'mean', 'count'],
    'quantity': ['sum', 'min', 'max']
})


# GROUPBY

# Single column groupby
df.groupby('category')['amount'].sum()

# Multiple columns
df.groupby(['category', 'year'])['amount'].sum()

# Multiple aggregations
df.groupby('category').agg({
    'amount': 'sum',
    'quantity': 'mean',
    'id': 'count'
}).rename(columns={'id': 'order_count'})

# Named aggregations (cleaner)
df.groupby('category').agg(
    total_amount=('amount', 'sum'),
    avg_quantity=('quantity', 'mean'),
    order_count=('id', 'count')
)

# Custom aggregation
df.groupby('category').agg(
    total=('amount', 'sum'),
    pct_of_total=('amount', lambda x: x.sum() / df['amount'].sum())
)

# Transform (keep original shape)
df['category_total'] = df.groupby('category')['amount'].transform('sum')
df['pct_of_category'] = df['amount'] / df['category_total']

# Filter groups
df.groupby('category').filter(lambda x: x['amount'].sum() > 1000)


# PIVOT TABLES

# Simple pivot
pivot = df.pivot_table(
    values='amount',
    index='category',
    columns='year',
    aggfunc='sum',
    fill_value=0
)

# Multiple values and aggfuncs
pivot = df.pivot_table(
    values=['amount', 'quantity'],
    index=['category', 'subcategory'],
    columns='year',
    aggfunc={'amount': 'sum', 'quantity': 'mean'}
)

# Crosstab
pd.crosstab(df['category'], df['status'], margins=True)
```

### 2.3 Merging và Joining

```python
# MERGE (SQL-style join)

# Inner join
merged = pd.merge(orders, customers, on='customer_id', how='inner')

# Left join
merged = pd.merge(orders, customers, on='customer_id', how='left')

# Multiple keys
merged = pd.merge(df1, df2, on=['key1', 'key2'])

# Different column names
merged = pd.merge(orders, customers, 
                  left_on='cust_id', 
                  right_on='customer_id')

# Merge with indicator
merged = pd.merge(df1, df2, how='outer', indicator=True)
only_in_df1 = merged[merged['_merge'] == 'left_only']


# CONCAT (stack dataframes)

# Vertical stack
combined = pd.concat([df1, df2, df3], ignore_index=True)

# Horizontal stack
combined = pd.concat([df1, df2], axis=1)


# JOIN (index-based)
result = df1.join(df2, how='left')
```

### 2.4 Performance Optimization

```python
# MEMORY OPTIMIZATION

# Check memory usage
df.info(memory_usage='deep')
df.memory_usage(deep=True)

# Downcast numeric types
df['int_col'] = pd.to_numeric(df['int_col'], downcast='integer')
df['float_col'] = pd.to_numeric(df['float_col'], downcast='float')

# Use categories for low-cardinality strings
df['category'] = df['category'].astype('category')

# Optimize before loading
dtype_spec = {
    'id': 'int32',
    'amount': 'float32',
    'status': 'category'
}
df = pd.read_csv('data.csv', dtype=dtype_spec)


# PERFORMANCE TIPS

# Vectorized operations (fast)
df['total'] = df['price'] * df['quantity']  # Good

# Avoid iterrows (slow)
for idx, row in df.iterrows():  # Bad - very slow
    pass

# Use itertuples if needed (faster than iterrows)
for row in df.itertuples():
    print(row.name, row.amount)

# Use numpy for heavy calculations
df['result'] = np.where(df['value'] > 0, df['value'], 0)

# Chunked reading for large files
chunks = pd.read_csv('large.csv', chunksize=100000)
results = []
for chunk in chunks:
    processed = process(chunk)
    results.append(processed)
final = pd.concat(results)
```

---

## PHẦN 3: DATABASE CONNECTIVITY

### 3.1 SQLAlchemy

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# CONNECTION STRINGS

# PostgreSQL
engine = create_engine(
    'postgresql://user:password@host:5432/database',
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# MySQL
engine = create_engine('mysql+pymysql://user:pass@host:3306/db')

# SQLite
engine = create_engine('sqlite:///local.db')

# With connection pooling
engine = create_engine(
    connection_string,
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600,   # Recycle after 1 hour
    echo=False           # Log SQL statements
)


# EXECUTING QUERIES

# Read data
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    rows = result.fetchall()

# With parameters (safe from SQL injection)
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM users WHERE id = :user_id"),
        {"user_id": 123}
    )

# Pandas integration
df = pd.read_sql(
    "SELECT * FROM orders WHERE date >= :start_date",
    engine,
    params={"start_date": "2024-01-01"}
)

# Write data
df.to_sql('table_name', engine, 
          if_exists='replace',  # or 'append', 'fail'
          index=False,
          chunksize=10000)


# TRANSACTIONS

with engine.begin() as conn:  # Auto-commit on success
    conn.execute(text("INSERT INTO logs VALUES (:msg)"), {"msg": "start"})
    conn.execute(text("UPDATE users SET status = 'processed'"))
    # Commits automatically if no exception

# Manual transaction control
with engine.connect() as conn:
    trans = conn.begin()
    try:
        conn.execute(text("INSERT INTO ..."))
        conn.execute(text("UPDATE ..."))
        trans.commit()
    except:
        trans.rollback()
        raise
```

### 3.2 Async Database Access

```python
import asyncio
import asyncpg
import aiomysql

# ASYNCPG (PostgreSQL)

async def fetch_users():
    conn = await asyncpg.connect(
        user='user',
        password='password',
        database='database',
        host='localhost'
    )
    
    rows = await conn.fetch('SELECT * FROM users')
    await conn.close()
    return rows

# Connection pool
async def main():
    pool = await asyncpg.create_pool(
        user='user',
        password='password',
        database='database',
        host='localhost',
        min_size=5,
        max_size=20
    )
    
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM users')
    
    await pool.close()

asyncio.run(main())


# BATCH OPERATIONS

async def batch_insert(pool, records):
    async with pool.acquire() as conn:
        await conn.executemany(
            'INSERT INTO users(name, email) VALUES($1, $2)',
            [(r['name'], r['email']) for r in records]
        )

# Parallel queries
async def parallel_fetch(pool, user_ids):
    async def fetch_one(user_id):
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                'SELECT * FROM users WHERE id = $1',
                user_id
            )
    
    tasks = [fetch_one(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)
```

---

## PHẦN 4: FILE HANDLING

### 4.1 Working with Various Formats

```python
import json
import csv
import yaml
import pyarrow.parquet as pq
import pyarrow as pa

# JSON

# Read JSON
with open('data.json', 'r') as f:
    data = json.load(f)

# Write JSON
with open('output.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)

# JSON Lines (one JSON per line)
def read_jsonl(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield json.loads(line)

def write_jsonl(filepath, records):
    with open(filepath, 'w') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')


# CSV

# Read CSV
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)

# Write CSV
with open('output.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'name', 'email'])
    writer.writeheader()
    writer.writerows(records)


# PARQUET (Best for analytics)

# Read Parquet
df = pd.read_parquet('data.parquet')

# Write Parquet
df.to_parquet(
    'output.parquet',
    engine='pyarrow',
    compression='snappy',
    index=False
)

# Partitioned Parquet
df.to_parquet(
    'output/',
    partition_cols=['year', 'month'],
    engine='pyarrow'
)

# Read specific columns (efficient)
df = pd.read_parquet('data.parquet', columns=['id', 'name'])

# PyArrow for more control
table = pq.read_table('data.parquet')
df = table.to_pandas()


# YAML

# Read YAML
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Write YAML
with open('config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
```

### 4.2 Working with Cloud Storage

```python
import boto3
from google.cloud import storage
from azure.storage.blob import BlobServiceClient

# AWS S3

s3 = boto3.client('s3')

# Upload file
s3.upload_file('local.csv', 'bucket-name', 'path/to/file.csv')

# Download file
s3.download_file('bucket-name', 'path/to/file.csv', 'local.csv')

# Read directly to pandas
import s3fs
df = pd.read_parquet('s3://bucket/path/data.parquet')

# List objects
response = s3.list_objects_v2(Bucket='bucket-name', Prefix='path/')
for obj in response.get('Contents', []):
    print(obj['Key'])


# GOOGLE CLOUD STORAGE

client = storage.Client()
bucket = client.bucket('bucket-name')

# Upload
blob = bucket.blob('path/to/file.csv')
blob.upload_from_filename('local.csv')

# Download
blob.download_to_filename('local.csv')

# Read directly
df = pd.read_parquet('gs://bucket/path/data.parquet')


# AZURE BLOB STORAGE

blob_service = BlobServiceClient.from_connection_string(conn_str)
container = blob_service.get_container_client('container-name')

# Upload
with open('local.csv', 'rb') as data:
    container.upload_blob(name='path/file.csv', data=data)

# Read directly
df = pd.read_parquet('abfss://container@account.dfs.core.windows.net/path/')
```

---

## PHẦN 5: API DEVELOPMENT

### 5.1 FastAPI for Data APIs

```python
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

app = FastAPI(title="Data API")


# MODELS

class DataRecord(BaseModel):
    id: int
    name: str
    value: float
    category: Optional[str] = None

class DataResponse(BaseModel):
    data: List[DataRecord]
    total: int
    page: int
    page_size: int


# ENDPOINTS

@app.get("/data", response_model=DataResponse)
async def get_data(
    category: Optional[str] = Query(None),
    min_value: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000)
):
    """Get paginated data with filters"""
    df = pd.read_parquet('data.parquet')
    
    # Apply filters
    if category:
        df = df[df['category'] == category]
    if min_value:
        df = df[df['value'] >= min_value]
    
    # Paginate
    total = len(df)
    start = (page - 1) * page_size
    df = df.iloc[start:start + page_size]
    
    return {
        "data": df.to_dict('records'),
        "total": total,
        "page": page,
        "page_size": page_size
    }


@app.post("/data")
async def insert_data(records: List[DataRecord]):
    """Insert new records"""
    df = pd.DataFrame([r.dict() for r in records])
    
    # Append to existing data
    existing = pd.read_parquet('data.parquet')
    combined = pd.concat([existing, df], ignore_index=True)
    combined.to_parquet('data.parquet', index=False)
    
    return {"inserted": len(records)}


@app.get("/data/stats")
async def get_stats(category: Optional[str] = None):
    """Get aggregate statistics"""
    df = pd.read_parquet('data.parquet')
    
    if category:
        df = df[df['category'] == category]
    
    return {
        "count": len(df),
        "sum": df['value'].sum(),
        "mean": df['value'].mean(),
        "min": df['value'].min(),
        "max": df['value'].max()
    }


# DEPENDENCY INJECTION

async def get_db_connection():
    engine = create_engine(DATABASE_URL)
    try:
        yield engine
    finally:
        engine.dispose()

@app.get("/users")
async def get_users(engine = Depends(get_db_connection)):
    df = pd.read_sql("SELECT * FROM users", engine)
    return df.to_dict('records')


# Run with: uvicorn main:app --reload
```

### 5.2 Requests và HTTP Clients

```python
import requests
import httpx
import aiohttp
import asyncio

# REQUESTS (Synchronous)

response = requests.get(
    'https://api.example.com/data',
    headers={'Authorization': 'Bearer token'},
    params={'page': 1, 'limit': 100},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
else:
    response.raise_for_status()

# POST request
response = requests.post(
    'https://api.example.com/data',
    json={'name': 'test', 'value': 123},
    headers={'Content-Type': 'application/json'}
)

# Session for connection reuse
session = requests.Session()
session.headers.update({'Authorization': 'Bearer token'})
for page in range(1, 10):
    response = session.get(f'https://api.example.com/data?page={page}')


# HTTPX (Async support)

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com/data')
        return response.json()

# Parallel requests
async def fetch_all(urls):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]


# AIOHTTP

async def fetch_with_aiohttp():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com/data') as response:
            return await response.json()

# Rate limited fetching
async def fetch_with_rate_limit(urls, rate_limit=10):
    semaphore = asyncio.Semaphore(rate_limit)
    
    async def fetch_one(session, url):
        async with semaphore:
            async with session.get(url) as response:
                return await response.json()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

---

## PHẦN 6: ERROR HANDLING & LOGGING

### 6.1 Exception Handling

```python
import logging
from typing import Optional

# CUSTOM EXCEPTIONS

class DataPipelineError(Exception):
    """Base exception for pipeline errors"""
    pass

class DataValidationError(DataPipelineError):
    """Raised when data validation fails"""
    pass

class DataSourceError(DataPipelineError):
    """Raised when data source is unavailable"""
    pass


# ERROR HANDLING PATTERNS

def safe_transform(record: dict) -> Optional[dict]:
    """Transform with error handling"""
    try:
        return {
            'id': int(record['id']),
            'amount': float(record['amount']),
            'date': pd.to_datetime(record['date'])
        }
    except (KeyError, ValueError, TypeError) as e:
        logging.warning(f"Failed to transform record: {record}. Error: {e}")
        return None


def process_with_recovery(records: list) -> tuple:
    """Process records with error recovery"""
    success = []
    failed = []
    
    for record in records:
        try:
            result = transform(record)
            success.append(result)
        except Exception as e:
            failed.append({
                'record': record,
                'error': str(e)
            })
    
    return success, failed


# RETRY LOGIC

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def fetch_with_retry(url: str) -> dict:
    """Fetch with automatic retry on failure"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

### 6.2 Logging Best Practices

```python
import logging
import json
from datetime import datetime

# BASIC SETUP

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline.log')
    ]
)

logger = logging.getLogger(__name__)


# STRUCTURED LOGGING

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log(self, level: str, message: str, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        getattr(self.logger, level.lower())(json.dumps(log_entry))
    
    def info(self, message: str, **kwargs):
        self.log('INFO', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log('ERROR', message, **kwargs)

# Usage
logger = StructuredLogger('pipeline')
logger.info('Processing started', 
            job_id='job-123',
            records_count=1000)


# PIPELINE LOGGING PATTERN

class PipelineLogger:
    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        self.start_time = None
        self.metrics = {}
    
    def start(self):
        self.start_time = datetime.now()
        logger.info(f"Pipeline {self.pipeline_name} started")
    
    def log_metric(self, name: str, value):
        self.metrics[name] = value
    
    def end(self, status: str = 'success'):
        duration = (datetime.now() - self.start_time).total_seconds()
        logger.info(
            f"Pipeline {self.pipeline_name} {status}",
            extra={
                'duration_seconds': duration,
                'metrics': self.metrics
            }
        )

# Usage
pl = PipelineLogger('daily_etl')
pl.start()
pl.log_metric('rows_processed', 10000)
pl.log_metric('rows_failed', 5)
pl.end('success')
```

---

## PHẦN 7: TESTING

### 7.1 Unit Testing

```python
import pytest
import pandas as pd
from unittest.mock import Mock, patch

# BASIC TESTS

def test_transform_record():
    input_record = {'id': '1', 'amount': '100.50'}
    result = transform_record(input_record)
    
    assert result['id'] == 1
    assert result['amount'] == 100.50


def test_transform_with_missing_field():
    input_record = {'id': '1'}  # Missing 'amount'
    
    with pytest.raises(KeyError):
        transform_record(input_record)


# FIXTURES

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'id': [1, 2, 3],
        'value': [10, 20, 30],
        'category': ['A', 'B', 'A']
    })

def test_aggregation(sample_dataframe):
    result = aggregate_by_category(sample_dataframe)
    
    assert result.loc['A', 'value'] == 40
    assert result.loc['B', 'value'] == 20


# MOCKING

@patch('module.requests.get')
def test_api_fetch(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {'data': [1, 2, 3]}
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    result = fetch_data('https://api.example.com')
    
    assert result == {'data': [1, 2, 3]}
    mock_get.assert_called_once()


# PARAMETERIZED TESTS

@pytest.mark.parametrize("input_val,expected", [
    ("100", 100.0),
    ("100.50", 100.50),
    ("-50", -50.0),
])
def test_parse_amount(input_val, expected):
    assert parse_amount(input_val) == expected


# RUN: pytest test_module.py -v
```

### 7.2 Integration Testing

```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="module")
def postgres_container():
    """Spin up PostgreSQL container for tests"""
    with PostgresContainer("postgres:14") as postgres:
        yield postgres

@pytest.fixture
def db_engine(postgres_container):
    """Create engine connected to test container"""
    engine = create_engine(postgres_container.get_connection_url())
    
    # Create test tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100)
            )
        """))
    
    yield engine
    engine.dispose()

def test_data_pipeline(db_engine):
    """Test full pipeline with real database"""
    # Insert test data
    test_data = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'email': ['alice@test.com', 'bob@test.com']
    })
    test_data.to_sql('users', db_engine, if_exists='append', index=False)
    
    # Run pipeline
    result = run_pipeline(db_engine)
    
    # Verify results
    assert result['processed_count'] == 2
    
    df = pd.read_sql('SELECT * FROM users', db_engine)
    assert len(df) == 2
```

---

## PHẦN 8: BEST PRACTICES

### 8.1 Code Organization

```
project/
├── src/
│   ├── __init__.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── api_extractor.py
│   │   └── db_extractor.py
│   ├── transformers/
│   │   ├── __init__.py
│   │   └── data_transformer.py
│   ├── loaders/
│   │   ├── __init__.py
│   │   └── warehouse_loader.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── config.py
│   └── pipelines/
│       ├── __init__.py
│       └── daily_etl.py
├── tests/
│   ├── unit/
│   └── integration/
├── config/
│   ├── dev.yaml
│   └── prod.yaml
├── requirements.txt
├── setup.py
└── README.md
```

### 8.2 Configuration Management

```python
from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings from environment"""
    
    # Database
    database_url: str
    database_pool_size: int = 5
    
    # API
    api_key: str
    api_timeout: int = 30
    
    # Pipeline
    batch_size: int = 1000
    max_retries: int = 3
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Usage
settings = get_settings()
engine = create_engine(settings.database_url)
```

### 8.3 Type Hints

```python
from typing import List, Dict, Optional, Union, TypeVar
from dataclasses import dataclass
import pandas as pd

T = TypeVar('T')

@dataclass
class ProcessingResult:
    success: bool
    records_processed: int
    errors: List[str]
    duration_seconds: float

def process_batch(
    records: List[Dict[str, any]],
    transform_fn: callable,
    batch_size: int = 100
) -> ProcessingResult:
    """
    Process records in batches with type hints.
    
    Args:
        records: List of dictionaries to process
        transform_fn: Function to apply to each record
        batch_size: Number of records per batch
    
    Returns:
        ProcessingResult with status and metrics
    """
    ...\n```

---

## 📦 UV - Fast Python Package Manager

### UV là gì?

```
UV là package manager mới nhất cho Python:
- Viết bằng Rust (cực nhanh)
- Drop-in replacement cho pip, venv, pip-tools
- 10-100x faster than pip
- Tích hợp với pyproject.toml
- Tạo bởi Astral (makers of Ruff)
```

### Cài đặt UV

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip (ironic but works)
pip install uv

# Or with Homebrew
brew install uv

# Verify installation
uv --version
```

### Package Management

```bash
# Create virtual environment (instant!)
uv venv

# Activate
source .venv/bin/activate  # Linux/Mac
.venv\\Scripts\\activate     # Windows

# Install packages (much faster than pip)
uv pip install pandas polars duckdb

# Install from requirements.txt
uv pip install -r requirements.txt

# Install with extras
uv pip install "fastapi[all]"

# Sync dependencies (like pip-sync)
uv pip sync requirements.txt
```

### UV Init và Project Management

```bash
# Initialize new project
uv init my_project
cd my_project

# Add dependency
uv add polars
uv add pandas ">=2.0"

# Add dev dependency
uv add --dev pytest ruff mypy

# Remove dependency
uv remove polars

# Lock dependencies
uv lock

# Sync environment with lock file
uv sync
```

### UV với pyproject.toml

```toml
# pyproject.toml
[project]
name = "de-pipeline"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "polars>=0.20",
    "duckdb>=0.10",
    "pyarrow>=15.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.3",
    "mypy>=1.8",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "ruff>=0.3",
]
```

### UV Scripts

```bash
# Run script without installing globally
uv run python script.py

# Run with specific Python version
uv run --python 3.12 python script.py

# Run tool (like npx for Python)
uv tool run ruff check .
uv tool run mypy src/
```

### UV vs pip Performance

| Operation | pip | uv | Speedup |
|---|---|---|---|
| Install pandas | 5.2s | 0.3s | 17x |
| Install from lock | 12s | 0.5s | 24x |
| Create venv | 3s | 0.01s | 300x |
| Resolve dependencies | 8s | 0.2s | 40x |

### Workflow: Data Engineering Project

```bash
# 1. Create project
uv init de-pipeline
cd de-pipeline

# 2. Add dependencies
uv add polars duckdb pyarrow
uv add sqlalchemy psycopg2-binary
uv add --dev pytest ruff mypy

# 3. Lock dependencies
uv lock

# 4. Run scripts
uv run python src/pipeline.py

# 5. Run tests
uv run pytest

# 6. CI/CD - fast install from lock
uv sync --frozen

# 7. Docker (fast layer caching)
# Dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
CMD ["uv", "run", "python", "main.py"]
```

### UV Tips

```
1. Always use uv venv instead of python -m venv
   → Instant creation

2. Use uv lock for reproducible builds
   → Creates uv.lock file

3. Use uv sync in CI/CD
   → Much faster than pip install

4. Use uv tool run for one-off tools
   → No global install needed

5. Replace pip-tools with uv
   uv pip compile requirements.in -o requirements.txt

6. Migration from pip
   → Just replace 'pip' with 'uv pip'
   → Most commands work identically
```

---

*Document Version: 1.1*
*Last Updated: January 2025*
*Coverage: Python core, Pandas, Databases, APIs, Testing, UV*
