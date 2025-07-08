import json
import os

from rest_framework import status
from rest_framework.response import Response

from cricdata_api.models import Player, Team
from cricdata_api.constants import (
    PLAYER_FORMATS, TOP_BATSMAN_COUNT, TOP_BOWLER_COUNT, TOP_ALL_ROUNDER_COUNT,
    TOP_KEEPER_COUNT, BEST_XI_TOTAL_COUNT,
    BAT_STAT_MATCHES, BAT_STAT_INNINGS, BAT_STAT_RUNS, BAT_STAT_AVERAGE, BAT_STAT_STRIKE_RATE,
    BAT_STAT_FIFTIES, BAT_STAT_HUNDREDS,
    BOWL_STAT_OVERS, BOWL_STAT_WICKETS, BOWL_STAT_ECONOMY, BOWL_STAT_AVERAGE, BOWL_STAT_FIVE_WKT,
    FIELD_PLAYER_FULL_NAME, FIELD_PLAYER_ROLE, FIELD_IS_ACTIVE, FIELD_BATTING_STYLE, FIELD_BOWLING_STYLE,
    FIELD_MATCHES, FIELD_INNINGS, FIELD_RUNS, FIELD_BAT_AVG, FIELD_STRIKE_RATE, FIELD_50S, FIELD_100S,
    FIELD_OVERS, FIELD_WICKETS, FIELD_BOWL_ECO, FIELD_BOWL_AVG, FIELD_FIVE_WKTS,
    ROLE_STRING_TO_INT,
)


def load_json_file():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'combined_stats.json')
    if not os.path.exists(file_path):
        return None, 'File not found'
    try:
        with open(file_path, 'r') as file:
            return json.load(file), None
    except json.JSONDecodeError as decode_error:
        return None, f'Invalid JSON format: {decode_error}'
    except OSError as os_error:
        return None, f'File access error: {os_error}'


def sync_teams_and_players_from_json(json_data):
    has_updates = False
    for team_record in json_data:
        team_info = team_record.get('team', {})
        players_data = team_record.get('players', [])
        team_instance, is_team_updated = process_team_from_json(team_info)
        has_updates |= is_team_updated
        has_updates |= save_or_update_all_players(players_data, team_instance)
    return has_updates


def process_team_from_json(team_info):
    team_id = team_info.get('team_id')
    country = team_info.get('country_name') or team_info.get('country')
    existing_team = Team.objects.filter(external_team_id=team_id).first()

    if existing_team:
        updated_fields = []
        if existing_team.full_team_name != team_info.get('name'):
            existing_team.full_team_name = team_info.get('name')
            updated_fields.append('full_team_name')
        if existing_team.team_abbreviation != team_info.get('short_name'):
            existing_team.team_abbreviation = team_info.get('short_name')
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
        full_team_name=team_info.get('name'),
        team_abbreviation=team_info.get('short_name'),
        country_name=country
    )
    return new_team, True


def save_or_update_all_players(players_data, team_instance):
    has_updated = False
    for player_record in players_data:
        if process_single_player(player_record, team_instance):
            has_updated = True
    return has_updated


def process_single_player(player_data, team_instance):
    has_updated = False
    for format_type in PLAYER_FORMATS:
        batting_data = (player_data.get('batting') or {}).get(format_type, {})
        bowling_data = (player_data.get('bowling') or {}).get(format_type, {})

        role_string = (player_data.get('role') or '').replace(" ", "").upper()
        role_int = ROLE_STRING_TO_INT.get(role_string, 1)  # Default to 'Batsman'

        player_defaults = {
            FIELD_PLAYER_FULL_NAME: player_data['name'],
            FIELD_PLAYER_ROLE: role_int,
            FIELD_IS_ACTIVE: True,
            FIELD_BATTING_STYLE: player_data.get('batting_style'),
            FIELD_BOWLING_STYLE: player_data.get('bowling_style'),
            FIELD_MATCHES: batting_data.get(BAT_STAT_MATCHES),
            FIELD_INNINGS: batting_data.get(BAT_STAT_INNINGS),
            FIELD_RUNS: batting_data.get(BAT_STAT_RUNS),
            FIELD_BAT_AVG: batting_data.get(BAT_STAT_AVERAGE),
            FIELD_STRIKE_RATE: batting_data.get(BAT_STAT_STRIKE_RATE),
            FIELD_50S: batting_data.get(BAT_STAT_FIFTIES),
            FIELD_100S: batting_data.get(BAT_STAT_HUNDREDS),
            FIELD_OVERS: bowling_data.get(BOWL_STAT_OVERS),
            FIELD_WICKETS: bowling_data.get(BOWL_STAT_WICKETS),
            FIELD_BOWL_ECO: bowling_data.get(BOWL_STAT_ECONOMY),
            FIELD_BOWL_AVG: bowling_data.get(BOWL_STAT_AVERAGE),
            FIELD_FIVE_WKTS: bowling_data.get(BOWL_STAT_FIVE_WKT),
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


def select_players(all_players_queryset, role_condition_function, sorting_key_function, limit_count):
    filtered_players = filter(role_condition_function, all_players_queryset)
    sorted_players = sorted(filtered_players, key=sorting_key_function, reverse=True)
    return sorted_players[:limit_count]


def get_best_eleven_players(team_name, match_format):
    from cricdata_api.serializers import PlayerSerializer  # Avoid circular import
    team_instance = Team.objects.filter(full_team_name__iexact=team_name).first()
    if not team_instance:
        return Response({'error': f'Team "{team_name}" not found.'}, status=status.HTTP_404_NOT_FOUND)

    all_team_players = Player.objects.filter(
        team=team_instance,
        format_category=match_format,
        is_active_player=True
    )

    best_batsmen = select_players(
        all_team_players,
        lambda player: 'bat' in player.get_player_role_type_display().lower() and 'keeper' not in player.get_player_role_type_display().lower(),
        lambda player: player.total_runs_scored or 0,
        TOP_BATSMAN_COUNT
    )

    best_bowlers = select_players(
        all_team_players,
        lambda player: 'bowl' in player.get_player_role_type_display().lower(),
        lambda player: player.total_wickets_taken or 0,
        TOP_BOWLER_COUNT
    )

    best_allrounders = select_players(
        all_team_players,
        lambda player: 'rounder' in player.get_player_role_type_display().lower(),
        lambda player: (player.total_runs_scored or 0) + (player.total_wickets_taken or 0),
        TOP_ALL_ROUNDER_COUNT
    )

    best_wicket_keepers = select_players(
        all_team_players,
        lambda player: 'keeper' in player.get_player_role_type_display().lower(),
        lambda player: player.total_runs_scored or 0,
        TOP_KEEPER_COUNT
    )

    final_selected_players = best_batsmen + best_bowlers + best_allrounders + best_wicket_keepers

    if len(final_selected_players) < BEST_XI_TOTAL_COUNT:
        already_selected_ids = {player.id for player in final_selected_players}
        remaining_players = sorted(
            [player for player in all_team_players if player.id not in already_selected_ids],
            key=lambda player: (player.total_runs_scored or 0) + (player.total_wickets_taken or 0),
            reverse=True
        )
        final_selected_players += remaining_players[:BEST_XI_TOTAL_COUNT - len(final_selected_players)]

    return PlayerSerializer(final_selected_players, many=True).data

