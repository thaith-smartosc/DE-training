import pandas as pd
from sqlalchemy import create_engine

# Step 1: Load CSV using pandas
csv_file_path = "output/grouped_sales/part-00000-361847dd-e9c6-4cf4-95e7-41718c6d1c41-c000.csv"
df = pd.read_csv(csv_file_path)

# Step 2: PostgreSQL connection details
db_user = "myuser"
db_pass = "mypassword"
db_host = "localhost"
db_port = "5432"
db_name = "mydatabase"
table_name = "grouped_sales"

# Step 3: Connect and load into PostgreSQL
engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
df.to_sql(table_name, engine, if_exists='replace', index=False)

print(f"✅ Successfully loaded data into PostgreSQL table: {table_name}")
