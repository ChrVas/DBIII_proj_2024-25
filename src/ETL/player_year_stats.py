import mysql.connector
from database.db_config import DB_CONFIG

def process_player_year_stats():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT DISTINCT 
        g.player_id,
        g.team_id as country_id,
        g.year
    FROM goals g
    ORDER BY g.year, g.player_id, g.team_id
    """)
    
    player_combinations = cursor.fetchall()
    
    for player_id, country_id, year in player_combinations:
        cursor.execute("""
        SELECT
            COUNT(*) as total_goals,
            COUNT(DISTINCT match_id) as matches_with_goals,
            SUM(CASE WHEN penalty = 1 THEN 1 ELSE 0 END) as penalties,
            SUM(CASE WHEN own_goal = 1 THEN 1 ELSE 0 END) as own_goals
        FROM goals 
        WHERE player_id = %s 
        AND team_id = %s 
        AND year = %s
        """, (player_id, country_id, year))
        
        stats = cursor.fetchone()
        
        total_goals = int(stats[0]) if stats[0] is not None else 0
        matches_with_goals = int(stats[1]) if stats[1] is not None else 0
        penalties = int(stats[2]) if stats[2] is not None else 0
        own_goals = int(stats[3]) if stats[3] is not None else 0
        
        cursor.execute("""
        INSERT INTO player_year_stats (
            player_id, country_id, year,
            goals, matches_with_goals, penalties, own_goals
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
        ) ON DUPLICATE KEY UPDATE
            goals = VALUES(goals),
            matches_with_goals = VALUES(matches_with_goals),
            penalties = VALUES(penalties),
            own_goals = VALUES(own_goals)
        """, (
            player_id, country_id, year,
            total_goals, matches_with_goals, penalties, own_goals
        ))

    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM player_year_stats")
    total_stats = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_year_stats")
    total_players = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT year) FROM player_year_stats")
    total_years = cursor.fetchone()[0]
    
    print(f"total entries = {total_stats}")
    print(f"total players = {total_players}")
    print(f"total years = {total_years}")
    
    cursor.close()
    conn.close()

def main():
    
    print("Starting player year stats ETL")
    
    process_player_year_stats()
    
    print("Finished player year stats ETL successfully")

if __name__ == "__main__":
    main()