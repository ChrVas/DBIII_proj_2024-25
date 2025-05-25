COUNTRY_NAME_MAPPINGS = {
    'Bohemia': 'Czech Republic',
    'Bohemia and Moravia': 'Czech Republic',
    'Belgian Congo': 'DR Congo',
    'Congo-Kinshasa': 'DR Congo',
    'Congo-Léopoldville': 'DR Congo',
    'Zaïre': 'DR Congo',
    'Irish Free State': 'Republic of Ireland',
    'Éire': 'Republic of Ireland',
    'Yugoslavia': 'Serbia',
    'Czechoslovakia': 'Czech Republic',
    'German DR': 'Germany',
    'North Vietnam': 'Vietnam',
    'Vietnam Republic': 'Vietnam',
    'Yemen AR': 'Yemen', 
    'Yemen DPR': 'Yemen',
    'United Arab Republic': 'Egypt',
    'Saarland': 'Germany',
    'Manchuria': 'China',
    'China PR': 'China',
    
    'Czech Republic': 'Czechia',
    'DR Congo': 'Democratic Republic of the Congo',
    'North Macedonia': 'Republic of North Macedonia',
    'Macau': 'China',
    'Northern Cyprus': 'Cyprus',
    'Palestine': 'State of Palestine',
    'Tahiti': 'France',
    'São Tomé and Príncipe': 'Sao Tome and Principe',
    'Zanzibar': 'Tanzania'
}

UK_NATIONS = [
    'England',
    'Scotland', 
    'Wales',
    'Northern Ireland'
]

def get_country_name(country_name):
    if country_name in UK_NATIONS:
        return country_name
    return COUNTRY_NAME_MAPPINGS.get(country_name, country_name)