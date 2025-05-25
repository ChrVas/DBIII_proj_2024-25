import csv
import mysql.connector
from datetime import datetime
from database.db_config import DB_CONFIG
from ETL.country_mappings import get_country_name

def get_player_id(cursor, player_name):
    cursor.execute(
        "SELECT player_id FROM players WHERE name = %s", 
        (player_name,)
    )
    result = cursor.fetchone()
    return result[0] if result else None

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

def process_goals(goalscorers_csv):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    country_ids = get_country_ids(cursor)
    
    with open(goalscorers_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        goals_data = []
        
        for row in reader:
            scorer = row.get('scorer', '').strip()
            team = get_country_name(row.get('team', '').strip())
            date_str = row.get('date', '')
            home_team = get_country_name(row.get('home_team', '').strip())
            away_team = get_country_name(row.get('away_team', '').strip())
            
            if not all([scorer, team, date_str, home_team, away_team]):
                continue
            
            player_id = get_player_id(cursor, scorer)
            team_id = country_ids.get(team)
            home_team_id = country_ids.get(home_team)
            away_team_id = country_ids.get(away_team)
            
            if not all([player_id, team_id, home_team_id, away_team_id]):
                continue
            
            match_id = get_match_id(cursor, date_str, home_team_id, away_team_id)
            if not match_id:
                continue
            
            year = datetime.strptime(date_str, '%Y-%m-%d').year
            penalty = row.get('penalty', '').lower() == 'true'
            own_goal = row.get('own_goal', '').lower() == 'true'
            
            goals_data.append((
                match_id,
                player_id,
                team_id,
                year,
                own_goal,
                penalty
            ))
        
        if goals_data:
            cursor.executemany("""
                INSERT INTO goals (
                    match_id, player_id, team_id, year,
                    own_goal, penalty
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
            """, goals_data)
            
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM goals")
            total_goals = cursor.fetchone()[0]
            
            print(f"total goals in database = {total_goals}")
    
    cursor.close()
    conn.close()

def main():
    print("Starting goals ETL")
    
    goalscorers_csv = 'data/goalscorers.csv'
    
    process_goals(goalscorers_csv)
    
    print("Finished goals ETL successfully")

if __name__ == "__main__":
    main()