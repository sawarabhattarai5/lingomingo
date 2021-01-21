from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<uuid:profile_uuid>/', views.profile, name='profile'),
    path('profile/edit/', views.profile_settings, name='edit_profile'),
    path('register/', views.register, name='register'),
    path('settings/', views.settings, name='settings'),
    path('friends/', views.friends, name='friends'),
    path('setup/', views.setup, name='setup'),
]
