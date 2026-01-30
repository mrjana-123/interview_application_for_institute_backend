from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login),
    path('dashboard/', views.dashboard),
    path('get_keys', views.get_keys),
    path('key_generate', views.generate_key),
    path('revoke_key', views.revoke_key),
    path('activation_code', views.activation_code),
    path('current-user', views.current_user),
    path('update_profile', views.update_profile),
    
]