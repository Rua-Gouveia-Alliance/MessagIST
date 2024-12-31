import logging
import psycopg
from psycopg import sql
from psycopg import OperationalError


# TODO: É preciso rever o codigo dos managers e dar rolback se operacoes nao forem bem sucedidas
class DatabaseClass:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.cur = None

    def connect(self):
        try:
            # connect to the default 'postgres' database to check/create the database
            conn = psycopg.connect(
                dbname="postgres",
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                autocommit=True,
                sslmode="require",
            )
            cur = conn.cursor()

            # check if the database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.dbname,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.dbname))
                )
                logging.debug(f"Database '{self.dbname}' created successfully.")
            else:
                logging.debug(f"Database '{self.dbname}' already exists.")

            cur.close()
            conn.close()

            # connect to the actual db
            self.conn = psycopg.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                sslmode="require",
            )
            self.cur = self.conn.cursor()
            logging.debug(f"Connected to {self.dbname} database.")
            return True
        except Exception as e:
            logging.error(f"Error: {e}")
            self.conn, self.cur = None, None
            return False

    def execute_script(self, script_path):
        if not self.conn or not self.cur:
            logging.error("Error: Not connected to the database.")
            return False

        try:
            with open(script_path, "r") as file:
                sql_script = file.read()

            self.cur.execute(sql_script)
            self.conn.commit()

            logging.debug(f"SQL script '{script_path}' executed successfully.")
            return True
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error executing script '{script_path}': {e}")
            return False

    def query(self, query, params=None):
        if not self.conn or not self.cur:
            logging.error("Error: Not connected to the database.")
            return None

        try:
            self.cur.execute(query, params)
            if self.cur.description:
                return self.cur.fetchall()
            return None
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error executing query: {e}")
            return None

    def fetch_one(self, query, params=None):
        if not self.conn or not self.cur:
            logging.error("Error: Not connected to the database.")
            return None

        try:
            self.cur.execute(query, params)
            return self.cur.fetchone()
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error fetching data: {e}")
            return None

    def commit(self):
        if not self.conn:
            logging.error("Error: Not connected to the database.")
            return False

        try:
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error commiting: {e}")
            return False

    def rollback(self):
        if not self.conn:
            logging.error("Error: Not connected to the database.")
            return False

        try:
            self.conn.rollback()
            return True
        except Exception as e:
            logging.error(f"Error rollbacking: {e}")
            return False

    def close(self):
        if self.cur:
            self.cur.close()

        if self.conn:
            self.conn.close()

        logging.debug("Connection closed.")
