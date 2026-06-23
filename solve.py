#!/usr/bin/env python3
"""Handle (汉兜) solver — works with handle.antfu.me"""

import sqlite3
import sys
from pathlib import Path


# --- Database helpers ---

def ensure_db():
    """Ensure the idiom database exists, building it if necessary."""
    db_path = Path('idiom.db')
    csv_path = Path('idiom.csv')
    if db_path.exists():
        return
    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        sys.exit(1)
    print("First run, building idiom database...")
    import make_db
    make_db.main()
    print("Database ready.\n")


def get_pinyin(cursor, word):
    """Look up pinyin components for a 4-character idiom.

    Returns [(c1,v1,t1), (c2,v2,t2), ...] or None.
    """
    cursor.execute(
        'SELECT c1, v1, t1, c2, v2, t2, c3, v3, t3, c4, v4, t4 FROM idioms WHERE word = ?',
        (word,)
    )
    row = cursor.fetchone()
    if not row:
        return None
    return [(row[i], row[i+1], row[i+2]) for i in range(0, 12, 3)]


# --- Solver ---

class Solver:
    """Narrow down candidate idioms based on color feedback."""

    def __init__(self, db_path='idiom.db'):
        conn = sqlite3.connect(db_path)
        self.cursor = conn.cursor()
        self.condition_strings = []

    def __call__(self, feedback):
        assert len(feedback) == 4
        for i, [c, v, t] in enumerate(feedback, start=1):
            for part_id, part_data in enumerate([c, v, t]):
                part_name = ['c', 'v', 't'][part_id]
                label, score = part_data
                if score == 0:
                    r = [i] if part_name == 't' else range(1, 5)
                    self.condition_strings.append(
                        ' AND '.join([f"{part_name}{k} != '{label}'" for k in r]))
                elif score == 1:
                    self.condition_strings.append(f"{part_name}{i} != '{label}'")
                    self.condition_strings.append(
                        '(' + ' OR '.join(
                            [f"{part_name}{k} = '{label}'" for k in range(1, 5) if k != i]) + ')')
                elif score == 2:
                    self.condition_strings.append(f"{part_name}{i} = '{label}'")
        joined_condition_string = ' AND '.join(self.condition_strings)
        self.cursor.execute(f'SELECT word FROM idioms WHERE {joined_condition_string}')
        result = self.cursor.fetchall()
        return ', '.join([x[0] for x in result])


# --- CLI ---

def parse_input(line):
    """Parse user input into (word, digits). Raises ValueError on bad format.

    Accepted formats:
      马到成功 002102000002
      马到成功 002 102 000 002
    """
    parts = line.strip().split()
    if len(parts) == 2 and len(parts[1]) == 12 and parts[1].isdigit():
        return parts[0], parts[1]
    if len(parts) == 5 and all(len(p) == 3 and p.isdigit() for p in parts[1:]):
        return parts[0], ''.join(parts[1:])
    raise ValueError


def build_feedback(cursor, word, digits):
    """Build the feedback tuple that Solver expects from a word and 12 score digits."""
    pinyin_parts = get_pinyin(cursor, word)
    if pinyin_parts is None:
        raise ValueError(f"「{word}」 not found in dictionary")

    feedback = []
    for i, (c, v, t) in enumerate(pinyin_parts):
        b = i * 3
        feedback.append(((c, int(digits[b])), (v, int(digits[b+1])), (t, int(digits[b+2]))))
    return tuple(feedback)


def show_pinyin(cursor, word):
    """Print pinyin breakdown for a word, so the user can match game colors."""
    pinyin_parts = get_pinyin(cursor, word)
    if pinyin_parts is None:
        print(f"  「{word}」 not found in dictionary")
        return
    chars = list(word)
    print(f"  {'  '.join(f'{ch}({c}{v}{t})' for ch, (c, v, t) in zip(chars, pinyin_parts))}")


def format_candidates(result_str, max_show=20):
    """Format candidate words for display."""
    if not result_str:
        return "没有找到匹配的成语。"
    candidates = [w.strip() for w in result_str.split(',')]
    total = len(candidates)
    lines = []
    for start in range(0, min(total, max_show), 5):
        lines.append('、'.join(candidates[start:start+5]))
    if total > max_show:
        lines.append(f"... 共 {total} 个")
    else:
        lines.append(f"共 {total} 个")
    return '\n'.join(lines)


HELP = """\
操作步骤:
  1. 在 handle.antfu.me 猜一个四字成语
  2. 看游戏中每个拼音成分的颜色
  3. 回到这里，输入: 猜的词 + 12 个数字
     每个字的声母、韵母、声调各一个数字
     0=灰(没有) 1=黄(有但位置不对) 2=绿(正确)

示例: 你猜了"马到成功"，游戏里显示:
  马: 声母灰 韵母灰 声调绿  → 002
  到: 声母黄 韵母灰 声调绿  → 102
  成: 声母灰 韵母灰 声调灰  → 000
  功: 声母灰 韵母灰 声调绿  → 002

  输入: 马到成功 002 102 000 002

命令: /help  /reset  /list  /quit
"""


def main():
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')

    ensure_db()

    conn = sqlite3.connect('idiom.db')
    cursor = conn.cursor()
    solver = Solver()
    round_num = 0

    print("=== 汉兜解题工具 ===\n")
    print(HELP)

    while True:
        try:
            line = input(f"[第 {round_num + 1} 轮] ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not line:
            continue
        if line == '/help':
            print(HELP)
            continue
        if line == '/reset':
            solver = Solver()
            round_num = 0
            print("已重置。\n")
            continue
        if line == '/list':
            joined = ' AND '.join(solver.condition_strings)
            solver.cursor.execute(f'SELECT word FROM idioms WHERE {joined}')
            result = solver.cursor.fetchall()
            print(format_candidates(', '.join(x[0] for x in result)))
            print()
            continue
        if line == '/quit':
            break

        # Word only — show pinyin hint and wait for color digits
        if len(line) == 4 and ' ' not in line:
            show_pinyin(cursor, line)
            try:
                digits = input("  颜色: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break
            line = f"{line} {digits}"

        try:
            word, digits = parse_input(line)
        except ValueError:
            print("格式不对，输入 /help 查看说明\n")
            continue

        try:
            feedback = build_feedback(cursor, word, digits)
        except ValueError as e:
            print(f"{e}\n")
            continue

        result = solver(feedback)
        round_num += 1
        print(format_candidates(result))
        print()

    conn.close()


if __name__ == '__main__':
    main()
