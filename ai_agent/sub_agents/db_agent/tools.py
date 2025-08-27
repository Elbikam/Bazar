import logging
import sqlite3


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_to_db() -> sqlite3.Connection:
    """Establishes a connection to the SQLite database."""
    db_path = "/home/b-elbikam/project/Nina_Bazar/db.sqlite3"
    try:
        conn = sqlite3.connect(db_path)
        logger.info("Database connection established.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None


def get_tables() -> list:
    """Retrieves the list of tables in the SQLite database."""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    result = execute_query(query)
    if result and result['state'] == 'success':
        return {'tables': [row['name'] for row in result['data']], 'state': 'success'}
    else:
        return {'tables': [], 'state': 'error'}



def get_table_info(table_name: str) -> list:
    """Retrieves the information about a specific table in the SQLite database."""
    query = f"SELECT name FROM pragma_table_info('{table_name}');"
    result = execute_query(query)
    if result and result['state'] == 'success':
        return {'columns': [row['name'] for row in result['data']], 'state': 'success'}
    else:
        return {'columns': [], 'state': 'error'}


def execute_query(sql: str) -> list:
    """Executes a SQL query on the SQLite database and returns all rows as a list of dicts.
    """
    logger.info(f"Executing query: {sql}")
    conn = connect_to_db()
    if conn is None:
        return {'data': [], 'state': 'error'}
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        # Return all rows as a list of dicts
        rows = cur.fetchall()
        conn.close()
        result = [dict(row) for row in rows]
        return {'data': result, 'state': 'success'}
    except Exception as e:
        logger.error(f"Database error: {e}")
        return {'data': [], 'state': 'error'}
