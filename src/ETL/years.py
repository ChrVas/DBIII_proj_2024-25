import csv
import mysql.connector
from datetime import datetime
from database.db_config import DB_CONFIG


def extract_years_from_results(results_csv, shootouts_csv):
    years = {}
    shootout_matches = set()
    
    with open(shootouts_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_str = row.get('date', '').strip()
            home_team = row.get('home_team', '').strip()
            away_team = row.get('away_team', '').strip()
            if date_str and home_team and away_team:
                shootout_matches.add((date_str, home_team, away_team))
    
    with open(results_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_str = row.get('date', '')
            if date_str:
                year = datetime.strptime(date_str, '%Y-%m-%d').year
                
                if year not in years:
                    years[year] = {
                        'total_matches': 0,
                        'total_draws': 0,
                        'total_penalty_shootouts': 0,
                        'total_goals': 0
                    }
                
                years[year]['total_matches'] += 1
                
                home_score = int(row.get('home_score', 0))
                away_score = int(row.get('away_score', 0))
                
                match_key = (row.get('date', '').strip(), 
                           row.get('home_team', '').strip(), 
                           row.get('away_team', '').strip())
                
                if home_score == away_score and match_key not in shootout_matches:
                    years[year]['total_draws'] += 1
                
                if match_key in shootout_matches:
                    years[year]['total_penalty_shootouts'] += 1
                
                years[year]['total_goals'] += home_score + away_score
                    
    return years

def update_goal_stats(goalscorers_csv, year_stats):
    with open(goalscorers_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        goal_count_by_year = {}
        for row in reader:
            date_str = row.get('date', '')
            if date_str and row.get('scorer', '').strip():
                try:
                    year = datetime.strptime(date_str, '%Y-%m-%d').year
                    if year not in goal_count_by_year:
                        goal_count_by_year[year] = 0
                    goal_count_by_year[year] += 1
                except ValueError:
                    pass
        
def load_years(year_stats, db_config):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO years 
        (year_id, total_matches, total_draws, total_penalty_shootouts, total_goals) 
    VALUES 
        (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        total_matches = VALUES(total_matches),
        total_draws = VALUES(total_draws),
        total_penalty_shootouts = VALUES(total_penalty_shootouts),
        total_goals = VALUES(total_goals)
    """
    
    year_data = []
    for year, stats in sorted(year_stats.items()):
        year_data.append((
            year,
            stats['total_matches'],
            stats['total_draws'],
            stats['total_penalty_shootouts'],
            stats['total_goals']
        ))
    
    cursor.executemany(insert_query, year_data)
    
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM years")
    count = cursor.fetchone()[0]
    print(f"total years = {count}")
    
    cursor.close()
    conn.close()

def main():
    print(f"Starting years ETL")
    
    results_csv = 'data/results.csv'
    shootouts_csv = 'data/shootouts.csv'
    goalscorers_csv = 'data/goalscorers.csv'
    
    year_stats = extract_years_from_results(results_csv, shootouts_csv)
    
    update_goal_stats(goalscorers_csv, year_stats)
    
    load_years(year_stats, DB_CONFIG)
    
    print(f"Finished years ETL successfully")


if __name__ == "__main__":
    main()