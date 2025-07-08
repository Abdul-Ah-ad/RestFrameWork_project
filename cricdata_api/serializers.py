from rest_framework import serializers

from cricdata_api.models import Player, Team

# Constants for formats
FORMAT_ODI = 'odi'
FORMAT_TEST = 'test'
FORMAT_T20 = 't20'
PLAYER_FORMATS = [FORMAT_ODI, FORMAT_TEST, FORMAT_T20]


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        exclude = ['id']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['team_id', 'name', 'short_name', 'country_name']


class TeamWithPlayersSerializer(serializers.ModelSerializer):
    players = serializers.ListField(write_only=True)

    class Meta:
        model = Team
        fields = ['team_id', 'name', 'short_name', 'country_name', 'players']

    def create(self, validated_data):
        players_data = validated_data.pop('players')
        team, _ = Team.objects.update_or_create(
            team_id=validated_data['team_id'],
            defaults=validated_data
        )
        self._save_or_update_all_players(players_data, team)
        return team

    def update(self, instance, validated_data):
        players_data = validated_data.pop('players', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._save_or_update_all_players(players_data, instance)
        return instance

    def _save_or_update_all_players(self, players_data, team):
        for player_data in players_data:
            self._process_player_data(player_data, team)

    def _process_player_data(self, player_data, team):
        player_id = player_data.get("player_id")
        name = player_data.get("name")
        role = player_data.get("role", "Unknown")
        batting_style = player_data.get("batting_style")
        bowling_style = player_data.get("bowling_style")

        for format_type in PLAYER_FORMATS:
            batting_stats = (player_data.get('batting') or {}).get(format_type, {})
            bowling_stats = (player_data.get('bowling') or {}).get(format_type, {})

            Player.objects.update_or_create(
                player_id=player_id,
                team=team,
                format=format_type,
                defaults={
                    "name": name,
                    "role": role,
                    "is_active": True,
                    "batting_style": batting_style,
                    "bowling_style": bowling_style,
                    "matches": batting_stats.get("matches"),
                    "innings": batting_stats.get("innings"),
                    "runs": batting_stats.get("runs"),
                    "batting_average": batting_stats.get("batting_average"),
                    "strike_rate": batting_stats.get("strike_rate"),
                    "fifties": batting_stats.get("fifties"),
                    "hundreds": batting_stats.get("hundreds"),
                    "overs": bowling_stats.get("overs"),
                    "wickets": bowling_stats.get("wickets"),
                    "economy": bowling_stats.get("economy"),
                    "bowling_average": bowling_stats.get("bowling_average"),
                    "five_wicket_hauls": bowling_stats.get("five_wicket_hauls"),
                }
            )



