import sqlite3

conn = sqlite3.connect('funcx.sqlite3')
cursor = conn.cursor()

table_name1 = 'new_awslog2'
table_name2 = 'new_awslog3'

# Get the column names for new_awslog2 table
cursor.execute(f"PRAGMA table_info({table_name1})")
columns1 = cursor.fetchall()
column_names1 = [column[1] for column in columns1]

# Get the column names for new_awslog3 table
cursor.execute(f"PRAGMA table_info({table_name2})")
columns2 = cursor.fetchall()
column_names2 = [column[1] for column in columns2]

# Create indexes for new_awslog2 table
for column in column_names1:
    index_name = f"idx_{table_name1}_{column}"
    index_query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name1}({column})"
    cursor.execute(index_query)

# Create indexes for new_awslog3 table
for column in column_names2:
    index_name = f"idx_{table_name2}_{column}"
    index_query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name2}({column})"
    cursor.execute(index_query)

conn.commit()
conn.close()

print("Indexes created successfully.")