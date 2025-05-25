import csv
import mysql.connector
from database.db_config import DB_CONFIG
from ETL.country_mappings import UK_NATIONS, get_country_name

def get_existing_country_id(cursor, name, official_name=None):
    query = """
    SELECT country_id, name, official_name 
    FROM countries 
    WHERE name = %s OR official_name = %s
    """
    cursor.execute(query, (name, name))
    results = cursor.fetchall()
    
    if official_name:
        cursor.execute(query, (official_name, official_name))
        results.extend(cursor.fetchall())
    
    return results[0][0] if results else None

def insert_country(conn, country_data):
    cursor = conn.cursor()
    
    existing_id = get_existing_country_id(cursor, country_data['name'], country_data.get('official_name'))
    
    if existing_id:
        query = """
        UPDATE countries SET
            iso_code = %s,
            iso3_code = %s,
            name = %s,
            official_name = %s,
            capital = %s,
            continent = %s,
            region_name = %s,
            subregion_name = %s,
            intermediate_region_name = %s,
            status = %s,
            development_status = %s,
            area_sq_km = %s,
            population = %s
        WHERE country_id = %s
        """
    else:
        query = """
        INSERT INTO countries (
            iso_code, iso3_code, name, official_name,
            capital, continent, region_name, subregion_name,
            intermediate_region_name, status,
            development_status, area_sq_km, population
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s
        )
        """
    
    for key in country_data:
        if country_data[key] == '':
            country_data[key] = None
    
    if country_data['area_sq_km'] is not None:
        try:
            country_data['area_sq_km'] = float(country_data['area_sq_km'])
        except ValueError:
            country_data['area_sq_km'] = None
            
    if country_data['population'] is not None:
        try:
            country_data['population'] = int(country_data['population'])
        except ValueError:
            country_data['population'] = None
    
    values = [
        country_data['iso_code'],
        country_data['iso3_code'],
        country_data['name'],
        country_data['official_name'],
        country_data['capital'],
        country_data['continent'],
        country_data['region_name'],
        country_data['subregion_name'],
        country_data['intermediate_region_name'],
        country_data['status'],
        country_data['development_status'],
        country_data['area_sq_km'],
        country_data['population']
    ]
    
    if existing_id:
        values.append(existing_id)
        
    cursor.execute(query, tuple(values))
    
    last_id = existing_id if existing_id else cursor.lastrowid
    
    if cursor:
        cursor.close()
    return last_id

def process_countries_csv(conn, filepath):
    with open(filepath, 'r', encoding='latin1') as file:
        csv_reader = csv.DictReader(file)
        total_rows = 0
        successful_inserts = 0
        
        conn.start_transaction()
        
        for row in csv_reader:
            total_rows += 1
            
            country_data = {}
            for csv_key, db_key in {
                'ISO': 'iso_code',
                'ISO3': 'iso3_code',
                'Display_Name': 'name',
                'Official_Name': 'official_name',
                'Capital': 'capital',
                'Continent': 'continent',
                'Region Name': 'region_name',
                'Sub-region Name': 'subregion_name',
                'Intermediate Region Name': 'intermediate_region_name',
                'Status': 'status',
                'Developed or Developing': 'development_status',
                'Area_SqKm': 'area_sq_km',
                'Population': 'population'
            }.items():
                if row[csv_key] == '#N/A':
                    country_data[db_key] = None
                else:
                    if db_key in ['name', 'official_name']:
                        country_data[db_key] = get_country_name(row[csv_key])
                    else:
                        country_data[db_key] = row[csv_key]
            
            country_id = insert_country(conn, country_data)
            if country_id:
                successful_inserts += 1
        
        conn.commit()
        
        print(f"total rows = {total_rows}")
        print(f"inserted successfully = {successful_inserts}")
        print(f"failed = {total_rows - successful_inserts}")

def load_countries(db_config):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    failed_countries = set()
    
    for nation in UK_NATIONS:
        standardized_nation = get_country_name(nation)
        try:
            cursor.execute("""
                INSERT INTO countries (iso_code, iso3_code, name, official_name)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    iso3_code = VALUES(iso3_code),
                    name = VALUES(name),
                    official_name = VALUES(official_name)
            """, ('GB', 'GBR', standardized_nation, standardized_nation))
            conn.commit()
        except mysql.connector.Error as e:
            print(f"Error inserting UK nation {nation}: {e}")
            failed_countries.add(nation)
    
    special_countries = [
        ('CN', 'CHN', 'China PR', 'China', "People's Republic of China"),
        ('CZ', 'CZE', 'Czechia', 'Czech Republic', 'Czech Republic'),
        ('MK', 'MKD', 'North Macedonia', 'Republic of North Macedonia', 'Republic of North Macedonia'),
        ('CD', 'COD', 'DR Congo', 'Democratic Republic of the Congo', 'Democratic Republic of the Congo'),
        ('IE', 'IRL', 'Republic of Ireland', 'Ireland', 'Republic of Ireland')
    ]
    
    for iso, iso3, name, official, full in special_countries:
        standardized_name = get_country_name(name)
        standardized_full = get_country_name(full)
        
        try:
            existing_id = get_existing_country_id(cursor, standardized_name, standardized_full)
            
            if existing_id:
                cursor.execute("""
                    UPDATE countries 
                    SET iso_code = %s,
                        iso3_code = %s,
                        name = %s,
                        official_name = %s
                    WHERE country_id = %s
                """, (iso, iso3, standardized_name, standardized_full, existing_id))
            else:
                cursor.execute("""
                    INSERT INTO countries (iso_code, iso3_code, name, official_name)
                    VALUES (%s, %s, %s, %s)
                """, (iso, iso3, standardized_name, standardized_full))
            
            conn.commit()
        except mysql.connector.Error as e:
            print(f"Error handling special country {name}: {e}")
            failed_countries.add(name)
    
    if cursor:
        cursor.close()
    conn.close()

def main():
    print("Starting countries ETL")
    
    con = mysql.connector.connect(**DB_CONFIG)
        
    if not con:
        print("Failed to connect to the database")
        exit(-1)
    
    csv_path = 'data/countries.csv'
    
    process_countries_csv(con, csv_path)
    
    load_countries(DB_CONFIG)
    
    print("Finished countries ETL successfully")
    con.close()

if __name__ == "__main__":
    main()