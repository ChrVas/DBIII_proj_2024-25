import csv
import mysql.connector
from datetime import datetime
from database.db_config import DB_CONFIG
from ETL.country_mappings import get_country_name

def get_country_id(conn, country_name):
    cursor = conn.cursor()
    try:
        std_name = get_country_name(country_name)
        cursor.execute(
            "SELECT country_id FROM countries WHERE name = %s OR official_name = %s", 
            (std_name, std_name)
        )
        result = cursor.fetchall() 
        if result:
            return result[0][0]
            
        if std_name != country_name:
            cursor.execute(
                "SELECT country_id FROM countries WHERE name = %s OR official_name = %s", 
                (country_name, country_name)
            )
            result = cursor.fetchall()  
            if result:
                return result[0][0]
                
        return None
    finally:
        try:
            while cursor.fetchall():
                pass
        except:
            pass
        cursor.close()

def insert_former_name(conn, former_name_data):
    try:
        cursor = conn.cursor()
        
        query = """
        INSERT INTO former_country_names (
            former_name, current_name, country_id, start_date, end_date
        ) VALUES (
            %s, %s, %s, %s, %s
        )
        """
        
        cursor.execute(query, (
            former_name_data['former_name'],
            former_name_data['current_name'],
            former_name_data['country_id'],
            former_name_data['start_date'],
            former_name_data['end_date']
        ))
    except mysql.connector.Error as e:
        print(f"Error inserting former name {former_name_data['former_name']}: {e}")
        return 
    finally:
        if cursor:
            cursor.close()

def process_former_names_csv(conn, filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        total_rows = 0
        successful_inserts = 0
        
        conn.start_transaction()
        
        for row in csv_reader:
            total_rows += 1
            
            current_name = get_country_name(row['current'])
            country_id = get_country_id(conn, current_name)
            
            if not country_id:
                print(f"Warning: Could not find country ID for {current_name}")
                continue
                
            former_name_data = {
                'former_name': row['former'],
                'current_name': current_name,
                'country_id': country_id,
                'start_date': datetime.strptime(row['start_date'], '%Y-%m-%d').date() if row['start_date'] else None,
                'end_date': datetime.strptime(row['end_date'], '%Y-%m-%d').date() if row['end_date'] else None
            }
            
            insert_former_name(conn, former_name_data)
            successful_inserts += 1
            
        conn.commit()
        
        print(f"total rows = {total_rows}")
        print(f"inserted successfully = {successful_inserts}")
        print(f"failed = {total_rows - successful_inserts}")

def main():
    print("Starting former names ETL")
    
    conn = mysql.connector.connect(**DB_CONFIG)
    
    if not conn:
        print("Failed to connect to the database")
        exit(-1)
        
    csv_path = 'data/former_names.csv'
    process_former_names_csv(conn, csv_path)
    
    print("Finished former names ETL successfully")
    conn.close()

if __name__ == "__main__":
    main()