"""
Middleware to check if user profile is complete and show notifications
"""
from django.contrib import messages
from django.urls import reverse


class ProfileCompletionMiddleware:
    """
    Middleware to check if logged-in users have completed their profile.
    Shows a persistent warning message if profile is incomplete.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request before the view
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            # Check if profile is complete
            profile = request.user.profile
            
            # Skip check for certain URLs
            exempt_urls = [
                reverse('profile'),
                reverse('logout'),
                '/admin/',
            ]
            
            # Check if current path should be exempt
            is_exempt = any(request.path.startswith(url) for url in exempt_urls)
            
            # Only show message if not on exempt pages and profile is incomplete
            if not is_exempt:
                profile_incomplete = (
                    not profile.age or 
                    not profile.height or 
                    not profile.weight or 
                    not profile.gender
                )
                
                if profile_incomplete:
                    # Check if we've already shown this message in this session
                    # to avoid showing it multiple times
                    if not request.session.get('profile_incomplete_shown', False):
                        messages.warning(
                            request,
                            '⚠️ Please complete your profile with health details (age, height, weight, gender) '
                            'to unlock all features and get personalized recommendations. '
                            '<a href="/users/profile/" class="alert-link fw-bold">Update Profile Now</a>',
                            extra_tags='safe'
                        )
                        request.session['profile_incomplete_shown'] = True
        
        response = self.get_response(request)
        return response

