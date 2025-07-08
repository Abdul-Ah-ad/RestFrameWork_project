# from django.urls import path
# from cricdata_api.views import (FetchTeamsPlayersView,TeamListView, PlayerListView,Best)

# urlpatterns = [
#     path('teams/', TeamListView.as_view(), name='team-list'),
#     path('players/', PlayerListView.as_view(), name='player-list'),
#     path('fetch_teams_players/', FetchTeamsPlayersView.as_view(), name='fetch-teams-players'),
#     path('best/', Best.as_view(), name='best-xi'),
#]
# cricdata_api/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cricdata_api.viewsets import (ImportDataViewSet, PlayerViewSet,
                                   TeamAnalysisViewSet, TeamViewSet)

router = DefaultRouter()
router.register('teams', TeamViewSet, basename='team')
router.register('players', PlayerViewSet, basename='player')
router.register('import', ImportDataViewSet, basename='import')
router.register('analysis', TeamAnalysisViewSet, basename='analysis')  # ✅ IMPORTANT

urlpatterns = [
    path('', include(router.urls)),
]
