import pyodbc
import logging
from data_operations_helpers import fetch_data_with_params, fetch_columns, fetch_data, parse_db_config

# önce ojdt sonra jdt1 tabloları transfer ediyor, dikkat ettiğimiz nokta var olan verileri tekrar eklememesi ve verileri silmemesi
# Setup basic configuration for logging
logging.basicConfig(filename='database_update.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def check_and_update_ocrd(entries_source, entries_target):
    source_config, target_config = parse_db_config(
        entries_source, entries_target)
    excluded_columns = [
        "Balance", "ChecksBal", "DNotesBal", "OrdersBal", "CreditLine",
        "DebtLine", "Discount", "DdctPrcnt", "DNoteBalFc", "OrderBalFC",
        "DNoteBalSy", "OrderBalSy", "IntrstRate", "Commission", "BalanceSys",
        "BalanceFC", "MinIntrst", "ChecksBalL", "ChecksBalS"
    ]

    try:
        with pyodbc.connect(**source_config) as source_conn, pyodbc.connect(**target_config) as target_conn:
            source_columns = fetch_columns(source_conn, 'OCRD')
            target_columns = fetch_columns(target_conn, 'OCRD')

            # Filter out excluded columns, ensure column exists in target, and remove CardCode to handle it separately
            columns_to_copy = [
                col for col in source_columns if col not in excluded_columns and col in target_columns and col != 'CardCode']

            # Prepare query to fetch data from source excluding certain financial columns
            query = f"SELECT CardCode, {', '.join(columns_to_copy)} FROM OCRD"
            source_data, _ = fetch_data(source_conn, query)

            cursor = target_conn.cursor()
            for row in source_data:
                card_code = row[0]
                cursor.execute(
                    "SELECT CardCode FROM OCRD WHERE CardCode = ?", (card_code,))
                if cursor.fetchone() is None:
                    # CardCode not found in target, proceed to insert
                    # Exclude CardCode from data to be inserted
                    data_to_insert = row[1:]
                    placeholders = ', '.join(['?' for _ in columns_to_copy])
                    sql_insert = f"INSERT INTO OCRD (CardCode, {', '.join(
                        columns_to_copy)}) VALUES (?, {placeholders})"
                    cursor.execute(sql_insert, (card_code, *data_to_insert))
            target_conn.commit()
    except Exception as e:
        logging.error(f"Error processing OCRD entries: {str(e)}")
        return False
    return True


def sync_rows(entries_source, entries_target, column_name, column_value, target_column_name):
    source_config, target_config = parse_db_config(
        entries_source, entries_target)

    try:
        with pyodbc.connect(**source_config) as source_conn, pyodbc.connect(**target_config) as target_conn:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()

            source_columns = fetch_columns(source_conn, 'OJDT')
            target_columns = fetch_columns(target_conn, 'OJDT')
            common_columns = [
                col for col in source_columns if col in target_columns]

            source_query = f"SELECT * FROM OJDT WHERE {column_name} = ?"
            param = int(column_value) if column_name in [
                'TransId', 'Number'] else column_value
            source_rows, column_names = fetch_data_with_params(
                source_conn, source_query, (param,))

            for row in source_rows:
                transId = row[column_names.index('TransId')]

                target_query = f"SELECT {target_column_name} FROM OJDT WHERE {
                    target_column_name} = ?"
                target_cursor.execute(target_query, (transId,))
                result = target_cursor.fetchone()

                if not result:
                    target_cursor.execute("SELECT MAX(TransId) FROM OJDT")
                    max_transId = (target_cursor.fetchone()[0] or 0) + 1

                    insert_values = [row[column_names.index(
                        col)] if col != 'TransId' and col != 'Number' else max_transId for col in common_columns]
                    # Burada orijinal transId'yi hedef sütuna ekliyoruz.
                    insert_values[common_columns.index(
                        target_column_name)] = transId

                    insert_query = f"INSERT INTO OJDT ({', '.join(common_columns)}) VALUES ({
                        ', '.join(['?' for _ in common_columns])})"

                    target_cursor.execute(insert_query, insert_values)
                    target_conn.commit()
            return True
    except Exception as e:
        return False

def update_target_jdt1(entries_source, entries_target, target_column_name):
    source_config, target_config = parse_db_config(entries_source, entries_target)

    try:
        with pyodbc.connect(**source_config) as source_conn, pyodbc.connect(**target_config) as target_conn:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()

            # Fetch all TransId values and their corresponding original TransId from the target database OJDT table
            target_query = f"SELECT TransId, {target_column_name} FROM OJDT"
            target_cursor.execute(target_query)
            transId_map = {row[1]: row[0] for row in target_cursor.fetchall()}

            source_columns = fetch_columns(source_conn, 'JDT1')
            target_columns = fetch_columns(target_conn, 'JDT1')

            common_columns = [col for col in source_columns if col in target_columns]
            column_indices = [source_columns.index(col) for col in common_columns]

            for original_transId in transId_map:
                # Fetch data from the source JDT1 table for the given original TransId
                source_query = f"SELECT {', '.join(common_columns)} FROM JDT1 WHERE TransId = ?"
                source_cursor.execute(source_query, (original_transId,))
                source_jdt1_data = source_cursor.fetchall()

                if source_jdt1_data:
                    # Update the TransId in source data to match the target TransId
                    updated_source_data = []
                    for data in source_jdt1_data:
                        data = list(data)
                        transId_idx = source_columns.index('TransId')  # Assuming 'TransId' is a column in source_columns
                        data[transId_idx] = transId_map[original_transId]
                        updated_source_data.append(data)

                    # Delete existing records in the target JDT1 table for the new TransId
                    delete_query = f"DELETE FROM JDT1 WHERE TransId = ?"
                    target_cursor.execute(delete_query, (transId_map[original_transId],))

                    # Insert updated records into the target JDT1 table
                    insert_query = f"INSERT INTO JDT1 ({', '.join(common_columns)}) VALUES ({', '.join(['?' for _ in common_columns])})"
                    for data in updated_source_data:
                        target_cursor.execute(insert_query, data)

            target_conn.commit()
            return True

    except Exception as e:
        print(f"Error updating target JDT1 table: {str(e)}")
        return False


def account_plan_transfer_and_exclude_balances(entries_source, entries_target):
    try:
        # Parse database configurations for source and target
        source_config, target_config = parse_db_config(entries_source, entries_target)
        
        # Connect to source database and fetch data
        with pyodbc.connect(**source_config) as source_conn:
            source_data, columns = fetch_data(source_conn, "SELECT * FROM OACT")
            # Convert each pyodbc.Row to a dictionary manually
            data_dicts = [{columns[i]: value for i, value in enumerate(row)} for row in source_data]

        # Exclude certain columns from data
        filtered_data = [
            {key: value for key, value in record.items() if key not in ['CurrTotal', 'SysTotal', 'FcTotal']}
            for record in data_dicts
        ]

        # Connect to target database, clear existing data and insert new data
        with pyodbc.connect(**target_config) as target_conn:
            target_cursor = target_conn.cursor()
            target_cursor.execute("DELETE FROM OACT")
            target_conn.commit()

            for record in filtered_data:
                placeholders = ', '.join(['?'] * len(record))
                columns = ', '.join(record.keys())
                sql = f"INSERT INTO OACT ({columns}) VALUES ({placeholders})"
                target_cursor.execute(sql, list(record.values()))
            
            target_conn.commit()

        return True

    except Exception as e:
        print(f"Error in transferring data: {str(e)}")
        return False

  
def transfer_based_on_condition(entries_source, entries_target, column_name, column_value, target_column_name):
    # Önce veri senkronizasyonunu gerçekleştir
    if not sync_rows(entries_source, entries_target, column_name, column_value, target_column_name):
        return False

    # Senkronizasyon başarılı olduktan sonra JDT1 tablosunu güncelle
    if not update_target_jdt1(entries_source, entries_target, target_column_name):
        return False

    return True

def tax_run_transfer_ovtg(entries_source, entries_target):
    source_config, target_config = parse_db_config(entries_source, entries_target)

    try:
        with pyodbc.connect(**source_config) as source_conn, pyodbc.connect(**target_config) as target_conn:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()

            source_columns = fetch_columns(source_conn, 'OVTG')
            target_columns = fetch_columns(target_conn, 'OVTG')

            common_columns = [col for col in source_columns if col in target_columns]
            column_indices = [source_columns.index(col) for col in common_columns]

            source_query = f"SELECT * FROM OVTG"
            source_rows, column_names = fetch_data(source_conn, source_query)

            for row in source_rows:
                taxCode = row[column_names.index('Code')]

                target_query = f"SELECT Code FROM OVTG WHERE Code = ?"
                target_cursor.execute(target_query, (taxCode,))
                result = target_cursor.fetchone()

                if not result:
                    insert_values = [row[column_names.index(col)] for col in common_columns]
                    insert_query = f"INSERT INTO OVTG ({', '.join(common_columns)}) VALUES ({', '.join(['?' for _ in common_columns])})"

                    target_cursor.execute(insert_query, insert_values)
                    target_conn.commit()
            return True
    except Exception as e:
        return False

def tax_run_transfer_vtg1(entries_source, entries_target):
    source_config, target_config = parse_db_config(entries_source, entries_target)

    try:
        with pyodbc.connect(**source_config) as source_conn, pyodbc.connect(**target_config) as target_conn:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()

            source_columns = fetch_columns(source_conn, 'VTG1')
            target_columns = fetch_columns(target_conn, 'VTG1')

            common_columns = [col for col in source_columns if col in target_columns]
            column_indices = [source_columns.index(col) for col in common_columns]

            source_query = f"SELECT * FROM VTG1"
            source_rows, column_names = fetch_data(source_conn, source_query)

            for row in source_rows:
                taxCode = row[column_names.index('Code')]

                target_query = f"SELECT Code FROM VTG1 WHERE Code = ?"
                target_cursor.execute(target_query, (taxCode,))
                result = target_cursor.fetchone()

                if not result:
                    insert_values = [row[column_names.index(col)] for col in common_columns]
                    insert_query = f"INSERT INTO VTG1 ({', '.join(common_columns)}) VALUES ({', '.join(['?' for _ in common_columns])})"

                    target_cursor.execute(insert_query, insert_values)
                    target_conn.commit()
            return True
    except Exception as e:
        return False
    
def tax_run_transfer(entries_source, entries_target):
    if not tax_run_transfer_ovtg(entries_source, entries_target):
        return False
    if not tax_run_transfer_vtg1(entries_source, entries_target):
        return False
    return True