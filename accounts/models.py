from accounts.listeners import profile_changed
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete
from utils.listeners import invalidate_object_cache
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete = models.SET_NULL,null = True)
    avatar = models.FileField(null=True)
    nickname = models.CharField(null=True,max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {}".format(self.user,self.nickname)

def get_profile(user):
    if hasattr(user,'_cached_user_profile'):
        return getattr(user,'_cached_user_profile')

    profile, _ = UserProfile.objects.get_or_create(user=user)
    setattr(user,'_cached_user_profile',profile)
    return profile

User.profile = property(get_profile)

# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_object_cache, sender=User)
post_save.connect(invalidate_object_cache, sender=User)

pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)