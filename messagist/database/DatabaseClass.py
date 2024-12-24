import psycopg2
from psycopg2 import sql
from psycopg2 import OperationalError

class DatabaseClass:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to the PostgreSQL database. Create the database if it does not exist."""
        try:
            # Step 1: Connect to the default 'postgres' database to check/create the database
            temp_connection = psycopg2.connect(
                dbname="postgres",  # Default PostgreSQL database
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            temp_connection.autocommit = True  # Enable autocommit for creating databases
            temp_cursor = temp_connection.cursor()

            # Step 2: Check if the database exists
            temp_cursor.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
                [self.dbname]
            )
            if not temp_cursor.fetchone():
                # Database does not exist, create it
                temp_cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.dbname))
                )
                print(f"Database '{self.dbname}' created successfully.")
            else:
                print(f"Database '{self.dbname}' already exists.")

            # Close temporary connection
            temp_cursor.close()
            temp_connection.close()

            # Step 3: Connect to the specified database
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to {self.dbname} database.")
        except OperationalError as e:
            print(f"Error: {e}")
            self.connection = None
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.connection = None


    def execute_script(self, script_path):
        """Execute a SQL script from a file."""
        if not self.connection:
            raise Exception("Not connected to the database.")
        try:
            with open(script_path, 'r') as file:
                sql_script = file.read()
            self.cursor.execute(sql_script)
            self.connection.commit()
            print(f"SQL script '{script_path}' executed successfully.")
        except Exception as e:
            print(f"Error executing script '{script_path}': {e}")

    def execute_query(self, query, params=None):
        """Execute a single query."""
        if not self.connection:
            raise Exception("Not connected to the database.")
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f"Error executing query: {e}")

    def fetch_one(self, query, params=None):
        """Fetch all results from a query."""
        if not self.connection:
            raise Exception("Not connected to the database.")
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def close(self):
        """Close the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Connection closed.")
