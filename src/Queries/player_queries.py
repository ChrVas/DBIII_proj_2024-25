import mysql.connector
from database.db_config import DB_CONFIG

def get_players():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    query = """
    SELECT name 
    FROM players 
    ORDER BY name
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in result]

def get_career_stats(player_name):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        MIN(p.first_appearance_year) as start_year,
        MAX(p.last_appearance_year) as end_year,
        p.total_goals,
        p.max_goals_in_match
    FROM players p
    WHERE p.name = %s
    GROUP BY p.player_id, p.total_goals, p.max_goals_in_match
    """
    
    cursor.execute(query, (player_name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def get_player_and_team_stats(player_name):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        pys.year,
        pys.goals as player_goals,
        ROUND(CAST(cys.goals_for AS FLOAT) / NULLIF(cys.matches_played, 0), 2) as team_goals_per_match
    FROM players p
    JOIN player_year_stats pys ON p.player_id = pys.player_id
    JOIN countries c ON pys.country_id = c.country_id
    JOIN country_year_stats cys ON c.country_id = cys.country_id AND pys.year = cys.year
    WHERE p.name = %s
    ORDER BY pys.year
    """
    
    cursor.execute(query, (player_name,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_team_scoring_stats(team_name, start_year, end_year):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        cys.year,
        ROUND(CAST(cys.goals_for AS FLOAT) / NULLIF(cys.matches_played, 0), 2) as avg_goals_per_match
    FROM countries c
    JOIN country_year_stats cys ON c.country_id = cys.country_id
    WHERE c.name = %s
    AND cys.year BETWEEN %s AND %s
    GROUP BY cys.year, cys.goals_for, cys.matches_played
    ORDER BY cys.year
    """
    
    cursor.execute(query, (team_name, start_year, end_year))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result