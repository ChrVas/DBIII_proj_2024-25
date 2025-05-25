from database.db_config import DB_CONFIG
import mysql.connector

def get_yr_stats():
    cn = mysql.connector.connect(**DB_CONFIG)
    cur = cn.cursor()
    
    qry = """
    SELECT 
        year_id as year,
        total_matches,
        total_draws,
        total_penalty_shootouts
    FROM years
    ORDER BY year_id;
    """
    
    cur.execute(qry)
    res = cur.fetchall()
    cur.close()
    cn.close()
    return res

def get_ctry_yr_stats(yr):
    cn = mysql.connector.connect(**DB_CONFIG)
    cur = cn.cursor()
    
    qry = """
    SELECT 
        c.name as country_name,
        c.region_name,
        c.development_status as status,
        cys.matches_played as total_matches,
        cys.wins,
        cys.losses,
        cys.draws
    FROM country_year_stats cys
    JOIN countries c ON c.country_id = cys.country_id
    WHERE cys.year = %s
    ORDER BY cys.matches_played DESC;
    """
    
    cur.execute(qry, (yr,))
    res = cur.fetchall()
    cur.close()
    cn.close()
    return res

def get_dist_rgns():
    cn = mysql.connector.connect(**DB_CONFIG)
    cur = cn.cursor()
    
    qry = """
    SELECT DISTINCT region_name 
    FROM countries 
    WHERE region_name IS NOT NULL 
    ORDER BY region_name;
    """
    
    cur.execute(qry)
    res = cur.fetchall()
    cur.close()
    cn.close()
    return [r[0] for r in res]