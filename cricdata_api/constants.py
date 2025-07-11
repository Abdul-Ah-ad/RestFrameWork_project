class PlayerRole:
    BATSMAN = 1
    BOWLER = 2
    ALL_ROUNDER = 3
    WICKET_KEEPER = 4
    CAPTAIN = 5
    VICE_CAPTAIN = 6

    LABELS = {
        BATSMAN: 'Batsman',
        BOWLER: 'Bowler',
        ALL_ROUNDER: 'All-Rounder',
        WICKET_KEEPER: 'Wicket-Keeper',
        CAPTAIN: 'Captain',
        VICE_CAPTAIN: 'Vice-Captain',
    }

    CHOICES = sorted(LABELS.items())

    CRICKET_ROLE_LABEL_MAPPER  = {
        'BATSMEN': BATSMAN,
        'BATSMAN': BATSMAN,
        'BOWLER': BOWLER,
        'ALLROUNDER': ALL_ROUNDER,
        'ALL-ROUNDER': ALL_ROUNDER,
        'WICKETKEEPER': WICKET_KEEPER,
        'WICKET-KEEPER': WICKET_KEEPER,
        'CAPTAIN': CAPTAIN,
        'VICECAPTAIN': VICE_CAPTAIN,
        'VICE-CAPTAIN': VICE_CAPTAIN,
    }


class MatchFormat:
    TEST = 1
    ODI = 2
    T20 = 3
    UNKNOWN = 0

    FORMAT_LABELS = {
        TEST: "test",
        ODI: "odi",
        T20: "t20",
        UNKNOWN: "unknown"
    }

    INTEGER_CHOICES = [
        (UNKNOWN, "unknown"),
        (TEST, "test"),
        (ODI, "odi"),
        (T20, "t20"),
    ]

    SUPPORTED = [TEST, ODI, T20]


TOP_BATSMAN_COUNT = 4
TOP_BOWLER_COUNT = 4
TOP_ALL_ROUNDER_COUNT = 2
TOP_KEEPER_COUNT = 1
BEST_ELEVEN_TOTAL_COUNT = 11


PLAYER_NAME = 'name'
PLAYER_BATTING_STYLE = 'batting_style'
PLAYER_BOWLING_STYLE = 'bowling_style'

BAT_STAT_MATCHES = 'matches'
BAT_STAT_INNINGS = 'innings'
BAT_STAT_RUNS = 'runs'
BAT_STAT_AVERAGE = 'batting_average'
BAT_STAT_STRIKE_RATE = 'strike_rate'
BAT_STAT_FIFTIES = 'fifties'
BAT_STAT_HUNDREDS = 'hundreds'

BOWL_STAT_OVERS = 'overs'
BOWL_STAT_WICKETS = 'wickets'
BOWL_STAT_ECONOMY = 'economy'
BOWL_STAT_AVERAGE = 'bowling_average'
BOWL_STAT_FIVE_WKT = 'five_wicket_hauls'


PLAYER_FULL_NAME = 'player_full_name'
PLAYER_ROLE = 'player_role_type'
IS_ACTIVE = 'is_active_player'
BATTING_STYLE = 'batting_style_description'
BOWLING_STYLE = 'bowling_style_description'

TOTAL_NO_OF_MATCHES_PLAYED = 'total_matches_played'
TOTAL_NO_OF_INNINGS_BATTED = 'total_innings_batted'
TOTAL_NO_OF_RUNS_SCORED = 'total_runs_scored'
CAREER_BATTING_AVERAGE = 'career_batting_average'
CAREER_STRIKE_RATE = 'career_strike_rate'
TOTAL_NO_OF_FIFTIES = 'number_of_fifties'
TOTAL_NO_OF_HUNDREDS = 'number_of_hundreds'

NO_OF_OVERS_BOWLED = 'total_overs_bowled'
NO_OF_WICKETS_TAKEN = 'total_wickets_taken'
ECONOMY_RATE = 'bowling_economy_rate'
BOWLING_AVERAGE = 'bowling_average_score'
NO_OF_FIVE_WICKET_HAULS = 'number_of_five_wicket_hauls'


TEAM_OBJECT_KEY = 'team'
PLAYER_LIST_KEY = 'players'
PLAYER_ROLE_KEY = 'role'
PLAYER_BATTING_STATS_KEY = 'batting'
PLAYER_BOWLING_STATS_KEY = 'bowling'

TEAM_ID_KEY = 'team_id'
TEAM_COUNTRY_NAME_KEY = 'country_name'
TEAM_COUNTRY_CODE_KEY = 'country'
TEAM_NAME_KEY = 'name'
TEAM_SHORT_NAME_KEY = 'short_name'

