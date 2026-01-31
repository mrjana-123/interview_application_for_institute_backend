from django.urls import path
from . import views



# We added namespace for our app
app_name = 'Sadmin'
urlpatterns = [ 
    # path("superadmin_login",views.superadmin_login),
    path("create_admin",views.create_admin),
    path("admin_list", views.get_admins, name="admin_list"),
    
    
    path("change_admin_status", views.change_admin_status, name="admin_list"),            
               
]
