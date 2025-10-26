from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import Profile

# Import custom admin site
from nutrilogic.admin_customization import admin_site

# Register User and Group with custom admin site
admin_site.register(User, BaseUserAdmin)
admin_site.register(Group)

# Profile Admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ['image', 'age', 'gender', 'height', 'weight', 'activity_level', 'goal', 'daily_water_target', 'daily_calorie_target']
    readonly_fields = ['daily_calorie_target']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'height', 'weight', 'daily_calorie_target', 'activity_level', 'goal']
    list_filter = ['gender', 'activity_level', 'goal']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['daily_calorie_target']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('image', 'age', 'gender', 'height', 'weight')
        }),
        ('Health & Fitness', {
            'fields': ('activity_level', 'goal', 'daily_water_target', 'daily_calorie_target')
        }),
    )

admin_site.register(Profile, ProfileAdmin)
