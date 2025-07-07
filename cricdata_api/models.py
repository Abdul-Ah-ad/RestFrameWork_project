from django.db import models
from django.utils import timezone

class Team(models.Model):
    team_id = models.IntegerField(unique=True)  # Still unique per team
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20, blank=True)
    country_name = models.CharField(max_length=100, blank=True, null=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    player_id = models.IntegerField()  # ❌ No unique=True here anymore
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    format = models.CharField(
        max_length=10,
        choices=(('odi', 'ODI'), ('test', 'Test'), ('t20', 'T20'), ('unknown', 'Unknown')),
        default='unknown'
    )

    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    batting_style = models.CharField(max_length=100, blank=True, null=True)
    bowling_style = models.CharField(max_length=100, blank=True, null=True)

    # Batting stats
    matches = models.IntegerField(null=True, blank=True)
    innings = models.IntegerField(null=True, blank=True)
    runs = models.IntegerField(null=True, blank=True)
    batting_average = models.FloatField(null=True, blank=True)
    strike_rate = models.FloatField(null=True, blank=True)
    fifties = models.IntegerField(null=True, blank=True)
    hundreds = models.IntegerField(null=True, blank=True)

    # Bowling stats
    overs = models.FloatField(null=True, blank=True)
    wickets = models.IntegerField(null=True, blank=True)
    economy = models.FloatField(null=True, blank=True)
    bowling_average = models.FloatField(null=True, blank=True)
    five_wicket_hauls = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('player_id', 'format')  # ✅ This allows same player for different formats

    def __str__(self):
        return f"{self.name} ({self.format})"
