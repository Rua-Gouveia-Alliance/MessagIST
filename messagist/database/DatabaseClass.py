import psycopg
from psycopg import sql
from psycopg import OperationalError


# TODO: Estas exceptions lançadas aqui nao fazem sentido porque depois nao sao apanhadas em lado nenhum
# TODO: É preciso rever o codigo dos managers e dar rolback se excecoes forem lançadas.
# TODO: O ssl mode nao devia tar ativo?
class DatabaseClass:
    def __init__(
        self, dbname, user, password, sslmode="require", host="localhost", port="5432"
    ):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.sslmode = sslmode
        self.host = host
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the PostgreSQL database. Create the database if it does not exist."""
        try:
            # Step 1: Connect to the default 'postgres' database to check/create the database
            conn = psycopg.connect(
                dbname="postgres",  # Default PostgreSQL database
                # dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                autocommit=True,
                # sslmode = self.sslmode
            )
            cur = conn.cursor()

            # Step 2: Check if the database exists
            cur.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
                [self.dbname],
            )
            if not cur.fetchone():
                # Database does not exist, create it
                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.dbname))
                )
                print(f"Database '{self.dbname}' created successfully.")
            else:
                print(f"Database '{self.dbname}' already exists.")

            cur.close()
            conn.close()

            # Step 3: Connect to the specified database
            self.conn = psycopg.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            self.cur = self.conn.cursor()
            print(f"Connected to {self.dbname} database.")
        except OperationalError as e:
            print(f"Error: {e}")
            self.conn = None
            self.cur = None
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.conn = None
            self.cur = None

    def execute_script(self, script_path):
        """Execute a SQL script from a file."""
        if not self.conn:
            raise Exception("Not connected to the database.")
        try:
            with open(script_path, "r") as file:
                sql_script = file.read()
            self.cur.execute(sql_script)
            self.conn.commit()
            print(f"SQL script '{script_path}' executed successfully.")
        except Exception as e:
            print(f"Error executing script '{script_path}': {e}")

    def query(self, query, params=None):
        """Execute a single query."""
        if not self.conn:
            raise Exception("Not connected to the database.")
        try:
            self.cur.execute(query, params)
        except Exception as e:
            print(f"Error executing query: {e}")

    def commit(self):
        """Commit queries."""
        if not self.conn:
            raise Exception("Not connected to the database.")
        try:
            self.conn.commit()
        except Exception as e:
            print(f"Error commiting: {e}")

    def rollback(self):
        """Rollback queries."""
        if not self.connection:
            raise Exception("Not connected to the database.")
        try:
            self.conn.rollback()
        except Exception as e:
            print(f"Error rollbacking: {e}")

    def fetch_one(self, query, params=None):
        """Fetch all results from a query."""
        if not self.conn:
            raise Exception("Not connected to the database.")
        try:
            self.cur.execute(query, params)
            return self.cur.fetchone()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def close(self):
        """Close the cursor and connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Connection closed.")
