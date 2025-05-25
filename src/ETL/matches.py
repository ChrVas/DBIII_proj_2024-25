import csv
import mysql.connector
from datetime import datetime
from database.db_config import DB_CONFIG
from ETL.country_mappings import get_country_name


def extract_matches(results_csv):
    matches = []
    with open(results_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_str = row.get('date', '')
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    year = date_obj.year

                    match = {
                        'date': date_str,
                        'year': year,
                        'home_team': get_country_name(row.get('home_team', '').strip()),
                        'away_team': get_country_name(row.get('away_team', '').strip()),
                        'home_score': int(row.get('home_score', 0)),
                        'away_score': int(row.get('away_score', 0)),
                        'tournament': row.get('tournament', '').strip(),
                        'city': row.get('city', '').strip(),
                        'country': get_country_name(row.get('country', '').strip()),
                        'has_penalty_shootout': False
                    }

                    matches.append(match)
                except ValueError as e:
                    print(f"Warning: Invalid data in row: {row}, error: {e}")

    return matches


def populate_shootouts(shootouts_csv, matches):
    match_dict = {}
    for i, match in enumerate(matches):
        key = (match['date'], match['home_team'], match['away_team'])
        match_dict[key] = i

    with open(shootouts_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        shootout_count = 0

        for row in reader:
            date_str = row.get('date', '').strip()
            home_team = row.get('home_team', '').strip()
            away_team = row.get('away_team', '').strip()

            key = (date_str, home_team, away_team)
            if key in match_dict:
                idx = match_dict[key]
                matches[idx]['has_penalty_shootout'] = True
                shootout_count += 1


def load_matches(matches, db_config):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    country_ids = get_country_ids(cursor)

    ensure_years_exist(cursor, matches)

    match_data = []

    for match in matches:
        home_team_id = country_ids.get(match['home_team'])
        away_team_id = country_ids.get(match['away_team'])
        country_id = country_ids.get(match['country']) if match['country'] else None

        if home_team_id is None or away_team_id is None or country_id is None:
            continue

        match_data.append((
            match['date'],
            match['year'],
            home_team_id,
            away_team_id,
            match['home_score'],
            match['away_score'],
            match['city'],
            country_id,
            match['has_penalty_shootout']
        ))

    insert_query = """
    INSERT INTO matches 
        (date, year, home_team_id, away_team_id, home_score, away_score,
            city, country_id, has_penalty_shootout) 
    VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.executemany(insert_query, match_data)
    conn.commit()

    cursor.close()
    conn.close()


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

def ensure_years_exist(cursor, matches):
    years = set(match['year'] for match in matches)

    try:
        for year in years:
            cursor.execute("""
                INSERT IGNORE INTO years (year_id) VALUES (%s)
            """, (year,))
    except mysql.connector.Error as e:
        print(f"Error ensuring years exist: {e}")


def main():
    results_csv = 'data/results.csv'
    shootouts_csv = 'data/shootouts.csv'

    print("Starting matches ETL")

    matches = extract_matches(results_csv)

    populate_shootouts(shootouts_csv, matches)

    load_matches(matches, DB_CONFIG)

    print(f"total matches = {len(matches)}")

    print("Finished matches ETL successfully")


if __name__ == "__main__":
    main()
