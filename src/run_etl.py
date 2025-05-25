from ETL.countries import main as countries_etl
from ETL.former_names import main as former_names_etl
from ETL.years import main as years_etl
from ETL.matches import main as matches_etl
from ETL.players import main as players_etl
from ETL.goals import main as goals_etl
from ETL.player_year_stats import main as player_year_stats_etl
from ETL.country_year_stats import main as country_year_stats_etl
from ETL.shootouts import main as shootouts_etl

countries_etl()
print("---")
former_names_etl()
print("---")
years_etl()
print("---")
matches_etl()
print("---")
players_etl()
print("---")
goals_etl()
print("---")
shootouts_etl()
print("---")
player_year_stats_etl()
print("---")
country_year_stats_etl()