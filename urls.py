from django.urls import path
from . import views

urlpatterns = [
    path('', views.meal_home, name='meal_home'),
    path('plans/', views.meal_plans, name='meal_plans'),
    path('create/', views.create_meal_plan, name='create_meal_plan'),
    path('plan/<int:meal_plan_id>/', views.meal_detail, name='meal_detail'),
    path('plan/<int:meal_plan_id>/toggle-consumed/', views.toggle_consumed, name='toggle_consumed'),
    path('ai-recommendations/', views.ai_recommend_meals, name='ai_recommend_meals'),
    path('api/search-foods/', views.search_foods_api, name='search_foods_api'),
]