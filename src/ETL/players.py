import csv
import mysql.connector
from database.db_config import DB_CONFIG


def extract_players(goalscorers_csv):
    players_data = {}
    match_goals = {} 

    with open(goalscorers_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            name = row.get('scorer', '').strip()
            date = row.get('date', '').strip()
            year = int(date[:4])

            match_key = f"{name}_{date}"

            match_goals[match_key] = match_goals.get(match_key, 0) + 1

            if name not in players_data:
                players_data[name] = {
                    'name': name,
                    'first_appearance_year': year,
                    'last_appearance_year': year,
                    'total_goals': 1,
                    'max_goals_in_match': match_goals[match_key]
                }
            else:
                player = players_data[name]
                player['first_appearance_year'] = min(
                    player['first_appearance_year'], year)
                player['last_appearance_year'] = max(
                    player['last_appearance_year'], year)
                player['total_goals'] += 1
                player['max_goals_in_match'] = max(
                    player['max_goals_in_match'],
                    match_goals[match_key]
                )

    return players_data


def load_players(players_data):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for player_name, data in players_data.items():
        insert_query = """
        INSERT INTO players
            (name, first_appearance_year, last_appearance_year,
                total_goals, max_goals_in_match)
        VALUES
            (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            first_appearance_year = LEAST(
                first_appearance_year, VALUES(first_appearance_year)),
            last_appearance_year = GREATEST(
                last_appearance_year, VALUES(last_appearance_year)),
            total_goals = VALUES(total_goals),
            max_goals_in_match = VALUES(max_goals_in_match)
        """

        cursor.execute(insert_query, (
            data['name'],
            data['first_appearance_year'],
            data['last_appearance_year'],
            data['total_goals'],
            data['max_goals_in_match']
        ))

    conn.commit()
    cursor.close()
    conn.close()


def main():
    print("Starting players ETL")

    goalscorers_csv = 'data/goalscorers.csv'

    players_data = extract_players(goalscorers_csv)
    load_players(players_data)

    print("Finished players ETL successfully")


if __name__ == "__main__":
    main()
