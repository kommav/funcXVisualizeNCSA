# import sqlite3
# import json

# conn = sqlite3.connect('funcx.sqlite3')
# cursor = conn.cursor()

# old_table_name = 'awslog'
# new_table_name = 'new_awslog2'

# cursor.execute(f"SELECT entry FROM {old_table_name}")
# rows = cursor.fetchall()

# sample_row = json.loads(rows[len(rows) - 1][0])
# column_names = list(sample_row.keys())

# create_table_query = f"CREATE TABLE {new_table_name} ({', '.join([f'{name} TEXT' for name in column_names])})"
# cursor.execute(create_table_query)

# for row in rows:
#     entry = json.loads(row[0]) 
#     column_placeholders = ', '.join(['?' for _ in column_names])
#     column_names_string = ', '.join(column_names)

#     values = [entry[name] if name in entry else None for name in column_names]

#     insert_query = f"INSERT INTO {new_table_name} ({column_names_string}) VALUES ({column_placeholders})"
#     cursor.execute(insert_query, tuple(values))

# conn.commit()
# conn.close()

# print(f"New table '{new_table_name}' created with the desired columns.")

import sqlite3
import json

conn = sqlite3.connect('funcx.sqlite3')
cursor = conn.cursor()

old_table_name = 'awslog'
new_table_name1 = 'new_awslog2'
new_table_name2 = 'new_awslog3'

cursor.execute(f"SELECT entry FROM {old_table_name}")
rows = cursor.fetchall()

sample_row = json.loads(rows[len(rows) - 1][0])
column_names = list(sample_row.keys())

# Create new table new_awslog2
create_table_query1 = f"CREATE TABLE {new_table_name1} ({', '.join([f'{name} TEXT' for name in column_names])})"
cursor.execute(create_table_query1)

# Create new table new_awslog3 with only 'endpoint_name' and 'endpoint_id' columns
create_table_query2 = f"CREATE TABLE {new_table_name2} (endpoint_name TEXT, endpoint_id TEXT)"
cursor.execute(create_table_query2)

for row in rows:
    entry = json.loads(row[0]) 

    values1 = [entry[name] if name in entry else None for name in column_names]

    insert_query1 = f"INSERT INTO {new_table_name1} ({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})"
    cursor.execute(insert_query1, tuple(values1))

    if 'endpoint_name' in entry and 'endpoint_id' in entry:
        values2 = [entry['endpoint_name'], entry['endpoint_id']]
        insert_query2 = f"INSERT INTO {new_table_name2} (endpoint_name, endpoint_id) VALUES (?, ?)"
        cursor.execute(insert_query2, tuple(values2))

conn.commit()
conn.close()

print(f"New table '{new_table_name1}' created with the desired columns.")
print(f"New table '{new_table_name2}' created with only 'endpoint_name' and 'endpoint_id' columns.")