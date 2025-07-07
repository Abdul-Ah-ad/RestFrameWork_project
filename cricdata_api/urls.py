from django.urls import path
from cricdata_api.views import (FetchTeamsPlayersView,TeamListView, PlayerListView,Best)

urlpatterns = [
    path('teams/', TeamListView.as_view(), name='team-list'),
    path('players/', PlayerListView.as_view(), name='player-list'),
    path('fetch_teams_players/', FetchTeamsPlayersView.as_view(), name='fetch-teams-players'),
    path('best/', Best.as_view(), name='best-xi'),
]
