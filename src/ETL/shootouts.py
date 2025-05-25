import csv
import mysql.connector
from database.db_config import DB_CONFIG
from ETL.country_mappings import get_country_name

def get_match_id(cursor, date, home_team_id, away_team_id):
        query = """
        SELECT match_id 
        FROM matches 
        WHERE date = %s 
        AND home_team_id = %s 
        AND away_team_id = %s
        """
        cursor.execute(query, (date, home_team_id, away_team_id))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            None

def get_country_ids(cursor):
    country_ids = {}
    
    cursor.execute("SELECT country_id, name, official_name FROM countries")
    for country_id, name, official_name in cursor.fetchall():
        standardized_name = get_country_name(name)
        country_ids[standardized_name] = country_id
        if official_name:
            standardized_official = get_country_name(official_name)
            country_ids[standardized_official] = country_id
    
    cursor.execute("""
        SELECT fcn.former_name, c.country_id 
        FROM former_country_names fcn
        JOIN countries c ON fcn.country_id = c.country_id
    """)
    for former_name, country_id in cursor.fetchall():
        standardized_former = get_country_name(former_name)
        country_ids[standardized_former] = country_id
    
    return country_ids

def main():
    shootouts_csv = 'data/shootouts.csv'
    
    print("Starting shootouts ETL")
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    country_ids = get_country_ids(cursor)
    
    with open(shootouts_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        shootouts_data = []
        skipped_shootouts = 0
        
        for row in reader:
            date_str = row.get('date', '').strip()
            home_team = get_country_name(row.get('home_team', '').strip())
            away_team = get_country_name(row.get('away_team', '').strip())
            winner = get_country_name(row.get('winner', '').strip())
            first_shooter = get_country_name(row.get('first_shooter', '').strip())
            
            if not all([date_str, home_team, away_team, winner]):
                continue
            
            home_team_id = country_ids.get(home_team)
            away_team_id = country_ids.get(away_team)
            winner_id = country_ids.get(winner)
            first_shooter_id = country_ids.get(first_shooter) if first_shooter else None
            
            if not all([home_team_id, away_team_id, winner_id]):
                skipped_shootouts += 1
                continue
            
            cursor.execute("""
                SELECT match_id 
                FROM matches 
                WHERE date = %s AND home_team_id = %s AND away_team_id = %s
            """, (date_str, home_team_id, away_team_id))
            
            match = cursor.fetchone()
            if not match:
                skipped_shootouts += 1
                continue
                
            match_id = match[0]
            
            cursor.execute("""
                INSERT INTO shootouts 
                    (match_id, winner_id, first_shooter_id)
                VALUES
                    (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    winner_id = VALUES(winner_id),
                    first_shooter_id = VALUES(first_shooter_id)
            """, (match_id, winner_id, first_shooter_id))
            
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM shootouts")
        total_shootouts = cursor.fetchone()[0]
        
        print(f"total shootouts in database = {total_shootouts}")
        print(f"skipped shootouts = {skipped_shootouts}")
    
    cursor.close()
    conn.close()
    
    print("Finished shootouts ETL successfully")

if __name__ == "__main__":
    main()