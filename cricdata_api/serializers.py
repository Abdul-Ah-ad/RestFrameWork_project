from rest_framework import serializers
from cricdata_api.models import Team, Player


class PlayerImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        exclude = ['id']


class TeamImportSerializer(serializers.ModelSerializer):
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
        self._save_or_update_players(players_data, team)
        return team

    def update(self, instance, validated_data):
        players_data = validated_data.pop('players', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._save_or_update_players(players_data, instance)
        return instance

    def _save_or_update_players(self, players_data, team):
        for player in players_data:
            player_id = player.get("player_id")
            name = player.get("name")
            role = player.get("role", "Unknown")

            batting_styles = player.get("batting_style")
            bowling_styles = player.get("bowling_style")

            for fmt in ['odi', 'test', 't20']:
                bat = (player.get('batting') or {}).get(fmt, {})
                bowl = (player.get('bowling') or {}).get(fmt, {})

                Player.objects.update_or_create(
                    player_id=player_id,
                    team=team,
                    format=fmt,
                    defaults={
                        "name": name,
                        "role": role,
                        "is_active": True,
                        "batting_style": batting_styles,
                        "bowling_style": bowling_styles,

                        # Batting stats
                        "matches": bat.get("matches"),
                        "innings": bat.get("innings"),
                        "runs": bat.get("runs"),
                        "batting_average": bat.get("batting_average"),
                        "strike_rate": bat.get("strike_rate"),
                        "fifties": bat.get("fifties"),
                        "hundreds": bat.get("hundreds"),

                        # Bowling stats
                        "overs": bowl.get("overs"),
                        "wickets": bowl.get("wickets"),
                        "economy": bowl.get("economy"),
                        "bowling_average": bowl.get("bowling_average"),
                        "five_wicket_hauls": bowl.get("five_wicket_hauls"),
                    }
                )
