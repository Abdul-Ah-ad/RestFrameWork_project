"""
utils.py

This module provides helper functions for:
- Loading and parsing JSON team/player data
- Synchronizing team and player data with the database
- Selecting the best XI players for a team based on format-specific statistics
"""

from rest_framework import status
from rest_framework.response import Response

from cricdata_api.constants import (BAT_STAT_AVERAGE, BAT_STAT_FIFTIES,
                                    BAT_STAT_HUNDREDS, BAT_STAT_INNINGS,
                                    BAT_STAT_MATCHES, BAT_STAT_RUNS,
                                    BAT_STAT_STRIKE_RATE, BEST_XI_TOTAL_COUNT,
                                    BOWL_STAT_AVERAGE, BOWL_STAT_ECONOMY,
                                    BOWL_STAT_FIVE_WKT, BOWL_STAT_OVERS,
                                    BOWL_STAT_WICKETS, FIELD_50S, FIELD_100S,
                                    FIELD_BAT_AVG, FIELD_BATTING_STYLE,
                                    FIELD_BOWL_AVG, FIELD_BOWL_ECO,
                                    FIELD_BOWLING_STYLE, FIELD_FIVE_WKTS,
                                    FIELD_INNINGS, FIELD_IS_ACTIVE,
                                    FIELD_MATCHES, FIELD_OVERS,
                                    FIELD_PLAYER_FULL_NAME, FIELD_PLAYER_ROLE,
                                    FIELD_RUNS, FIELD_STRIKE_RATE,
                                    FIELD_WICKETS, JSON_BATTING_KEY,
                                    JSON_BOWLING_KEY, JSON_COUNTRY,
                                    JSON_COUNTRY_NAME, JSON_NAME,
                                    JSON_PLAYERS_KEY, JSON_ROLE_KEY,
                                    JSON_SHORT_NAME, JSON_TEAM_ID,
                                    JSON_TEAM_KEY, PLAYER_BATTING_STYLE,
                                    PLAYER_BOWLING_STYLE, PLAYER_FORMATS,
                                    PLAYER_NAME, ROLE_STRING_TO_INT,
                                    TOP_ALL_ROUNDER_COUNT, TOP_BATSMAN_COUNT,
                                    TOP_BOWLER_COUNT, TOP_KEEPER_COUNT)
from cricdata_api.models import Player, Team


def sync_teams_and_players_from_json(json_data):
    """
    Syncs teams and players from parsed JSON data to the database.
    Returns True if any update or creation occurred.
    """
    has_updates = False
    for team_record in json_data:
        team_info = team_record.get(JSON_TEAM_KEY, {})
        players_data = team_record.get(JSON_PLAYERS_KEY, [])
        team_instance, is_team_updated = process_team_from_json(team_info)
        has_updates |= is_team_updated
        has_updates |= save_or_update_all_players(players_data, team_instance)
    return has_updates


def process_team_from_json(team_info):
    """
    Processes team info: updates an existing team or creates a new one.
    Returns the team instance and a boolean indicating if it was updated.
    """
    team_id = team_info.get(JSON_TEAM_ID)
    country = team_info.get(JSON_COUNTRY_NAME) or team_info.get(JSON_COUNTRY)
    existing_team = Team.objects.filter(external_team_id=team_id).first()

    if existing_team:
        updated_fields = []
        if existing_team.full_team_name != team_info.get(JSON_NAME):
            existing_team.full_team_name = team_info.get(JSON_NAME)
            updated_fields.append('full_team_name')
        if existing_team.team_abbreviation != team_info.get(JSON_SHORT_NAME):
            existing_team.team_abbreviation = team_info.get(JSON_SHORT_NAME)
            updated_fields.append('team_abbreviation')
        if existing_team.country_name != country:
            existing_team.country_name = country
            updated_fields.append('country_name')

        if updated_fields:
            existing_team.save(update_fields=updated_fields)
            return existing_team, True
        return existing_team, False

    new_team = Team.objects.create(
        external_team_id=team_id,
        full_team_name=team_info.get(JSON_NAME),
        team_abbreviation=team_info.get(JSON_SHORT_NAME),
        country_name=country
    )
    return new_team, True


def save_or_update_all_players(players_data, team_instance):
    """
    Saves or updates all players associated with the given team.
    Returns True if any update or creation occurred.
    """
    has_updated = False
    for player_record in players_data:
        if process_single_player(player_record, team_instance):
            has_updated = True
    return has_updated


def process_single_player(player_data, team_instance):
    """
    Processes an individual player record for all formats.
    Creates or updates the player in the database.
    Returns True if the player was newly added or updated.
    """
    has_updated = False
    for format_type in PLAYER_FORMATS:
        batting_data = (player_data.get(JSON_BATTING_KEY) or {}).get(format_type, {})
        bowling_data = (player_data.get(JSON_BOWLING_KEY) or {}).get(format_type, {})

        role_string = (player_data.get(JSON_ROLE_KEY) or '').replace(" ", "").upper()
        role_int = ROLE_STRING_TO_INT.get(role_string, 1) 

        player_defaults = {
            FIELD_PLAYER_FULL_NAME: player_data[PLAYER_NAME],FIELD_PLAYER_ROLE: role_int,FIELD_IS_ACTIVE: True,
            FIELD_BATTING_STYLE: player_data.get(PLAYER_BATTING_STYLE),
            FIELD_BOWLING_STYLE: player_data.get(PLAYER_BOWLING_STYLE),
            FIELD_MATCHES: batting_data.get(BAT_STAT_MATCHES),FIELD_INNINGS: batting_data.get(BAT_STAT_INNINGS),
            FIELD_RUNS: batting_data.get(BAT_STAT_RUNS),FIELD_BAT_AVG: batting_data.get(BAT_STAT_AVERAGE),
            FIELD_STRIKE_RATE: batting_data.get(BAT_STAT_STRIKE_RATE),FIELD_50S: batting_data.get(BAT_STAT_FIFTIES),
            FIELD_100S: batting_data.get(BAT_STAT_HUNDREDS),FIELD_OVERS: bowling_data.get(BOWL_STAT_OVERS),
            FIELD_WICKETS: bowling_data.get(BOWL_STAT_WICKETS),FIELD_BOWL_ECO: bowling_data.get(BOWL_STAT_ECONOMY),
            FIELD_BOWL_AVG: bowling_data.get(BOWL_STAT_AVERAGE),FIELD_FIVE_WKTS: bowling_data.get(BOWL_STAT_FIVE_WKT),
        }

        existing_player = Player.objects.filter(
            external_player_id=player_data['player_id'],
            team=team_instance,
            format_category=format_type
        ).first()

        if existing_player:
            changed_fields = [
                field for field, new_value in player_defaults.items()
                if getattr(existing_player, field) != new_value
            ]
            if changed_fields:
                for changed_field in changed_fields:
                    setattr(existing_player, changed_field, player_defaults[changed_field])
                existing_player.save(update_fields=changed_fields)
                has_updated = True
        else:
            Player.objects.create(
                external_player_id=player_data['player_id'],
                team=team_instance,
                format_category=format_type,
                **player_defaults
            )
            has_updated = True

    return has_updated


def is_batsman(player):
    """Returns True if player is a batsman but not a wicket-keeper."""
    role = player.get_player_role_type_display().lower()
    return 'bat' in role and 'keeper' not in role


def is_bowler(player):
    """Returns True if player is a bowler."""
    return 'bowl' in player.get_player_role_type_display().lower()


def is_allrounder(player):
    """Returns True if player is an all-rounder."""
    return 'rounder' in player.get_player_role_type_display().lower()


def is_wicket_keeper(player):
    """Returns True if player is a wicket-keeper."""
    return 'keeper' in player.get_player_role_type_display().lower()


def performance_score_runs(player):
    """Returns player's total runs for sorting."""
    return player.total_runs_scored or 0


def performance_score_wickets(player):
    """Returns player's total wickets for sorting."""
    return player.total_wickets_taken or 0


def performance_score_allrounder(player):
    """Returns combined runs and wickets for all-rounder ranking."""
    return (player.total_runs_scored or 0) + (player.total_wickets_taken or 0)


def select_best_players(players_queryset, role_condition_fn, score_fn, limit_count):
    """
    Filters players by role condition and sorts them by score.
    Returns top N players as per limit_count.
    """
    filtered = filter(role_condition_fn, players_queryset)
    sorted_players = sorted(filtered, key=score_fn, reverse=True)
    return sorted_players[:limit_count]


def get_best_eleven_players(team_name, match_format):
    """
    Selects the best 11 players from a team based on performance in the given match format.
    Returns serialized player data.
    local import to avoid circular dependency.
    """
    from cricdata_api.serializers import PlayerSerializer

    team_instance = Team.objects.filter(full_team_name__iexact=team_name).first()
    if not team_instance:
        return Response({'error': f'Team \"{team_name}\" not found.'}, status=status.HTTP_404_NOT_FOUND)

    all_players = Player.objects.filter(
        team=team_instance,format_category=match_format,is_active_player=True)

    best_batsmen = select_best_players(all_players, is_batsman, performance_score_runs, TOP_BATSMAN_COUNT)
    best_bowlers = select_best_players(all_players, is_bowler, performance_score_wickets, TOP_BOWLER_COUNT)
    best_allrounders = select_best_players(all_players, is_allrounder, performance_score_allrounder,
                                           TOP_ALL_ROUNDER_COUNT)
    best_keepers = select_best_players(all_players, is_wicket_keeper, performance_score_runs, TOP_KEEPER_COUNT)

    selected_players = best_batsmen + best_bowlers + best_allrounders + best_keepers

    if len(selected_players) < BEST_XI_TOTAL_COUNT:
        already_selected_ids = {player.id for player in selected_players}
        remaining_players = sorted(
            [player for player in all_players if player.id not in already_selected_ids],
            key=performance_score_allrounder,
            reverse=True
        )
        selected_players += remaining_players[:BEST_XI_TOTAL_COUNT - len(selected_players)]

    return PlayerSerializer(selected_players, many=True).data
