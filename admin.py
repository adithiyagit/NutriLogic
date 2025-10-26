from django.contrib import admin
from .models import HealthPrediction

# Import custom admin site
from nutrilogic.admin_customization import admin_site

# Register your models here.

class HealthPredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'condition_type', 'risk_level', 'prediction_score', 'prediction_date']
    list_filter = ['condition_type', 'risk_level', 'prediction_date']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['prediction_date', 'prediction_score', 'input_data']
    date_hierarchy = 'prediction_date'
    ordering = ['-prediction_date']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Prediction Details', {
            'fields': ('condition_type', 'risk_level', 'prediction_score', 'prediction_date')
        }),
        ('Input Data', {
            'fields': ('input_data',),
            'classes': ('collapse',)
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
    )
    
    def get_risk_level_display_with_color(self, obj):
        colors = {
            'L': 'green',
            'M': 'orange',
            'H': 'red'
        }
        color = colors.get(obj.risk_level, 'black')
        return f'<span style="color: {color}; font-weight: bold;">{obj.get_risk_level_display()}</span>'
    get_risk_level_display_with_color.allow_tags = True
    get_risk_level_display_with_color.short_description = 'Risk Level'

admin_site.register(HealthPrediction, HealthPredictionAdmin)
