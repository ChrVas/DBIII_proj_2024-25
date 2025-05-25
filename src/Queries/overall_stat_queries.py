import mysql.connector
from database.db_config import DB_CONFIG

def country_scores():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = """
    SELECT 
        c.name,
        SUM(cys.wins) as total_wins,
        c.population
    FROM countries c
    JOIN country_year_stats cys ON c.country_id = cys.country_id
    WHERE c.population IS NOT NULL
    GROUP BY c.country_id, c.name, c.population
    ORDER BY total_wins DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def top_10(category):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    categories = {
        'wins': 'SUM(cys.wins)',
        'score': 'SUM(cys.wins * 3 + cys.draws)',
        'wins_per_year': 'SUM(cys.wins) / COUNT(DISTINCT cys.year)',
        'score_per_year': 'SUM(cys.wins * 3 + cys.draws) / COUNT(DISTINCT cys.year)'
    }
    query = f"""
    SELECT 
        c.name,
        {categories[category]} as value
    FROM countries c
    JOIN country_year_stats cys ON c.country_id = cys.country_id
    GROUP BY c.country_id, c.name
    ORDER BY value DESC
    LIMIT 10
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results