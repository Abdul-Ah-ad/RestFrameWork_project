"""
This module provides helper functions for:
- Loading and parsing JSON team/player data
- Synchronizing team and player data with the database
- Selecting the best XI players for a team based on format-specific statistics
"""

from typing import Any, Dict, List, Tuple

from rest_framework import status
from rest_framework.response import Response

from cricdata_api.constants import (BAT_STAT_AVERAGE, BAT_STAT_FIFTIES,
                                    BAT_STAT_HUNDREDS, BAT_STAT_INNINGS,
                                    BAT_STAT_MATCHES, BAT_STAT_RUNS,
                                    BAT_STAT_STRIKE_RATE, BATTING_STYLE,
                                    BEST_ELEVEN_TOTAL_COUNT, BOWL_STAT_AVERAGE,
                                    BOWL_STAT_ECONOMY, BOWL_STAT_FIVE_WKT,
                                    BOWL_STAT_OVERS, BOWL_STAT_WICKETS,
                                    BOWLING_AVERAGE, BOWLING_STYLE,
                                    CAREER_BATTING_AVERAGE, CAREER_STRIKE_RATE,
                                    ECONOMY_RATE, IS_ACTIVE,
                                    NO_OF_FIVE_WICKET_HAULS,
                                    NO_OF_OVERS_BOWLED, NO_OF_WICKETS_TAKEN,
                                    PLAYER_BATTING_STATS_KEY,
                                    PLAYER_BATTING_STYLE,
                                    PLAYER_BOWLING_STATS_KEY,
                                    PLAYER_BOWLING_STYLE, PLAYER_FULL_NAME,
                                    PLAYER_LIST_KEY, PLAYER_NAME,
                                    PLAYER_ROLE_KEY, TEAM_COUNTRY_CODE_KEY,
                                    TEAM_COUNTRY_NAME_KEY, TEAM_ID_KEY,
                                    TEAM_NAME_KEY, TEAM_OBJECT_KEY,
                                    TEAM_SHORT_NAME_KEY, TOP_ALL_ROUNDER_COUNT,
                                    TOP_BATSMAN_COUNT, TOP_BOWLER_COUNT,
                                    TOP_KEEPER_COUNT, TOTAL_NO_OF_FIFTIES,
                                    TOTAL_NO_OF_HUNDREDS,
                                    TOTAL_NO_OF_INNINGS_BATTED,
                                    TOTAL_NO_OF_MATCHES_PLAYED,
                                    TOTAL_NO_OF_RUNS_SCORED, MatchFormat,
                                    PlayerRole)
from cricdata_api.models import Player, Team


def sync_teams_and_players_from_json(json_data: List[Dict[str, Any]]) -> bool:
    """
    Syncs all teams and players from the provided JSON structure.

    Args:
        json_data: List of dictionaries containing team and player data.

    Returns:
        bool: True if any data was updated, False otherwise.
    """
    has_updates = False
    for team_record in json_data:
        team_info = team_record.get(TEAM_OBJECT_KEY, {})
        players_data = team_record.get(PLAYER_LIST_KEY, [])
        team_instance, team_updated = process_team_from_json(team_info)
        has_updates |= team_updated
        has_updates |= save_or_update_all_players(players_data, team_instance)
    return has_updates


def process_team_from_json(team_info: Dict[str, Any]) -> Tuple[Team, bool]:
    """
    Updates or creates a Team instance based on external data.

    Returns:
        Tuple[Team, bool]: Team instance and whether it was updated or created.
    """
    team_id = team_info.get(TEAM_ID_KEY)
    country = team_info.get(TEAM_COUNTRY_NAME_KEY) or team_info.get(TEAM_COUNTRY_CODE_KEY)
    existing_team = Team.objects.filter(external_team_id=team_id).first()

    if existing_team:
        updated_fields = []
        if existing_team.full_team_name != team_info.get(TEAM_NAME_KEY):
            existing_team.full_team_name = team_info.get(TEAM_NAME_KEY)
            updated_fields.append('full_team_name')
        if existing_team.team_abbreviation != team_info.get(TEAM_SHORT_NAME_KEY):
            existing_team.team_abbreviation = team_info.get(TEAM_SHORT_NAME_KEY)
            updated_fields.append('team_abbreviation')
        if existing_team.country_name != country:
            existing_team.country_name = country
            updated_fields.append('country_name')

        if updated_fields:
            existing_team.save(update_fields=updated_fields)
            return existing_team, True
        return existing_team, False

    new_team = Team.objects.create(
        external_team_id=team_id,full_team_name=team_info.get(TEAM_NAME_KEY),
        team_abbreviation=team_info.get(TEAM_SHORT_NAME_KEY),country_name=country
    )
    return new_team, True


def save_or_update_all_players(players_data: List[Dict[str, Any]], team_instance: Team) -> bool:
    """
    Syncs all players for a team from player data.

    Returns:
        bool: True if any player was updated or created.
    """
    has_updated = False
    for player_data in players_data:
        if create_or_update_single_player_stats(player_data, team_instance):
            has_updated = True
    return has_updated


def create_or_update_single_player_stats(player_data: Dict[str, Any], team_instance: Team) -> bool:
    """
    Syncs a single player across all formats.

    Returns:
        bool: True if the player was created or updated.
    """
    has_updated = False
    for format_type in MatchFormat.SUPPORTED:
        batting_data = (player_data.get(PLAYER_BATTING_STATS_KEY) or {}).get(format_type, {})
        bowling_data = (player_data.get(PLAYER_BOWLING_STATS_KEY) or {}).get(format_type, {})

        role_string = (player_data.get(PLAYER_ROLE_KEY) or '').replace(" ", "").upper()
        role_int = PlayerRole.CRICKET_ROLE_LABEL_MAPPER.get(role_string, PlayerRole.BATSMAN)

        player_defaults = {
            PLAYER_FULL_NAME: player_data[PLAYER_NAME],'player_role_type': role_int,IS_ACTIVE: True,
            BATTING_STYLE: player_data.get(PLAYER_BATTING_STYLE),
            BOWLING_STYLE: player_data.get(PLAYER_BOWLING_STYLE),
            TOTAL_NO_OF_MATCHES_PLAYED: batting_data.get(BAT_STAT_MATCHES),
            TOTAL_NO_OF_INNINGS_BATTED: batting_data.get(BAT_STAT_INNINGS),
            TOTAL_NO_OF_RUNS_SCORED: batting_data.get(BAT_STAT_RUNS),
            CAREER_BATTING_AVERAGE: batting_data.get(BAT_STAT_AVERAGE),
            CAREER_STRIKE_RATE: batting_data.get(BAT_STAT_STRIKE_RATE),
            TOTAL_NO_OF_FIFTIES: batting_data.get(BAT_STAT_FIFTIES),
            TOTAL_NO_OF_HUNDREDS: batting_data.get(BAT_STAT_HUNDREDS),
            NO_OF_OVERS_BOWLED: bowling_data.get(BOWL_STAT_OVERS),
            NO_OF_WICKETS_TAKEN: bowling_data.get(BOWL_STAT_WICKETS),
            ECONOMY_RATE: bowling_data.get(BOWL_STAT_ECONOMY),
            BOWLING_AVERAGE: bowling_data.get(BOWL_STAT_AVERAGE),
            NO_OF_FIVE_WICKET_HAULS: bowling_data.get(BOWL_STAT_FIVE_WKT),
        }

        player_instance = Player.objects.filter(
            external_player_id=player_data['player_id'],player_associated_team=team_instance,
            format_category=format_type
        ).first()

        if player_instance:
            changed_fields = [
                field for field, new_value in player_defaults.items()
                if getattr(player_instance, field) != new_value
            ]
            if changed_fields:
                for field in changed_fields:
                    setattr(player_instance, field, player_defaults[field])
                player_instance.save(update_fields=changed_fields)
                has_updated = True
        else:
            Player.objects.update_or_create(
                external_player_id=player_data['player_id'],format_category=format_type,
                defaults={'player_associated_team': team_instance,**player_defaults})
            has_updated = True

    return has_updated


def is_batsman(player: Player) -> bool:
    """
    Determines if the given player is a batsman (but not a wicket-keeper).

    Args:
        player (Player): The player instance.

    Returns:
        bool: True if the player is a batsman, False otherwise.
    """
    return 'bat' in player.get_player_role_type_display().lower() and 'keeper' not in player.get_player_role_type_display().lower()


def is_bowler(player: Player) -> bool:
    """
    Determines if the given player is a bowler.

    Args:
        player (Player): The player instance.

    Returns:
        bool: True if the player is a bowler, False otherwise.
    """
    return 'bowl' in player.get_player_role_type_display().lower()


def is_allrounder(player: Player) -> bool:
    """
    Determines if the given player is an all-rounder.

    Args:
        player (Player): The player instance.

    Returns:
        bool: True if the player is an all-rounder, False otherwise.
    """
    return 'rounder' in player.get_player_role_type_display().lower()


def is_wicket_keeper(player: Player) -> bool:
    """
    Determines if the given player is a wicket-keeper.

    Args:
        player (Player): The player instance.

    Returns:
        bool: True if the player is a wicket-keeper, False otherwise.
    """
    return 'keeper' in player.get_player_role_type_display().lower()


def performance_score_runs(player: Player) -> int:
    """
    Returns the performance score of a player based on total runs scored.

    Args:
        player (Player): The player instance.

    Returns:
        int: Total runs scored or 0 if not available.
    """
    return getattr(player, TOTAL_NO_OF_RUNS_SCORED) or 0


def performance_score_wickets(player: Player) -> int:
    """
    Returns the performance score of a player based on total wickets taken.

    Args:
        player (Player): The player instance.

    Returns:
        int: Total wickets taken or 0 if not available.
    """
    return getattr(player, NO_OF_WICKETS_TAKEN) or 0


def performance_score_allrounder(player: Player) -> int:
    """
    Returns a combined performance score for an all-rounder (runs + wickets).

    Args:
        player (Player): The player instance.

    Returns:
        int: Sum of runs and wickets, or 0 if none.
    """
    return performance_score_runs(player) + performance_score_wickets(player)


def get_sorted_best_players(players_queryset, role_condition_function, scoring_function, limit_count: int):
    """
    Filters and sorts players based on role and scoring function, then limits the result.

    Args:
        players_queryset (QuerySet): Queryset of Player instances.
        role_condition_function (Callable): Function to filter players by role.
        scoring_function (Callable): Function to calculate performance score.
        limit_count (int): Maximum number of top players to return.

    Returns:
        List[Player]: Top players sorted by score in descending order.
    """
    filtered = filter(role_condition_function, players_queryset)
    return sorted(filtered, key=scoring_function, reverse=True)[:limit_count]


def get_best_eleven_players(team_name: str, match_format: str):
    """
    Selects the best eleven players from a team based on performance.

    Args:
        team_name: Name of the team.
        match_format: Format category (e.g., 'odi', 'test').

    Returns:
        Response or serialized player list.
    """
    from cricdata_api.serializers import PlayerSerializer

    team_instance = Team.objects.filter(full_team_name__iexact=team_name).first()
    if not team_instance:
        return Response({'error': f'Team \'{team_name}\' not found.'}, status=status.HTTP_404_NOT_FOUND)

    all_players = Player.objects.filter(
        player_associated_team=team_instance,format_category=match_format,is_active_player=True)

    best_batsmen = get_sorted_best_players(all_players, is_batsman, performance_score_runs, TOP_BATSMAN_COUNT)
    best_bowlers = get_sorted_best_players(all_players, is_bowler, performance_score_wickets, TOP_BOWLER_COUNT)
    best_allrounders = get_sorted_best_players(all_players, is_allrounder, performance_score_allrounder, TOP_ALL_ROUNDER_COUNT)
    best_keepers = get_sorted_best_players(all_players, is_wicket_keeper, performance_score_runs, TOP_KEEPER_COUNT)

    selected_players = best_batsmen + best_bowlers + best_allrounders + best_keepers

    if len(selected_players) < BEST_ELEVEN_TOTAL_COUNT:
        already_selected_ids = {p.id for p in selected_players}
        remaining_players = sorted(
            [p for p in all_players if p.id not in already_selected_ids],
            key=performance_score_allrounder,reverse=True)
        selected_players += remaining_players[:BEST_ELEVEN_TOTAL_COUNT - len(selected_players)]

    return PlayerSerializer(selected_players, many=True).data
