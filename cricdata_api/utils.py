import json
import os

from rest_framework import status
from rest_framework.response import Response

from cricdata_api.models import Player, Team
from cricdata_api.serializers import PlayerSerializer

# === Constants === #
TOP_BATSMAN_COUNT = 4
TOP_BOWLER_COUNT = 4
TOP_ALL_ROUNDER_COUNT = 2
TOP_KEEPER_COUNT = 1
BEST_XI_TOTAL_COUNT = 11


def load_json_file():
    """
    Load combined_stats.json file from the root project directory.
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'combined_stats.json'
    )

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
    """
    Main orchestrator: Processes all teams and their players from JSON.
    """
    has_updates = False
    for team_record in json_data:
        team_info = team_record.get('team', {})
        players = team_record.get('players', [])
        team, team_updated = process_team(team_info)
        has_updates |= team_updated

        for player_data in players:
            player_updated = process_player(player_data, team)
            has_updates |= player_updated

    return has_updates


def process_team(team_info):
    """
    Create or update a team from JSON data.
    """
    team_id = team_info.get('team_id')
    country = team_info.get('country_name') or team_info.get('country')
    team = Team.objects.filter(team_id=team_id).first()

    if team:
        if (
            team.name != team_info.get('name') or
            team.short_name != team_info.get('short_name') or
            team.country_name != country
        ):
            team.name = team_info.get('name')
            team.short_name = team_info.get('short_name')
            team.country_name = country
            team.save()
            return team, True
        return team, False

    team = Team.objects.create(
        team_id=team_id,
        name=team_info.get('name'),
        short_name=team_info.get('short_name'),
        country_name=country
    )
    return team, True


def process_player(player_data, team):
    """
    Create or update a player's stats across formats.
    """
    has_updated = False
    for format_type in ['odi', 'test', 't20']:
        batting = (player_data.get('batting') or {}).get(format_type, {})
        bowling = (player_data.get('bowling') or {}).get(format_type, {})

        defaults = {
            "name": player_data["name"],
            "role": player_data["role"],
            "is_active": True,
            "batting_style": player_data.get("batting_style"),
            "bowling_style": player_data.get("bowling_style"),
            "matches": batting.get("matches"),
            "innings": batting.get("innings"),
            "runs": batting.get("runs"),
            "batting_average": batting.get("batting_average"),
            "strike_rate": batting.get("strike_rate"),
            "fifties": batting.get("fifties"),
            "hundreds": batting.get("hundreds"),
            "overs": bowling.get("overs"),
            "wickets": bowling.get("wickets"),
            "economy": bowling.get("economy"),
            "bowling_average": bowling.get("bowling_average"),
            "five_wicket_hauls": bowling.get("five_wicket_hauls"),
        }

        player = Player.objects.filter(
            player_id=player_data['player_id'],
            team=team,
            format=format_type
        ).first()

        if player:
            if any(getattr(player, field) != value for field, value in defaults.items()):
                for field, value in defaults.items():
                    setattr(player, field, value)
                player.save()
                has_updated = True
        else:
            Player.objects.create(
                player_id=player_data['player_id'],
                team=team,
                format=format_type,
                **defaults
            )
            has_updated = True

    return has_updated


def select_players(players, role_condition, sort_key_func, limit):
    """
    Filter, sort, and select top N players based on condition and metric.
    """
    filtered_players = filter(role_condition, players)
    sorted_players = sorted(filtered_players, key=sort_key_func, reverse=True)
    return sorted_players[:limit]


def get_best_xi(team_name, match_category):
    """
    Select the best XI players based on performance for a given team and match format.
    """
    team = Team.objects.filter(name__iexact=team_name).first()
    if not team:
        return Response({'error': f'Team \"{team_name}\" not found.'}, status=status.HTTP_404_NOT_FOUND)

    all_players = Player.objects.filter(team=team, format=match_category, is_active=True)

    best_batsmen = select_players(
        all_players,
        lambda player: 'bat' in player.role.lower() and 'keeper' not in player.role.lower(),
        lambda player: player.runs or 0,
        TOP_BATSMAN_COUNT
    )

    best_bowlers = select_players(
        all_players,
        lambda player: 'bowl' in player.role.lower(),
        lambda player: player.wickets or 0,
        TOP_BOWLER_COUNT
    )

    best_allrounders = select_players(
        all_players,
        lambda player: 'rounder' in player.role.lower(),
        lambda player: (player.runs or 0) + (player.wickets or 0),
        TOP_ALL_ROUNDER_COUNT
    )

    best_keeper = select_players(
        all_players,
        lambda player: 'keeper' in player.role.lower(),
        lambda player: player.runs or 0,
        TOP_KEEPER_COUNT
    )

    final_xi = best_batsmen + best_bowlers + best_allrounders + best_keeper

    if len(final_xi) < BEST_XI_TOTAL_COUNT:
        selected_ids = {player.id for player in final_xi}
        remaining_players = [player for player in all_players if player.id not in selected_ids]
        additional_players = sorted(
            remaining_players,
            key=lambda player: (player.runs or 0) + (player.wickets or 0),
            reverse=True
        )
        final_xi += additional_players[:BEST_XI_TOTAL_COUNT - len(final_xi)]

    serializer = PlayerSerializer(final_xi, many=True)
    return serializer.data


