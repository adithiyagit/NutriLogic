from django import forms
from .models import MealPlan, MealFood, Food, FoodCategory

class FoodForm(forms.ModelForm):
    """Form for adding custom food items"""
    class Meta:
        model = Food
        fields = ['name', 'category', 'calories', 'protein', 'carbs', 'fats', 'fiber']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Homemade Curry'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calories per 100g',
                'min': '0'
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Protein in grams per 100g',
                'min': '0',
                'step': '0.1'
            }),
            'carbs': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Carbs in grams per 100g',
                'min': '0',
                'step': '0.1'
            }),
            'fats': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fats in grams per 100g',
                'min': '0',
                'step': '0.1'
            }),
            'fiber': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fiber in grams per 100g',
                'min': '0',
                'step': '0.1'
            }),
        }
        labels = {
            'name': 'Food Name',
            'category': 'Food Category',
            'calories': 'Calories (per 100g)',
            'protein': 'Protein (g per 100g)',
            'carbs': 'Carbohydrates (g per 100g)',
            'fats': 'Fats (g per 100g)',
            'fiber': 'Fiber (g per 100g)'
        }

class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['name', 'date', 'meal_type', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., My Breakfast Plan'}),
            'meal_type': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add any notes or preferences...'}),
        }

class MealFoodForm(forms.ModelForm):
    # Add search field for food
    food_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Search for food items...',
            'id': 'food-search'
        }),
        label='Search Food'
    )
    
    # Add category filter
    category = forms.ModelChoiceField(
        queryset=FoodCategory.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select mb-3', 'id': 'category-filter'}),
        label='Filter by Category'
    )
    
    class Meta:
        model = MealFood
        fields = ['food', 'quantity']
        widgets = {
            'food': forms.Select(attrs={
                'class': 'form-select',
                'id': 'food-select',
                'size': '10'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1',
                'value': '100',
                'placeholder': 'Quantity in grams'
            }),
        }
        labels = {
            'food': 'Select Food Item',
            'quantity': 'Quantity (grams)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order foods alphabetically
        self.fields['food'].queryset = Food.objects.all().order_by('name')