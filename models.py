from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class HealthPrediction(models.Model):
    CONDITION_CHOICES = [
        ('OB', 'Obesity'),
        ('DB', 'Diabetes'),
        ('HD', 'Heart Disease'),
        ('ND', 'Nutrient Deficiency'),
    ]
    
    RISK_LEVELS = [
        ('L', 'Low Risk'),
        ('M', 'Moderate Risk'),
        ('H', 'High Risk'),
    ]
    
    CONDITION_TYPES = [
        ('obesity', 'Obesity'),
        ('diabetes', 'Diabetes'),
        ('heart_disease', 'Heart Disease'),
        ('nutrient_deficiency', 'Nutrient Deficiency'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_predictions')
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES)
    risk_level = models.CharField(max_length=1, choices=RISK_LEVELS)
    prediction_date = models.DateTimeField(default=timezone.now)
    prediction_score = models.FloatField(default=0.0, help_text="ML model prediction score (0-1)")
    input_data = models.JSONField(blank=True, null=True, help_text="Input data used for prediction")
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_condition_type_display()} ({self.get_risk_level_display()})"
    
    class Meta:
        ordering = ['-prediction_date']
