import mysql.connector
from database.db_config import DB_CONFIG

def get_ctry_yr_rng(ctry_nm):
    cn = mysql.connector.connect(**DB_CONFIG)
    cur = cn.cursor()
    cur.execute("""
        SELECT MIN(year), MAX(year)
        FROM country_year_stats cys
        JOIN countries c ON c.country_id = cys.country_id
        WHERE c.name = %s
    """, (ctry_nm,))
    min_yr, max_yr = cur.fetchone()
    cur.close()
    cn.close()
    return {'min_year': min_yr, 'max_year': max_yr}

def get_ctry_stats(ctry_nm, st_yr=None, end_yr=None):
    cn = mysql.connector.connect(**DB_CONFIG)
    cur = cn.cursor()
    
    qry = """
        SELECT cys.year,cys.matches_played, cys.wins, cys.losses, cys.draws, cys.home_matches, cys.home_wins, cys.home_losses, cys.away_matches, cys.away_wins, cys.away_losses
        FROM country_year_stats cys
        JOIN countries c ON c.country_id = cys.country_id
        WHERE c.name = %s
    """
    prms = [ctry_nm]
    
    if st_yr and end_yr:
        qry += " AND cys.year BETWEEN %s AND %s"
        prms.extend([st_yr, end_yr])
    
    qry += " ORDER BY cys.year"
    
    cur.execute(qry, prms)
    res = cur.fetchall()
    cur.close()
    cn.close()
    return res

def get_all_ctry():
    cn = mysql.connector.connect(**DB_CONFIG)
    cur = cn.cursor()
    cur.execute("SELECT name FROM countries ORDER BY name")
    ctries = [row[0] for row in cur.fetchall()]
    cur.close()
    cn.close()
    return ctries

def get_ctry_yr_info(ctry_nm):
    cn = mysql.connector.connect(**DB_CONFIG)
    cur = cn.cursor()
    cur.execute("""
        SELECT 
            MIN(cys.year) as first_year,
            MAX(cys.year) as last_year,
            COUNT(DISTINCT cys.year) as total_years,
            SUM(cys.matches_played) as total_matches,
            SUM(cys.wins) as total_wins,
            SUM(cys.losses) as total_losses,
            SUM(cys.home_matches) as total_home_matches,
            SUM(cys.home_wins) as total_home_wins,
            SUM(cys.home_losses) as total_home_losses,
            SUM(cys.away_matches) as total_away_matches,
            SUM(cys.away_wins) as total_away_wins,
            SUM(cys.away_losses) as total_away_losses
        FROM country_year_stats cys
        JOIN countries c ON c.country_id = cys.country_id
        WHERE c.name = %s
    """, (ctry_nm,))
    res = cur.fetchone()
    cur.close()
    cn.close()
    return {
        'first_year': res[0],
        'last_year': res[1],
        'total_years': res[2],
        'total_matches': res[3],
        'total_wins': res[4],
        'total_losses': res[5],
        'total_home_matches': res[6],
        'total_home_wins': res[7],
        'total_home_losses': res[8],
        'total_away_matches': res[9],
        'total_away_wins': res[10],
        'total_away_losses': res[11]
    }

def get_ctry_yrly_stats(ctry_nm):
    cn = mysql.connector.connect(**DB_CONFIG)
    cur = cn.cursor()
    cur.execute("""
        SELECT 
            cys.year,
            cys.matches_played,
            cys.wins,
            cys.losses,
            cys.draws
        FROM country_year_stats cys
        JOIN countries c ON c.country_id = cys.country_id
        WHERE c.name = %s
        ORDER BY cys.year
    """, (ctry_nm,))
    res = cur.fetchall()
    cur.close()
    cn.close()
    
    yrs = [row[0] for row in res]
    mtchs = [row[1] for row in res]
    wns = [row[2] for row in res]
    lsss = [row[3] for row in res]
    drws = [row[4] for row in res]
    
    return {
        'years': yrs,
        'matches': mtchs,
        'wins': wns,
        'losses': lsss,
        'draws': drws
    }