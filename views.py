from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HealthPrediction
from .ml_model import predictor
from users.models import Profile

# Create your views here.
@login_required
def health_home(request):
    # Get user's recent predictions
    predictions = HealthPrediction.objects.filter(user=request.user).order_by('-prediction_date')[:5]
    return render(request, 'health/health_home.html', {'predictions': predictions})

@login_required
def predict_health(request):
    """Health prediction - PREMIUM FEATURE"""
    # Check premium subscription
    try:
        subscription = request.user.subscription
        if not subscription.is_active():
            messages.warning(request, 'Health Predictions is a premium feature. Please subscribe to access it.')
            return redirect('premium-home')
    except:
        messages.warning(request, 'Health Predictions is a premium feature. Please subscribe to access it.')
        return redirect('premium-home')
    
    if request.method == 'POST':
        try:
            # Get user profile data
            profile = Profile.objects.get(user=request.user)
            
            # Calculate BMI
            bmi = profile.calculate_bmi()
            
            # Get activity level (convert to 0-1 scale)
            activity_mapping = {
                'S': 0.2,  # Sedentary
                'L': 0.4,  # Light
                'M': 0.6,  # Moderate
                'A': 0.8,  # Active
                'V': 1.0   # Very Active
            }
            activity_level = activity_mapping.get(profile.activity_level, 0.5)
            
            # Get diet score from form
            diet_score = float(request.POST.get('diet_score', 0.5))
            
            # Calculate calorie ratio (consumed/target)
            calorie_ratio = float(request.POST.get('calorie_ratio', 1.0))
            
            # Prepare input data
            user_data = {
                'age': profile.age,
                'bmi': bmi,
                'activity_level': activity_level,
                'diet_score': diet_score,
                'calorie_ratio': calorie_ratio
            }
            
            # Get predictions
            results = predictor.predict(user_data)
            
            # Save predictions to database
            for condition, (risk, score) in results.items():
                HealthPrediction.objects.create(
                    user=request.user,
                    condition_type=condition,
                    risk_level=risk,
                    prediction_score=score,
                    input_data=user_data,
                )
            
            messages.success(request, 'Health predictions generated successfully!')
            return redirect('health_results')
            
        except Exception as e:
            messages.error(request, f'Error generating predictions: {str(e)}')
    
    return render(request, 'health/predict_form.html')

@login_required
def health_results(request):
    """Health results - PREMIUM FEATURE"""
    # Check premium subscription
    try:
        subscription = request.user.subscription
        if not subscription.is_active():
            messages.warning(request, 'Health Predictions is a premium feature. Please subscribe to access it.')
            return redirect('premium-home')
    except:
        messages.warning(request, 'Health Predictions is a premium feature. Please subscribe to access it.')
        return redirect('premium-home')
    
    # Get user's latest predictions for each condition
    latest_predictions = {}
    
    for condition in ['obesity', 'diabetes', 'heart_disease', 'nutrient_deficiency']:
        try:
            pred = HealthPrediction.objects.filter(
                user=request.user, 
                condition_type=condition
            ).latest('prediction_date')
            latest_predictions[condition] = pred
        except HealthPrediction.DoesNotExist:
            latest_predictions[condition] = None
    
    return render(request, 'health/health_results.html', {
        'predictions': latest_predictions
    })

@login_required
def prediction_history(request):
    """Prediction history - PREMIUM FEATURE"""
    # Check premium subscription
    try:
        subscription = request.user.subscription
        if not subscription.is_active():
            messages.warning(request, 'Health Predictions is a premium feature. Please subscribe to access it.')
            return redirect('premium-home')
    except:
        messages.warning(request, 'Health Predictions is a premium feature. Please subscribe to access it.')
        return redirect('premium-home')
    
    # Get all user's predictions grouped by date
    predictions = HealthPrediction.objects.filter(user=request.user).order_by('-prediction_date')
    
    return render(request, 'health/prediction_history.html', {
        'predictions': predictions
    })
