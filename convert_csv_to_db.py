import sqlite3
import csv

conn = sqlite3.connect("dictionary.db")
cursor = conn.cursor()

# Speed optimization
cursor.execute("PRAGMA journal_mode = OFF")
cursor.execute("PRAGMA synchronous = OFF")
cursor.execute("PRAGMA temp_store = MEMORY")

cursor.execute("""
CREATE TABLE IF NOT EXISTS dictionary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    en TEXT NOT NULL,
    hi TEXT NOT NULL
)
""")

# Old data delete (optional)
cursor.execute("DELETE FROM dictionary")

# Bulk insert for speed
with open("english_to_hindi_dictionary.csv", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    data = [(row["en"].lower(), row["hi"]) for row in reader]

cursor.executemany("INSERT INTO dictionary (en, hi) VALUES (?, ?)", data)

# Index for ultra-fast search
cursor.execute("CREATE INDEX IF NOT EXISTS idx_en ON dictionary(en)")

conn.commit()
conn.close()

print("✅ 124,290 words successfully converted!")