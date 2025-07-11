"""
Defines all the URL routes for the cricdata_api application using DRF routers.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cricdata_api.viewsets import (InjectDataViewSet, PlayerViewSet,TeamAnalysisViewSet, TeamViewSet)

router = DefaultRouter()
router.register('teams', TeamViewSet, basename='team')
router.register('players', PlayerViewSet, basename='player')
router.register('inject-teams-data', InjectDataViewSet, basename='inject-data')
router.register('team-analysis', TeamAnalysisViewSet, basename='team-analysis')

urlpatterns = [path('', include(router.urls)),]

