import sqlite3


class Solver:
    def __init__(self):
        db_path = 'idiom.db'
        conn = sqlite3.connect(db_path)
        self.cursor = conn.cursor()
        self.condition_strings = []
    
    def __call__(self, feedback):
        assert len(feedback) == 4
        for i, [c, v, t] in enumerate(feedback, start = 1):
            for part_id, part_data in enumerate([c, v, t]):
                part_name = ['c', 'v', 't'][part_id]
                label, score = part_data
                if score == 0:
                    r = [i] if part_name == 't' else range(1, 5)
                    self.condition_strings.append(' AND '.join([f"{part_name}{k} != '{label}'" for k in r]))
                elif score == 1:
                    self.condition_strings.append(f"{part_name}{i} != '{label}'")
                    self.condition_strings.append(
                        '(' + ' OR '.join([f"{part_name}{k} = '{label}'" for k in range(1, 5) if k != i]) + ')')
                elif score == 2:
                    self.condition_strings.append(f"{part_name}{i} = '{label}'")
        joined_condition_string = ' AND '.join(self.condition_strings)
        self.cursor.execute(f'SELECT word FROM idioms WHERE {joined_condition_string}')
        result = self.cursor.fetchall()
        return ', '.join([x[0] for x in result])
