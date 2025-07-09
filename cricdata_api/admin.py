# cricdata_api/admin.py
from django.contrib import admin

from .models import Player, Team

admin.site.register(Team)
admin.site.register(Player)