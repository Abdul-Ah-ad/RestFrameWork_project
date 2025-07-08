# cricdata_api/constants.py

# =========================
# Player Role Choices
# =========================
ROLE_STRING_TO_INT = {
    'BATSMEN': 1,
    'BATSMAN': 1,
    'BOWLER': 2,
    'ALLROUNDER': 3,
    'ALL-ROUNDER': 3,
    'WICKETKEEPER': 4,
    'WICKET-KEEPER': 4,
    'CAPTAIN': 5,
    'VICECAPTAIN': 6,
    'VICE-CAPTAIN': 6,
}
ROLE_ID_TO_LABEL = {
    1: 'Batsman',
    2: 'Bowler',
    3: 'All-Rounder',
    4: 'Wicket-Keeper',
    5: 'Captain',
    6: 'Vice-Captain',
}

PLAYER_ROLE_CHOICES = sorted(ROLE_ID_TO_LABEL.items())

# =========================
# Match Format Constants
# =========================
FORMAT_ODI = 'odi'
FORMAT_TEST = 'test'
FORMAT_T20 = 't20'
FORMAT_UNKNOWN = 'unknown'

MATCH_FORMAT_CHOICES = [
    (FORMAT_ODI, 'ODI'),
    (FORMAT_TEST, 'Test'),
    (FORMAT_T20, 'T20'),
    (FORMAT_UNKNOWN, 'Unknown'),
]

PLAYER_FORMATS = [FORMAT_ODI, FORMAT_TEST, FORMAT_T20]

# =========================
# Best XI Selection Limits
# =========================
TOP_BATSMAN_COUNT = 4
TOP_BOWLER_COUNT = 4
TOP_ALL_ROUNDER_COUNT = 2
TOP_KEEPER_COUNT = 1
BEST_XI_TOTAL_COUNT = 11

# =========================
# Batting Stat Keys (JSON)
# =========================
BAT_STAT_MATCHES = 'matches'
BAT_STAT_INNINGS = 'innings'
BAT_STAT_RUNS = 'runs'
BAT_STAT_AVERAGE = 'batting_average'
BAT_STAT_STRIKE_RATE = 'strike_rate'
BAT_STAT_FIFTIES = 'fifties'
BAT_STAT_HUNDREDS = 'hundreds'

# =========================
# Bowling Stat Keys (JSON)
# =========================
BOWL_STAT_OVERS = 'overs'
BOWL_STAT_WICKETS = 'wickets'
BOWL_STAT_ECONOMY = 'economy'
BOWL_STAT_AVERAGE = 'bowling_average'
BOWL_STAT_FIVE_WKT = 'five_wicket_hauls'

# =========================
# Player Model Field Names
# =========================
FIELD_PLAYER_FULL_NAME = 'player_full_name'
FIELD_PLAYER_ROLE = 'player_role_type'
FIELD_IS_ACTIVE = 'is_active_player'
FIELD_BATTING_STYLE = 'batting_style_description'
FIELD_BOWLING_STYLE = 'bowling_style_description'

FIELD_MATCHES = 'total_matches_played'
FIELD_INNINGS = 'total_innings_batted'
FIELD_RUNS = 'total_runs_scored'
FIELD_BAT_AVG = 'career_batting_average'
FIELD_STRIKE_RATE = 'career_strike_rate'
FIELD_50S = 'number_of_fifties'
FIELD_100S = 'number_of_hundreds'

FIELD_OVERS = 'total_overs_bowled'
FIELD_WICKETS = 'total_wickets_taken'
FIELD_BOWL_ECO = 'bowling_economy_rate'
FIELD_BOWL_AVG = 'bowling_average_score'
FIELD_FIVE_WKTS = 'number_of_five_wicket_hauls'
