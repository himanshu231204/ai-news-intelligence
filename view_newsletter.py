"""View the latest newsletter from database."""
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect("newsletter.db")
cursor = conn.cursor()

# Get the latest newsletter from newsletter_runs
cursor.execute(
    "SELECT newsletter_text, created_at, article_count FROM newsletter_runs ORDER BY created_at DESC LIMIT 1"
)

result = cursor.fetchone()
conn.close()

if result:
    newsletter, created_at, count = result
    print("=" * 80)
    print(f"Latest Newsletter ({count} items) - {created_at}")
    print("=" * 80)
    print(newsletter)
    print("\n" + "=" * 80)
    print(f"Length: {len(newsletter)} characters")
    print("=" * 80)
else:
    print("No newsletter found in database.")
