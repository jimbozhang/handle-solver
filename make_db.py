from pathlib import Path
import sqlite3

from pinyin_parser import PinyinParser


def add_idiom_to_db(cursor, parser, word, pinyin):    
    pinyins = pinyin.split(' ')
    assert len(word) == 4 and len(pinyins) == 4

    row_values = [word]
    for pinyin in pinyins:
        cvt = parser(pinyin)
        assert len(cvt) == 3
        row_values.extend(cvt)
    cursor.execute("INSERT INTO idioms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row_values)

def main():
    dataset_path = Path('idiom.csv')
    db_path = Path('idiom.db')

    if db_path.exists():
        db_path.unlink()
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE idioms
             (word, c1, v1, t1, c2, v2, t2, c3, v3, t3, c4, v4, t4)''')

    parser = PinyinParser()

    for line in dataset_path.read_text(encoding='utf').splitlines():
        word, pinyin = line.strip('\n').split(',')
        add_idiom_to_db(cursor, parser, word, pinyin)
    
    db.commit()
    db.close()


if __name__ == '__main__':
    main()
