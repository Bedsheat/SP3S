from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update-profile/', views.update_profile_view, name='update_profile'),
    path('upload-resume/', views.upload_resume_view, name='upload_resume'),
    path('api/parse-resume/', views.parse_resume_api, name='parse_resume_api'),
    path('api/llm-status/', views.llm_status_api, name='llm_status_api'),
]
