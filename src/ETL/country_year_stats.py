import mysql.connector
from database.db_config import DB_CONFIG

def process_country_year_stats():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT DISTINCT 
        home_team_id as country_id,
        year
    FROM matches
    UNION
    SELECT DISTINCT 
        away_team_id as country_id,
        year
    FROM matches
    ORDER BY year, country_id
    """)
    
    country_years = cursor.fetchall()
    
    for country_id, year in country_years:
        cursor.execute("""
        SELECT
            COUNT(*) as home_matches,
            SUM(CASE 
                WHEN home_score > away_score THEN 1 
                WHEN home_score = away_score AND s.winner_id = home_team_id THEN 1
                ELSE 0 
            END) as home_wins,
            SUM(CASE 
                WHEN home_score = away_score AND s.winner_id IS NULL THEN 1 
                ELSE 0 
            END) as home_draws,
            SUM(CASE 
                WHEN home_score < away_score THEN 1 
                WHEN home_score = away_score AND s.winner_id = away_team_id THEN 1
                ELSE 0 
            END) as home_losses,
            SUM(home_score) as home_goals_for,
            SUM(away_score) as home_goals_against
        FROM matches m
        LEFT JOIN shootouts s ON m.match_id = s.match_id
        WHERE home_team_id = %s AND year = %s
        """, (country_id, year))
        
        home_stats = cursor.fetchone()
        
        cursor.execute("""
        SELECT
            COUNT(*) as away_matches,
            SUM(CASE 
                WHEN away_score > home_score THEN 1 
                WHEN away_score = home_score AND s.winner_id = away_team_id THEN 1
                ELSE 0 
            END) as away_wins,
            SUM(CASE 
                WHEN away_score = home_score AND s.winner_id IS NULL THEN 1 
                ELSE 0 
            END) as away_draws,
            SUM(CASE 
                WHEN away_score < home_score THEN 1 
                WHEN away_score = home_score AND s.winner_id = home_team_id THEN 1
                ELSE 0 
            END) as away_losses,
            SUM(away_score) as away_goals_for,
            SUM(home_score) as away_goals_against
        FROM matches m
        LEFT JOIN shootouts s ON m.match_id = s.match_id
        WHERE away_team_id = %s AND year = %s
        """, (country_id, year))
        
        away_stats = cursor.fetchone()
        
        home_matches = int(home_stats[0]) if home_stats[0] is not None else 0
        home_wins = int(home_stats[1]) if home_stats[1] is not None else 0
        home_draws = int(home_stats[2]) if home_stats[2] is not None else 0
        home_losses = int(home_stats[3]) if home_stats[3] is not None else 0
        home_goals_for = int(home_stats[4]) if home_stats[4] is not None else 0
        home_goals_against = int(home_stats[5]) if home_stats[5] is not None else 0
        
        away_matches = int(away_stats[0]) if away_stats[0] is not None else 0
        away_wins = int(away_stats[1]) if away_stats[1] is not None else 0
        away_draws = int(away_stats[2]) if away_stats[2] is not None else 0
        away_losses = int(away_stats[3]) if away_stats[3] is not None else 0
        away_goals_for = int(away_stats[4]) if away_stats[4] is not None else 0
        away_goals_against = int(away_stats[5]) if away_stats[5] is not None else 0
        
        total_matches = home_matches + away_matches
        total_wins = home_wins + away_wins
        total_draws = home_draws + away_draws
        total_losses = home_losses + away_losses
        total_goals_for = home_goals_for + away_goals_for
        total_goals_against = home_goals_against + away_goals_against
        
        cursor.execute("""
        INSERT INTO country_year_stats (
            country_id, year,
            matches_played, wins, draws, losses,
            goals_for, goals_against,
            home_matches, home_wins, home_draws, home_losses,
            away_matches, away_wins, away_draws, away_losses
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON DUPLICATE KEY UPDATE
            matches_played = VALUES(matches_played),
            wins = VALUES(wins),
            draws = VALUES(draws),
            losses = VALUES(losses),
            goals_for = VALUES(goals_for),
            goals_against = VALUES(goals_against),
            home_matches = VALUES(home_matches),
            home_wins = VALUES(home_wins),
            home_draws = VALUES(home_draws),
            home_losses = VALUES(home_losses),
            away_matches = VALUES(away_matches),
            away_wins = VALUES(away_wins),
            away_draws = VALUES(away_draws),
            away_losses = VALUES(away_losses)
        """, (
            country_id, year,
            total_matches, total_wins, total_draws, total_losses,
            total_goals_for, total_goals_against,
            home_matches, home_wins, home_draws, home_losses,
            away_matches, away_wins, away_draws, away_losses
        ))

    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM country_year_stats")
    total_stats = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT country_id) FROM country_year_stats")
    total_countries = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT year) FROM country_year_stats")
    total_years = cursor.fetchone()[0]
    
    print(f"total entries = {total_stats}")
    print(f"total countries = {total_countries}")
    print(f"total years = {total_years}")
    
    cursor.close()
    conn.close()

def main():
    
    print("Starting country year stats ETL")
    
    process_country_year_stats()
    
    print("Finished country year stats ETL successfully")

if __name__ == "__main__":
    main()