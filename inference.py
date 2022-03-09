import sqlite3


def main():
    db_path = 'idiom.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM idioms;''')
    rows = cursor.fetchall()
    conn.close()


if __name__ == '__main__':
    main()
