# app/database.py
import os
import psycopg
from psycopg.rows import dict_row

# Get the database connection string from Docker's environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """
    Creates a raw connection to the PostgreSQL database.
    Using dict_row means query results come back as clean Python dictionaries 
    instead of flat tuples (e.g., {'user_id': 1} instead of just (1,)).
    """
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def test_db_connection():
    """
    A simple test query to verify Python can talk to Postgres 
    and that the PostGIS extension is active.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Query the PostGIS version to verify the extension is working
                cur.execute("SELECT PostGIS_Full_Version();")
                version = cur.fetchone()
                return {"status": "success", "postgis_version": version["postgis_full_version"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
