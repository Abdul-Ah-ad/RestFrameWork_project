# views.py
import json
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from cricdata_api.serializers import TeamImportSerializer
from cricdata_api.models import Team
from rest_framework import generics
from cricdata_api.models import Team, Player
from cricdata_api.serializers import TeamImportSerializer, PlayerImportSerializer
from rest_framework import permissions


class FetchTeamsPlayersView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'combined_stats.json'
            )

            with open(file_path, 'r') as f:
                data = json.load(f)

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
                            needs_update = False
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
                            }.items():
                                if getattr(existing, key) != val:
                                    needs_update = True
                                    break

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

            if updated:
                return Response({'message': '✅ Data imported or updated successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': '🟢 No changes detected. Data is up-to-date.'}, status=status.HTTP_200_OK)

        except FileNotFoundError:
            return Response({'error': '❌ File not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamImportSerializer

class PlayerListView(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerImportSerializer
    

class Best(APIView):
    permission_classes = [permissions.AllowAny] 
    print('inside best start 11 function')
    def get(self, request):
        return Response({'detail':'gg'})
        team_name = request.query_params.get('team')
        # match_format = request.query_params.get('format', 'odi').strip().lower()
        # print(team_name)
        # print(match_format)

        # if not team_name:
        #     return Response({'error': 'Query parameter "team" is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # # ✅ Get team
        # team = Team.objects.filter(name__iexact=team_name).first()
        # if not team:
        #     return Response({'error': f'Team \"{team_name}\" not found.'}, status=status.HTTP_404_NOT_FOUND)

        # # ✅ Get players for that team and format
        # players = Player.objects.filter(team=team, format=match_format, is_active=True)

        # # ✅ Categorize players
        # batsmen = sorted(
        #     [p for p in players if 'bat' in p.role.lower() and 'keeper' not in p.role.lower()],
        #     key=lambda x: x.runs or 0,
        #     reverse=True
        # )[:4]

        # bowlers = sorted(
        #     [p for p in players if 'bowl' in p.role.lower()],
        #     key=lambda x: x.wickets or 0,
        #     reverse=True
        # )[:4]

        # allrounders = sorted(
        #     [p for p in players if 'rounder' in p.role.lower()],
        #     key=lambda x: (x.runs or 0) + (x.wickets or 0),
        #     reverse=True
        # )[:2]

        # keepers = sorted(
        #     [p for p in players if 'keeper' in p.role.lower()],
        #     key=lambda x: x.runs or 0,
        #     reverse=True
        # )[:1]

        # # ✅ Combine best XI
        # final_xi = batsmen + bowlers + allrounders + keepers

        # # ✅ Fill remaining spots with best of rest
        # if len(final_xi) < 11:
        #     selected_ids = {p.id for p in final_xi}
        #     remaining = [p for p in players if p.id not in selected_ids]
        #     final_xi += sorted(
        #         remaining,
        #         key=lambda x: (x.runs or 0) + (x.wickets or 0),
        #         reverse=True
        #     )[:11 - len(final_xi)]

        # serializer = PlayerImportSerializer(final_xi, many=True)
        # print('inside best end 11 function')
        return Response(serializer.data)
    
    