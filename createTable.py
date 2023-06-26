import sqlite3
import json

conn = sqlite3.connect('funcx.sqlite3')
cursor = conn.cursor()

old_table_name = 'awslog'
new_table_name = 'new_awslog2'

cursor.execute(f"SELECT entry FROM {old_table_name}")
rows = cursor.fetchall()

sample_row = json.loads(rows[len(rows) - 1][0])
column_names = list(sample_row.keys())

create_table_query = f"CREATE TABLE {new_table_name} ({', '.join([f'{name} TEXT' for name in column_names])})"
cursor.execute(create_table_query)

for row in rows:
    entry = json.loads(row[0]) 
    column_placeholders = ', '.join(['?' for _ in column_names])
    column_names_string = ', '.join(column_names)

    values = [entry[name] if name in entry else None for name in column_names]

    insert_query = f"INSERT INTO {new_table_name} ({column_names_string}) VALUES ({column_placeholders})"
    cursor.execute(insert_query, tuple(values))

conn.commit()
conn.close()

print(f"New table '{new_table_name}' created with the desired columns.")