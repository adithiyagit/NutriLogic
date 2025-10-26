from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FoodCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Food Categories"

class Food(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='foods')
    calories = models.PositiveIntegerField(help_text="Calories per 100g")
    protein = models.FloatField(help_text="Protein in grams per 100g")
    carbs = models.FloatField(help_text="Carbohydrates in grams per 100g")
    fats = models.FloatField(help_text="Fats in grams per 100g")
    fiber = models.FloatField(help_text="Fiber in grams per 100g", default=0)
    image = models.ImageField(upload_to='food_images', default='default_food.jpg')
    
    def __str__(self):
        return self.name

class MealPlan(models.Model):
    MEAL_TYPE_CHOICES = [
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
        ('S', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    name = models.CharField(max_length=100)
    date = models.DateField()
    meal_type = models.CharField(max_length=1, choices=MEAL_TYPE_CHOICES)
    foods = models.ManyToManyField(Food, through='MealFood')
    is_consumed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_meal_type_display()} ({self.date})"
    
    @property
    def total_calories(self):
        return sum(meal_food.calories for meal_food in self.meal_foods.all())
    
    @property
    def total_protein(self):
        return sum(meal_food.protein for meal_food in self.meal_foods.all())
    
    @property
    def total_carbs(self):
        return sum(meal_food.carbs for meal_food in self.meal_foods.all())
    
    @property
    def total_fats(self):
        return sum(meal_food.fats for meal_food in self.meal_foods.all())

class MealFood(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meal_foods')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Quantity in grams")
    
    def __str__(self):
        return f"{self.food.name} ({self.quantity}g) in {self.meal_plan.name}"
    
    @property
    def calories(self):
        return (self.food.calories * self.quantity) / 100
    
    @property
    def protein(self):
        return (self.food.protein * self.quantity) / 100
    
    @property
    def carbs(self):
        return (self.food.carbs * self.quantity) / 100
    
    @property
    def fats(self):
        return (self.food.fats * self.quantity) / 100
