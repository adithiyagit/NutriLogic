import numpy as np
import joblib
import os
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class HealthPredictor:
    """Simple ML model for health condition prediction"""
    
    def __init__(self):
        self.models = {
            'obesity': self._get_model('obesity'),
            'diabetes': self._get_model('diabetes'),
            'heart_disease': self._get_model('heart_disease'),
            'nutrient_deficiency': self._get_model('nutrient_deficiency')
        }
        self.scaler = StandardScaler()
        
    def _get_model(self, condition_type):
        """Get or create a model for the specified condition"""
        model_path = os.path.join(settings.BASE_DIR, f'health/ml_models/{condition_type}_model.joblib')
        
        # If model exists, load it
        if os.path.exists(model_path):
            try:
                return joblib.load(model_path)
            except:
                pass
                
        # Create a simple model (for demonstration)
        return self._create_demo_model(condition_type)
    
    def _create_demo_model(self, condition_type):
        """Create a simple demonstration model"""
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        
        # Train with dummy data
        X = np.random.rand(100, 5)  # 5 features: age, bmi, activity, diet_score, calorie_ratio
        
        # Different logic for different conditions
        if condition_type == 'obesity':
            y = (X[:, 1] > 0.7).astype(int)  # High BMI -> obesity risk
        elif condition_type == 'diabetes':
            y = ((X[:, 1] > 0.6) & (X[:, 3] < 0.4)).astype(int)  # High BMI + poor diet -> diabetes risk
        elif condition_type == 'heart_disease':
            y = ((X[:, 1] > 0.6) & (X[:, 2] < 0.3)).astype(int)  # High BMI + low activity -> heart disease risk
        else:  # nutrient_deficiency
            y = (X[:, 3] < 0.3).astype(int)  # Poor diet -> nutrient deficiency risk
            
        model.fit(X, y)
        return model
    
    def predict(self, user_data):
        """
        Predict health risks based on user data
        
        Args:
            user_data: dict with keys 'age', 'bmi', 'activity_level', 'diet_score', 'calorie_ratio'
        
        Returns:
            dict of condition_type -> (risk_level, score)
        """
        # Convert user data to feature vector
        features = np.array([
            user_data.get('age', 30) / 100,  # Normalize age
            user_data.get('bmi', 25) / 40,   # Normalize BMI
            user_data.get('activity_level', 0.5),  # 0-1 scale
            user_data.get('diet_score', 0.5),      # 0-1 scale
            user_data.get('calorie_ratio', 1.0)    # ratio of consumed/target
        ]).reshape(1, -1)
        
        results = {}
        
        # Make predictions for each condition
        for condition, model in self.models.items():
            prob = model.predict_proba(features)[0][1]  # Probability of positive class
            
            # Determine risk level
            if prob < 0.3:
                risk = 'L'  # Low risk
            elif prob < 0.7:
                risk = 'M'  # Moderate risk
            else:
                risk = 'H'  # High risk
                
            results[condition] = (risk, prob)
            
        return results

# Singleton instance
predictor = HealthPredictor()