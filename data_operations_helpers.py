
def fetch_data_with_params(conn, query, params):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchall(), [column[0] for column in cursor.description]
    finally:
        cursor.close()


def fetch_columns(conn, table):
    cursor = conn.cursor()
    try:
        # Returns no rows, only column info
        cursor.execute(f"SELECT * FROM {table} WHERE 1=0")
        return [column[0] for column in cursor.description]
    finally:
        cursor.close()


def fetch_data(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall(), [column[0] for column in cursor.description]
    finally:
        cursor.close()


def parse_db_config(entries_source, entries_target):
    source_config = {
        'driver': '{ODBC Driver 17 for SQL Server}',
        'server': entries_source['server'].get(),
        'database': entries_source['database'].get(),
        'user': entries_source['username'].get(),
        'password': entries_source['password'].get()
    }
    target_config = {
        'driver': '{ODBC Driver 17 for SQL Server}',
        'server': entries_target['server'].get(),
        'database': entries_target['database'].get(),
        'user': entries_target['username'].get(),
        'password': entries_target['password'].get()
    }
    return source_config, target_config
