from django.contrib import admin
from .models import Food, FoodCategory, MealPlan, MealFood

# Import custom admin site
from nutrilogic.admin_customization import admin_site

# Register your models here.

class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories', 'protein', 'carbs', 'fats']
    list_filter = ['category']
    search_fields = ['name']
    list_per_page = 50

class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'date', 'meal_type', 'is_consumed']
    list_filter = ['meal_type', 'is_consumed', 'date']
    search_fields = ['name', 'user__username']
    date_hierarchy = 'date'
    readonly_fields = ['total_calories', 'total_protein', 'total_carbs', 'total_fats']
    
    def total_calories(self, obj):
        return f"{obj.total_calories:.2f} kcal"
    total_calories.short_description = 'Total Calories'
    
    def total_protein(self, obj):
        return f"{obj.total_protein:.2f}g"
    total_protein.short_description = 'Total Protein'
    
    def total_carbs(self, obj):
        return f"{obj.total_carbs:.2f}g"
    total_carbs.short_description = 'Total Carbs'
    
    def total_fats(self, obj):
        return f"{obj.total_fats:.2f}g"
    total_fats.short_description = 'Total Fats'

class MealFoodAdmin(admin.ModelAdmin):
    list_display = ['meal_plan', 'food', 'quantity', 'display_calories']
    list_filter = ['meal_plan__meal_type']
    search_fields = ['meal_plan__name', 'food__name']
    
    def display_calories(self, obj):
        return f"{obj.calories:.2f} kcal"
    display_calories.short_description = 'Calories'

# Register with custom admin site
admin_site.register(FoodCategory, FoodCategoryAdmin)
admin_site.register(Food, FoodAdmin)
admin_site.register(MealPlan, MealPlanAdmin)
admin_site.register(MealFood, MealFoodAdmin)
