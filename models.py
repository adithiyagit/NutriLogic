from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image

# Create your models here.
class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('S', 'Sedentary (little or no exercise)'),
        ('L', 'Lightly active (light exercise/sports 1-3 days/week)'),
        ('M', 'Moderately active (moderate exercise/sports 3-5 days/week)'),
        ('V', 'Very active (hard exercise/sports 6-7 days a week)'),
        ('E', 'Extra active (very hard exercise, physical job or training twice a day)'),
    ]
    
    GOAL_CHOICES = [
        ('L', 'Lose weight'),
        ('M', 'Maintain weight'),
        ('G', 'Gain weight'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    age = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(120)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(50), MaxValueValidator(300)], help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(20), MaxValueValidator(500)], help_text="Weight in kg")
    activity_level = models.CharField(max_length=1, choices=ACTIVITY_LEVEL_CHOICES, default='M')
    goal = models.CharField(max_length=1, choices=GOAL_CHOICES, default='M')
    daily_water_target = models.PositiveIntegerField(default=8, help_text="Target number of glasses per day")
    daily_calorie_target = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def calculate_bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to m
            return self.weight / (height_m * height_m)
        return None
    
    def save(self, *args, **kwargs):
        # Calculate daily calorie target before saving if height and weight are provided
        if self.height and self.weight and self.age and self.gender:
            # Calculate BMI
            bmi = self.calculate_bmi()
            
            # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
            if self.gender == 'M':
                bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
            else:
                bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
            
            # Apply activity factor
            activity_factors = {
                'S': 1.2,
                'L': 1.375,
                'M': 1.55,
                'V': 1.725,
                'E': 1.9
            }
            
            maintenance_calories = bmr * activity_factors[self.activity_level]
            
            # Adjust based on goal
            if self.goal == 'L':
                self.daily_calorie_target = int(maintenance_calories * 0.85)  # 15% deficit
            elif self.goal == 'G':
                self.daily_calorie_target = int(maintenance_calories * 1.15)  # 15% surplus
            else:
                self.daily_calorie_target = int(maintenance_calories)
        
        # Save the model first
        super().save(*args, **kwargs)
        
        # Resize profile image if it exists
        try:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
        except (FileNotFoundError, ValueError, AttributeError):
            # If the image file doesn't exist or there's an issue, skip resizing
            pass
