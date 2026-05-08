import sqlite3
conn = sqlite3.connect('newsletter.db')
cur = conn.cursor()
cur.execute("SELECT newsletter_text FROM newsletter_runs ORDER BY created_at DESC LIMIT 1")
row = cur.fetchone()
if not row:
    print('no newsletter')
    exit(0)
text = row[0]
needle = 'Follow for more AI insights'
start = 0
count = 0
while True:
    idx = text.lower().find(needle.lower(), start)
    if idx == -1:
        break
    count += 1
    context = text[idx-40:idx+120]
    print(f'Occurrence {count} at {idx}:')
    print(context)
    print('---')
    start = idx + len(needle)
print('Total occurrences:', count)
conn.close()
