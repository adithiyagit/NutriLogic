from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_home, name='health_home'),
    path('predict/', views.predict_health, name='predict_health'),
    path('results/', views.health_results, name='health_results'),
    path('history/', views.prediction_history, name='prediction_history'),
]