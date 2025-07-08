import json
import os

from rest_framework import status
from rest_framework.response import Response

from cricdata_api.models import Player, Team
from cricdata_api.serializers import PlayerSerializer


def load_json_file():
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'combined_stats.json'
    )
    if not os.path.exists(file_path):
        return None, 'File not found'

    try:
        with open(file_path, 'r') as f:
            return json.load(f), None
    except Exception as e:
        return None, str(e)


def import_team_and_players(data):
    updated = False

    for team_entry in data:
        team_data = team_entry.get('team', {})
        players_data = team_entry.get('players', [])

        team_id = team_data.get('team_id')
        team_obj = Team.objects.filter(team_id=team_id).first()

        if team_obj:
            if (
                team_obj.name != team_data.get('name') or
                team_obj.short_name != team_data.get('short_name') or
                team_obj.country_name != (team_data.get('country_name') or team_data.get('country'))
            ):
                team_obj.name = team_data.get('name')
                team_obj.short_name = team_data.get('short_name')
                team_obj.country_name = team_data.get('country_name') or team_data.get('country')
                team_obj.save()
                updated = True
        else:
            team_obj = Team.objects.create(
                team_id=team_id,
                name=team_data.get('name'),
                short_name=team_data.get('short_name'),
                country_name=team_data.get('country_name') or team_data.get('country')
            )
            updated = True

        for player in players_data:
            for fmt in ['odi', 'test', 't20']:
                bat = (player.get('batting') or {}).get(fmt, {})
                bowl = (player.get('bowling') or {}).get(fmt, {})

                existing = Player.objects.filter(
                    player_id=player['player_id'],
                    team=team_obj,
                    format=fmt
                ).first()

                if existing:
                    needs_update = any(
                        getattr(existing, key) != val
                        for key, val in {
                            "name": player["name"],
                            "role": player["role"],
                            "batting_style": player.get("batting_style"),
                            "bowling_style": player.get("bowling_style"),
                            "matches": bat.get("matches"),
                            "innings": bat.get("innings"),
                            "runs": bat.get("runs"),
                            "batting_average": bat.get("batting_average"),
                            "strike_rate": bat.get("strike_rate"),
                            "fifties": bat.get("fifties"),
                            "hundreds": bat.get("hundreds"),
                            "overs": bowl.get("overs"),
                            "wickets": bowl.get("wickets"),
                            "economy": bowl.get("economy"),
                            "bowling_average": bowl.get("bowling_average"),
                            "five_wicket_hauls": bowl.get("five_wicket_hauls"),
                        }.items()
                    )

                    if needs_update:
                        for k, v in {
                            "name": player["name"],
                            "role": player["role"],
                            "batting_style": player.get("batting_style"),
                            "bowling_style": player.get("bowling_style"),
                            "matches": bat.get("matches"),
                            "innings": bat.get("innings"),
                            "runs": bat.get("runs"),
                            "batting_average": bat.get("batting_average"),
                            "strike_rate": bat.get("strike_rate"),
                            "fifties": bat.get("fifties"),
                            "hundreds": bat.get("hundreds"),
                            "overs": bowl.get("overs"),
                            "wickets": bowl.get("wickets"),
                            "economy": bowl.get("economy"),
                            "bowling_average": bowl.get("bowling_average"),
                            "five_wicket_hauls": bowl.get("five_wicket_hauls"),
                        }.items():
                            setattr(existing, k, v)
                        existing.save()
                        updated = True
                else:
                    Player.objects.create(
                        player_id=player['player_id'],
                        team=team_obj,
                        format=fmt,
                        name=player["name"],
                        role=player["role"],
                        is_active=True,
                        batting_style=player.get("batting_style"),
                        bowling_style=player.get("bowling_style"),
                        matches=bat.get("matches"),
                        innings=bat.get("innings"),
                        runs=bat.get("runs"),
                        batting_average=bat.get("batting_average"),
                        strike_rate=bat.get("strike_rate"),
                        fifties=bat.get("fifties"),
                        hundreds=bat.get("hundreds"),
                        overs=bowl.get("overs"),
                        wickets=bowl.get("wickets"),
                        economy=bowl.get("economy"),
                        bowling_average=bowl.get("bowling_average"),
                        five_wicket_hauls=bowl.get("five_wicket_hauls"),
                    )
                    updated = True

    return updated


def get_best_xi(team_name, match_category):
    team = Team.objects.filter(name__iexact=team_name).first()
    if not team:
        return Response({'error': f'Team \"{team_name}\" not found.'}, status=status.HTTP_404_NOT_FOUND)

    players = Player.objects.filter(team=team, format=match_category, is_active=True)

    batsmen = sorted(
        [p for p in players if 'bat' in p.role.lower() and 'keeper' not in p.role.lower()],
        key=lambda x: x.runs or 0,
        reverse=True
    )[:4]

    bowlers = sorted(
        [p for p in players if 'bowl' in p.role.lower()],
        key=lambda x: x.wickets or 0,
        reverse=True
    )[:4]

    allrounders = sorted(
        [p for p in players if 'rounder' in p.role.lower()],
        key=lambda x: (x.runs or 0) + (x.wickets or 0),
        reverse=True
    )[:2]

    keepers = sorted(
        [p for p in players if 'keeper' in p.role.lower()],
        key=lambda x: x.runs or 0,
        reverse=True
    )[:1]

    final_xi = batsmen + bowlers + allrounders + keepers

    if len(final_xi) < 11:
        selected_ids = {p.id for p in final_xi}
        remaining = [p for p in players if p.id not in selected_ids]
        final_xi += sorted(
            remaining,
            key=lambda x: (x.runs or 0) + (x.wickets or 0),
            reverse=True
        )[:11 - len(final_xi)]

    serializer = PlayerSerializer(final_xi, many=True)
    return serializer.data
