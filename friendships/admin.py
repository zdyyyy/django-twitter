from django.contrib import admin
from friendships.models import Friendship

# Register your models here.
@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id','from_user_id','to_user_id','created_at')
    data_hierarchy = 'created_at'
