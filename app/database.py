# app/database.py
import os
import psycopg
from psycopg.rows import dict_row

# Get the database connection string from Docker's environment variables
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://kom_way_admin:kjkj@localhost:5433/kom_way_db_dev"
)

def get_db_connection():
    """
    Creates a raw connection to the PostgreSQL database.
    Using dict_row means query results come back as clean Python dictionaries 
    instead of flat tuples (e.g., {'user_id': 1} instead of just (1,)).
    """
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def insert_api_log(time_local, status, ip, duration_ms, latitude, longitude, ws, temp):
    """Inserts a request log entry into the database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO api_logs (time_local, status, ip, duration_ms, latitude, longitude, ws, temp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (time_local, status, ip, duration_ms, latitude, longitude, ws, temp))
            conn.commit()

def get_api_logs(days: int = 30):
    """Retrieves API logs from the database within the specified history limit (in days)."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, time_local, status, ip, duration_ms, latitude, longitude, ws, temp, created_at
                FROM api_logs
                WHERE created_at >= NOW() - INTERVAL '1 day' * %s
                ORDER BY created_at DESC;
            """, (days,))
            return cur.fetchall()

def execute_query(query: str, params: tuple = None, fetch: str = "all"):
    """Generic helper to execute any SQL query."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch == "all":
                return cur.fetchall()
            elif fetch == "one":
                return cur.fetchone()
            elif fetch == "commit":
                conn.commit()
                return None
            return cur

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
