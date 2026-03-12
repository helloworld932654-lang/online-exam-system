import MySQLdb

db = MySQLdb.connect(host='localhost', user='root', passwd='nutan@932654', db='online_exam', port=3307)
cur = db.cursor()

queries = [
    "ALTER TABLE questions ADD COLUMN subject VARCHAR(100) DEFAULT 'General' AFTER id",
    "ALTER TABLE questions ADD COLUMN answer_explanation TEXT NULL AFTER correct_option",
    "ALTER TABLE results ADD COLUMN subject VARCHAR(100) DEFAULT 'General' AFTER user_id"
]

for query in queries:
    try:
        cur.execute(query)
        print(f"Executed: {query}")
    except Exception as e:
        print(f"Error on {query}: {e}")

db.commit()
cur.close()
db.close()
print("Migrations complete")
