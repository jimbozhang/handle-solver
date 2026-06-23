"""Build the idiom SQLite database from idiom.csv."""

import re
import sqlite3
from pathlib import Path


class PinyinParser:
    """Parse a pinyin syllable into (consonant, vowel, tone)."""

    def __init__(self):
        self.c_list = [
            'zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q',
            'r', 'x', 'w', 'y', 'z', 'c', 's'
        ]
        self.v_list = [
            'a', 'ai', 'an', 'ang', 'ao', 'e', 'ei', 'en', 'eng', 'er', 'i',
            'ia', 'ian', 'iang', 'iao', 'ie', 'in', 'ing', 'io', 'iong', 'iu',
            'o', 'ong', 'ou', 'u', 'ua', 'uai', 'uan', 'uang', 'ue', 'ui',
            'un', 'uo', 'v', 'van', 've', 'vn'
        ]

    def __call__(self, pinyin):
        c, vt = self._split_cv(pinyin)
        v, t = self._split_vt(vt)
        return [c, v, t]

    def _split_cv(self, pinyin):
        c = ''
        for x in self.c_list:
            if pinyin.startswith(x):
                c = x
                break
        return c, pinyin[len(c):]

    def _split_vt(self, v):
        if any(ch in v for ch in 'āēīōūǖ'):
            t = '1'
        elif any(ch in v for ch in 'áéíóúǘ'):
            t = '2'
        elif any(ch in v for ch in 'ǎěǐǒǔǚ'):
            t = '3'
        elif any(ch in v for ch in 'àèìòùǜ'):
            t = '4'
        else:
            t = '0'

        v = re.sub(r'[āáǎà]', 'a', v)
        v = re.sub(r'[ēéěè]', 'e', v)
        v = re.sub(r'[īíǐì]', 'i', v)
        v = re.sub(r'[ōóǒò]', 'o', v)
        v = re.sub(r'[ūúǔù]', 'u', v)
        v = re.sub(r'[ǖǘǚǜü]', 'v', v)

        assert v in self.v_list
        return v, t


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
