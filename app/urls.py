from django.urls import path
from . import views

urlpatterns = [
    path('super_admin_login', views.super_admin_login),
    path('login', views.login),
    path('dashboard/', views.dashboard),
    path('get_keys', views.get_keys),
    path('key_generate', views.generate_key),
    
    path('revoke_key', views.revoke_key),
    
    path('sender_revoke_key', views.sender_revoke_key),
    
    path('activation_code', views.activation_code),
    path('current-user', views.current_user),
    path('update_profile', views.update_profile),
    path("super-admin/dashboard",views.super_admin_dashboarded),
    # path("super_admin_generate_key",views.super_admin_generate_key),
    path("add-admin/", views.add_admin),
    path("get-admins/", views.get_admins),
    
    path("update-admin/", views.update_admin),
    path("delete-admin/", views.delete_admin),
    path("admin/keys/", views.get_admin_keys),
    
    
    path("delete_key/", views.delete_key),
    path("sender_revoke_key", views.sender_revoke_key),
    path("super_admin_generate_key/", views.super_admin_generate_key),
    
    path("get_admin_details/", views.get_admin_details),
    
    
    
    
    
    path("activated_key_for_sender", views.activated_key_for_sender),
    path("activated_key_for_receiver", views.activated_key_for_receiver),
    
    
    path("super-admin/dashboard/cards/", views.super_admin_dashboard_cards),
    
    path("change_password", views.change_password),
    
  
    path("notifications/", views.get_notifications),

    path("notifications/read/<str:notification_id>/", views.mark_notification_read),
    path("notifications/read-all/", views.mark_all_notifications_read),


    
]

