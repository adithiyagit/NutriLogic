from django.contrib import admin
from django.utils.html import format_html
from django.templatetags.static import static
from django.views.decorators.cache import never_cache
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.functional import cached_property
from django.forms import Media
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

class NutriLogicAdminSite(admin.AdminSite):
    """Custom admin site for NutriLogic with custom styling and behavior."""
    site_header = 'NutriLogic Administration'
    site_title = 'NutriLogic Admin'
    index_title = 'Welcome to NutriLogic Administration'
    site_url = '/'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.custom_index), name='index'),
            path('logout/', self.custom_logout, name='logout'),
        ]
        return custom_urls + urls
    
    def custom_logout(self, request):
        """
        Custom logout view that accepts both GET and POST requests.
        """
        from django.contrib.auth import logout as auth_logout
        from django.template.response import TemplateResponse
        
        # Log the user out
        auth_logout(request)
        
        # Render the logged out template
        context = {
            'site_header': self.site_header,
            'site_title': self.site_title,
            'site_url': self.site_url,
            'title': 'Logged out',
        }
        
        return TemplateResponse(request, 'admin/logged_out.html', context)
    
    def custom_index(self, request, extra_context=None):
        """
        Custom index view with statistics dashboard and visualizations.
        """
        from django.contrib.auth.models import User
        from meals.models import MealPlan, Food
        from health.models import HealthPrediction
        from premium.models import Subscription, Payment
        from users.models import Profile
        from django.db.models import Sum, Count, Q
        from django.utils import timezone
        from datetime import timedelta
        import json
        
        app_list = self.get_app_list(request)
        
        # Calculate statistics
        stats = {
            'total_users': User.objects.count(),
            'total_meal_plans': MealPlan.objects.count(),
            'total_predictions': HealthPrediction.objects.count(),
            'active_subscriptions': Subscription.objects.filter(status='A').count(),
            'total_foods': Food.objects.count(),
            'total_revenue': Payment.objects.filter(status='S').aggregate(
                total=Sum('amount')
            )['total'] or 0,
        }
        
        # User Activity Analysis - Goal Distribution
        goal_stats = Profile.objects.values('goal').annotate(count=Count('goal')).order_by('goal')
        goal_data = {
            'labels': [dict(Profile.GOAL_CHOICES).get(item['goal'], 'Unknown') for item in goal_stats],
            'values': [item['count'] for item in goal_stats],
        }
        
        # User Activity Analysis - Activity Level Distribution
        activity_stats = Profile.objects.values('activity_level').annotate(count=Count('activity_level')).order_by('activity_level')
        activity_data = {
            'labels': [dict(Profile.ACTIVITY_LEVEL_CHOICES).get(item['activity_level'], 'Unknown') for item in activity_stats],
            'values': [item['count'] for item in activity_stats],
        }
        
        # Gender Distribution
        gender_stats = Profile.objects.exclude(gender__isnull=True).values('gender').annotate(count=Count('gender')).order_by('gender')
        gender_data = {
            'labels': [dict(Profile.GENDER_CHOICES).get(item['gender'], 'Unknown') for item in gender_stats],
            'values': [item['count'] for item in gender_stats],
        }
        
        # Health Prediction Risk Distribution
        risk_stats = HealthPrediction.objects.values('risk_level').annotate(count=Count('risk_level')).order_by('risk_level')
        risk_data = {
            'labels': [dict(HealthPrediction.RISK_LEVELS).get(item['risk_level'], 'Unknown') for item in risk_stats],
            'values': [item['count'] for item in risk_stats],
        }
        
        # Health Condition Type Distribution
        condition_stats = HealthPrediction.objects.values('condition_type').annotate(count=Count('condition_type')).order_by('condition_type')
        condition_data = {
            'labels': [dict(HealthPrediction.CONDITION_TYPES).get(item['condition_type'], 'Unknown') for item in condition_stats],
            'values': [item['count'] for item in condition_stats],
        }
        
        # Subscription Status Distribution
        subscription_stats = Subscription.objects.values('status').annotate(count=Count('status')).order_by('status')
        subscription_choices = {
            'A': 'Active',
            'C': 'Cancelled',
            'E': 'Expired',
            'P': 'Pending',
        }
        subscription_data = {
            'labels': [subscription_choices.get(item['status'], 'Unknown') for item in subscription_stats],
            'values': [item['count'] for item in subscription_stats],
        }
        
        # User Registration Trend (Last 7 days)
        today = timezone.now().date()
        dates = [(today - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
        user_trend_data = {
            'labels': dates,
            'values': [
                User.objects.filter(date_joined__date=today - timedelta(days=i)).count()
                for i in range(6, -1, -1)
            ]
        }
        
        # Meal Plans Created (Last 7 days)
        meal_trend_data = {
            'labels': dates,
            'values': [
                MealPlan.objects.filter(date=today - timedelta(days=i)).count()
                for i in range(6, -1, -1)
            ]
        }
        
        # Payment Status Distribution
        payment_stats = Payment.objects.values('status').annotate(count=Count('status')).order_by('status')
        payment_choices = {
            'P': 'Pending',
            'S': 'Success',
            'F': 'Failed',
        }
        payment_data = {
            'labels': [payment_choices.get(item['status'], 'Unknown') for item in payment_stats],
            'values': [item['count'] for item in payment_stats],
        }
        
        # Convert to JSON for JavaScript
        chart_data = {
            'goal_data': json.dumps(goal_data),
            'activity_data': json.dumps(activity_data),
            'gender_data': json.dumps(gender_data),
            'risk_data': json.dumps(risk_data),
            'condition_data': json.dumps(condition_data),
            'subscription_data': json.dumps(subscription_data),
            'user_trend_data': json.dumps(user_trend_data),
            'meal_trend_data': json.dumps(meal_trend_data),
            'payment_data': json.dumps(payment_data),
        }
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            'stats': stats,
            'chart_data': chart_data,
            **(extra_context or {}),
        }
        
        request.current_app = self.name
        return TemplateResponse(request, 'admin/index.html', context)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ()
    
    def each_context(self, request):
        """Add custom context variables to the admin."""
        context = super().each_context(request)
        context.update({
            'site_header': self.site_header,
            'site_title': self.site_title,
            'site_url': self.site_url,
            'has_permission': request.user.is_active and request.user.is_staff,
            'available_apps': self.get_app_list(request),
        })
        return context

# Create an instance of our custom admin site
admin_site = NutriLogicAdminSite(name='nutrilogic_admin')
