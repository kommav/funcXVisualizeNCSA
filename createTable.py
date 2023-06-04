import sqlite3
import json

# Connect to the SQLite database
conn = sqlite3.connect('funcx.sqlite3')
cursor = conn.cursor()

# Define the name of the old table and the new table
old_table_name = 'awslog'
new_table_name = 'new_awslog'

# Retrieve all rows from the old table
cursor.execute(f"SELECT entry FROM {old_table_name}")
rows = cursor.fetchall()

# Get the column names from the JSON entry
sample_row = json.loads(rows[0][0])  # Parse the JSON entry
column_names = list(sample_row.keys())

# Create a new table with desired columns
create_table_query = f"CREATE TABLE {new_table_name} ({', '.join([f'{name} TEXT' for name in column_names])})"
cursor.execute(create_table_query)

# Insert data into the new table
for row in rows:
    entry = json.loads(row[0])  # Parse the JSON entry

    # Prepare the column names and placeholders for the INSERT query
    column_placeholders = ', '.join(['?' for _ in column_names])
    column_names_string = ', '.join(column_names)

    # Prepare the values for insertion
    values = [entry[name] if name in entry else None for name in column_names]

    # Execute the INSERT query
    insert_query = f"INSERT INTO {new_table_name} ({column_names_string}) VALUES ({column_placeholders})"
    cursor.execute(insert_query, tuple(values))

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"New table '{new_table_name}' created with the desired columns.")