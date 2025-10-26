from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Food, MealPlan, MealFood, FoodCategory
from .forms import MealPlanForm, MealFoodForm, FoodForm
from django.db.models import Sum

# Create your views here.
def meal_home(request):
    return render(request, 'meals/meal_home.html')

@login_required
def meal_plans(request):
    today = timezone.now().date()
    meal_plans = MealPlan.objects.filter(user=request.user, date=today).order_by('meal_type')
    
    # Calculate daily totals
    daily_totals = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fats': 0
    }
    
    for plan in meal_plans:
        daily_totals['calories'] += plan.total_calories
        daily_totals['protein'] += plan.total_protein
        daily_totals['carbs'] += plan.total_carbs
        daily_totals['fats'] += plan.total_fats
    
    # Calculate percentage of daily goal
    if hasattr(request.user, 'profile') and request.user.profile.daily_calorie_target:
        daily_totals['calorie_percentage'] = (daily_totals['calories'] / request.user.profile.daily_calorie_target) * 100
    else:
        daily_totals['calorie_percentage'] = 0
    
    context = {
        'meal_plans': meal_plans,
        'daily_totals': daily_totals,
        'today': today
    }
    return render(request, 'meals/meal_plans.html', context)

@login_required
def create_meal_plan(request):
    """Simplified meal creation - directly add foods, auto-create meal plan"""
    from datetime import date
    
    # Get or create today's meal plan based on meal type
    meal_type = request.GET.get('meal_type', 'B')  # Default to Breakfast
    today = timezone.now().date()
    
    # Try to get existing meal plan for today and meal type
    meal_plan = MealPlan.objects.filter(
        user=request.user,
        date=today,
        meal_type=meal_type
    ).first()
    
    # If no meal plan exists, create one automatically
    if not meal_plan:
        meal_type_names = {'B': 'Breakfast', 'L': 'Lunch', 'D': 'Dinner', 'S': 'Snack'}
        meal_plan = MealPlan.objects.create(
            user=request.user,
            name=f"{meal_type_names[meal_type]} - {today.strftime('%b %d')}",
            date=today,
            meal_type=meal_type
        )
    
    # Handle food addition
    if request.method == 'POST' and 'add_food' in request.POST:
        food_form = MealFoodForm(request.POST)
        if food_form.is_valid():
            meal_food = food_form.save(commit=False)
            meal_food.meal_plan = meal_plan
            meal_food.save()
            messages.success(request, f'{meal_food.food.name} ({meal_food.quantity}g) added!')
            return redirect(f'/meals/create/?meal_type={meal_type}')
    
    # Handle food removal
    elif request.method == 'POST' and 'remove_food' in request.POST:
        food_id = request.POST.get('food_id')
        MealFood.objects.filter(id=food_id, meal_plan=meal_plan).delete()
        messages.info(request, 'Food item removed.')
        return redirect(f'/meals/create/?meal_type={meal_type}')
    
    # Initialize forms
    food_form = MealFoodForm()
    
    # Get search and filter parameters for foods
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    # Filter foods
    foods = Food.objects.all().order_by('name')
    if search_query:
        foods = foods.filter(name__icontains=search_query)
    if category_id:
        foods = foods.filter(category_id=category_id)
    
    # Get meal foods
    meal_foods = MealFood.objects.filter(meal_plan=meal_plan)
    
    # Calculate totals
    total_calories = sum(mf.calories for mf in meal_foods)
    total_protein = sum(mf.protein for mf in meal_foods)
    total_carbs = sum(mf.carbs for mf in meal_foods)
    total_fats = sum(mf.fats for mf in meal_foods)
    
    context = {
        'food_form': food_form,
        'meal_plan': meal_plan,
        'meal_foods': meal_foods,
        'foods': foods,
        'search_query': search_query,
        'category_id': category_id,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fats': total_fats,
        'current_meal_type': meal_type,
        'title': f'Add Foods to {meal_plan.get_meal_type_display()}'
    }
    return render(request, 'meals/create_meal_simple.html', context)

# Removed old add_food_to_meal view - no longer needed

@login_required
def meal_detail(request, meal_plan_id):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, user=request.user)
    meal_foods = MealFood.objects.filter(meal_plan=meal_plan)
    
    # Calculate macronutrient calories
    # Protein: 4 kcal/g, Carbs: 4 kcal/g, Fats: 9 kcal/g
    protein_calories = meal_plan.total_protein * 4
    carbs_calories = meal_plan.total_carbs * 4
    fats_calories = meal_plan.total_fats * 9
    
    context = {
        'meal_plan': meal_plan,
        'meal_foods': meal_foods,
        'protein_calories': protein_calories,
        'carbs_calories': carbs_calories,
        'fats_calories': fats_calories,
    }
    return render(request, 'meals/meal_detail.html', context)

@login_required
def toggle_consumed(request, meal_plan_id):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id, user=request.user)
    meal_plan.is_consumed = not meal_plan.is_consumed
    meal_plan.save()
    
    if meal_plan.is_consumed:
        messages.success(request, f'Meal "{meal_plan.name}" marked as consumed!')
    else:
        messages.info(request, f'Meal "{meal_plan.name}" marked as not consumed.')
    
    return redirect('meal_plans')

# Removed recommend_meal view - using AI recommendations instead
@login_required
def ai_recommend_meals(request):
    """AI-powered meal recommendations using Random Forest - PREMIUM FEATURE"""
    # Check premium subscription
    try:
        subscription = request.user.subscription
        if not subscription.is_active():
            messages.warning(request, 'AI Recommendations is a premium feature. Please subscribe to access it.')
            return redirect('premium-home')
    except:
        messages.warning(request, 'AI Recommendations is a premium feature. Please subscribe to access it.')
        return redirect('premium-home')
    
    # Ensure user has a profile
    if not hasattr(request.user, 'profile'):
        messages.warning(request, 'Please complete your profile first.')
        return redirect('profile')
    
    profile = request.user.profile
    
    # Check if profile has required data
    if not all([profile.age, profile.height, profile.weight, profile.gender]):
        messages.warning(request, 'Please complete your profile with age, height, weight, and gender to get AI recommendations.')
        return redirect('profile')
    
    try:
        from .recommender import MealRecommender
        
        # Use actual user data - NO DEFAULTS
        user_data = {
            'age': int(profile.age),
            'gender': 'Male' if profile.gender == 'M' else ('Female' if profile.gender == 'F' else 'Other'),
            'height': float(profile.height),
            'weight': float(profile.weight),
            'goal': profile.goal if profile.goal else 'M',
            'activity_level': profile.activity_level if profile.activity_level else 'M',
        }
        
        recommender = MealRecommender()
        recommendations = recommender.get_recommendations(user_data, num_recommendations=15)
        
        # Calculate actual BMI
        bmi = profile.calculate_bmi()
        
        context = {
            'recommendations': recommendations,
            'profile': profile,
            'bmi': bmi,
            'user_data': user_data,  # Pass to template for debugging
        }
        
        return render(request, 'meals/ai_recommendations.html', context)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('meal_plans')

@login_required
def search_foods_api(request):
    """API endpoint for searching foods"""
    from django.http import JsonResponse
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'foods': [], 'message': 'Type at least 2 characters to search'})
    
    # Search foods by name
    foods = Food.objects.filter(name__icontains=query).select_related('category')[:20]
    
    foods_data = [{
        'id': food.id,
        'name': food.name,
        'category': food.category.name,
        'calories': food.calories,
        'protein': float(food.protein),
        'carbs': float(food.carbs),
        'fats': float(food.fats)
    } for food in foods]
    
    message = f'Found {len(foods_data)} foods' if foods_data else f'No foods found for "{query}"'
    
    return JsonResponse({
        'foods': foods_data,
        'message': message,
        'total': len(foods_data)
    })

# Removed add_custom_food and manage_foods views - using Django admin instead