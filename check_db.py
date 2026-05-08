"""Check database schema."""
import sqlite3

conn = sqlite3.connect("newsletter.db")
cursor = conn.cursor()

# Get table info
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for row in cursor.fetchall():
    print(row[0])
    print()

conn.close()
