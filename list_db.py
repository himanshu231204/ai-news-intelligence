import sqlite3
conn = sqlite3.connect('newsletter.db')
cur = conn.cursor()
cur.execute("SELECT id, created_at, article_count, LENGTH(newsletter_text) FROM newsletter_runs ORDER BY created_at DESC LIMIT 10")
for row in cur.fetchall():
    print(row)
conn.close()
