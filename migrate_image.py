import MySQLdb

def migrate():
    try:
        db = MySQLdb.connect(host="localhost", port=3307, user="root", password="nutan@932654", database="online_exam")
        cur = db.cursor()
        
        print("Adding image_path column to questions table...")
        # Check if column exists first
        cur.execute("SHOW COLUMNS FROM questions LIKE 'image_path'")
        result = cur.fetchone()
        
        if not result:
            cur.execute("ALTER TABLE questions ADD COLUMN image_path VARCHAR(255) NULL AFTER answer_explanation")
            db.commit()
            print("Successfully added image_path column.")
        else:
            print("image_path column already exists.")
            
        cur.close()
        db.close()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
