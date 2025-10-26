from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

# Create your views here.
def home(request):
    """View function for the home page of the site."""
    return render(request, 'users/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    # Ensure user has a profile
    try:
        profile = request.user.profile
    except:
        from .models import Profile
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        # Debug: Check if image is in request
        if 'image' in request.FILES:
            print(f"Image file received: {request.FILES['image'].name}")
        else:
            print("No image file in request")
        
        if u_form.is_valid() and p_form.is_valid():
            # Save user form
            u_form.save()
            
            # Save profile form - this will handle the image upload automatically
            saved_profile = p_form.save()
            print(f"Profile saved. Image path: {saved_profile.image.path if saved_profile.image else 'No image'}")
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            # Show validation errors
            if not u_form.is_valid():
                for field, errors in u_form.errors.items():
                    for error in errors:
                        messages.error(request, f'User {field}: {error}')
            if not p_form.is_valid():
                for field, errors in p_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Profile {field}: {error}')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
        
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)

def logout_view(request):
    """Logout view - logs out the user and shows logout page"""
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return render(request, 'users/logout.html')
