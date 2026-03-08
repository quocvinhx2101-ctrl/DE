import sqlite3
import random
from datetime import datetime, timedelta

def create_dummy_data():
    conn = sqlite3.connect("lab1.db")
    cursor = conn.cursor()

    # 1. Create Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_clickstream (
        user_id INTEGER,
        event_time TIMESTAMP,
        page_url TEXT
    );
    """)

    # 2. Generate Data
    # Scenario:
    # User 1: 
    #   - Session A: 08:00, 08:05, 08:29 (All within 30 mins gap)
    #   - Session B: 09:15 (Gap > 30 mins from 08:29)
    # User 2:
    #   - Session C: 10:00, 10:01
    
    data = [
        (1, "2024-01-01 08:00:00", "/home"),
        (1, "2024-01-01 08:05:00", "/products"),
        (1, "2024-01-01 08:29:00", "/cart"),  # < 30 mins from prev
        (1, "2024-01-01 09:15:00", "/checkout"), # > 30 mins from prev -> NEW SESSION
        (1, "2024-01-01 09:20:00", "/thank-you"),
        
        (2, "2024-01-01 10:00:00", "/home"),
        (2, "2024-01-01 10:01:00", "/about"),
        
        (3, "2024-01-01 12:00:00", "/home"), # Single event session
    ]

    cursor.executemany("INSERT INTO user_clickstream VALUES (?, ?, ?)", data)
    conn.commit()
    print("✅ Database created: 'lab1.db'")
    print(f"✅ Inserted {len(data)} rows.")
    
    # 3. Verify
    print("\nSample Data:")
    for row in cursor.execute("SELECT * FROM user_clickstream LIMIT 5"):
        print(row)

    conn.close()

if __name__ == "__main__":
    create_dummy_data()
