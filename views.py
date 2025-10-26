from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from meals.models import MealPlan, MealFood
from health.models import HealthPrediction
from django.db.models import Sum, Avg
from django.utils import timezone
import json
from datetime import timedelta

# Create your views here.
@login_required
def dashboard_home(request):
    """Dashboard - PREMIUM FEATURE"""
    # Check premium subscription
    try:
        subscription = request.user.subscription
        if not subscription.is_active():
            messages.warning(request, 'Dashboard is a premium feature. Please subscribe to access it.')
            return redirect('premium-home')
    except:
        messages.warning(request, 'Dashboard is a premium feature. Please subscribe to access it.')
        return redirect('premium-home')
    
    # Get user's meal plans for the last 7 days
    last_week = timezone.now() - timedelta(days=7)
    meal_plans = MealPlan.objects.filter(
        user=request.user,
        date__gte=last_week
    ).order_by('date')
    
    # Calculate daily calories
    daily_calories = []
    daily_labels = []
    
    for meal_plan in meal_plans:
        daily_calories.append(meal_plan.total_calories)
        daily_labels.append(meal_plan.date.strftime('%m/%d'))
    
    # Get macronutrient distribution
    total_macros = MealFood.objects.filter(
        meal_plan__user=request.user,
        meal_plan__date__gte=last_week
    ).aggregate(
        total_protein=Sum('food__protein'),
        total_carbs=Sum('food__carbs'),
        total_fats=Sum('food__fats')
    )
    
    # Prepare macros data for pie chart
    macros_data = []
    macros_labels = ['Protein', 'Carbs', 'Fats']
    
    if total_macros['total_protein'] is not None:
        macros_data = [
            total_macros['total_protein'],
            total_macros['total_carbs'],
            total_macros['total_fats']
        ]
    
    # Get health predictions (don't slice yet so we can filter)
    health_predictions_qs = HealthPrediction.objects.filter(
        user=request.user
    ).order_by('-prediction_date')
    
    # Prepare health prediction data
    prediction_data = {
        'obesity': [],
        'diabetes': [],
        'heart_disease': [],
        'nutrient_deficiency': []
    }
    prediction_labels = []
    
    for prediction in health_predictions_qs[:20]:
        if prediction.condition_type == 'obesity' and len(prediction_labels) < 5:
            prediction_labels.append(prediction.prediction_date.strftime('%m/%d'))
    
    for condition in prediction_data.keys():
        condition_predictions = health_predictions_qs.filter(condition_type=condition)[:5]
        for pred in condition_predictions:
            prediction_data[condition].append(pred.prediction_score)
    
    # Reverse the lists to show chronological order
    prediction_labels.reverse()
    for condition in prediction_data.keys():
        prediction_data[condition].reverse()
    
    context = {
        'daily_calories': json.dumps(daily_calories),
        'daily_labels': json.dumps(daily_labels),
        'macros_data': json.dumps(macros_data),
        'macros_labels': json.dumps(macros_labels),
        'prediction_data': json.dumps(prediction_data),
        'prediction_labels': json.dumps(prediction_labels),
        'meal_plans': meal_plans,
        'health_predictions': health_predictions_qs[:5]
    }
    
    return render(request, 'dashboard/dashboard_home.html', context)
