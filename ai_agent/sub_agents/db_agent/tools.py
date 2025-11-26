import logging
import sqlite3
import json 
from django.apps import apps

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
    all_models = apps.get_models()
    table_names = [model._meta.db_table for model in all_models]
    return table_names



def get_table_info(table_name: str) -> list:
    """Retrieves the information about a specific table in the SQLite database."""
    query = f"SELECT name FROM pragma_table_info('{table_name}');"
    result = execute_query(query)
    data = result['data']
    details = []
    for i in data:
        details.append(i['name'])
    return details 





def execute_query(sql: str) -> dict:
    """
    Executes a SINGLE, read-only SQL query on the database.
    Args:
        sql (str): The SQL SELECT query string to be executed.
    Return :
        dict: A dictionary with one of the following structures:
            - On success: {'state': 'success', 'data': [dict_row1, dict_row2, ...]}
            - On failure: {'state': 'error', 'message': 'A description of the error.'}
    """
    logger.info(f"Executing query: {sql}")
    conn = connect_to_db()
    if conn is None:
        return {'data': [], 'status': 'error'}
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        # Return all rows as a list of dicts
        rows = cur.fetchall()
        conn.close()
        result = [dict(row) for row in rows]
        return {"status": "success","data":result}
    except Exception as e:
        logger.error(f"Database error: {e}")
        return {"data": [], "status": "error"}
