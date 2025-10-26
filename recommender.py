import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from django.conf import settings


class MealRecommender:
    def __init__(self):
        self.meals_data = None
        self.model = None
        self.load_data_and_model()

    def load_data_and_model(self):
        try:
            csv_path = os.path.join(settings.BASE_DIR, 'meals', 'data', 'Indian_Food_Nutrition_Processed.csv')
            self.meals_data = pd.read_csv(csv_path)
            
            # Clean column names
            self.meals_data.columns = self.meals_data.columns.str.strip()
            
            # Rename columns
            column_renames = {
                'Calories (kcal)': 'Calories',
                'Protein (g)': 'Protein',
                'Fats (g)': 'Fat',
                'Carbohydrates (g)': 'Carbs'
            }
            self.meals_data = self.meals_data.rename(columns=column_renames)
            
            # Load model
            model_path = os.path.join(settings.BASE_DIR, 'meals', 'data', 'meal_classifier.pkl')
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
            else:
                self.train_model()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self.create_fallback_data()

    def create_fallback_data(self):
        self.meals_data = pd.DataFrame({
            'Dish Name': ['Chicken Curry', 'Dal Tadka', 'Paneer Tikka', 'Biryani', 'Roti'],
            'Calories': [300, 200, 250, 400, 100],
            'Protein': [25, 15, 18, 20, 5],
            'Carbs': [15, 30, 10, 50, 20],
            'Fat': [18, 8, 15, 15, 2]
        })

    def train_model(self):
        if self.meals_data is None or self.meals_data.empty:
            return
        
        data = self.meals_data.dropna(subset=['Calories', 'Protein', 'Fat', 'Carbs'])
        conditions = [
            (data['Calories'] < 400),
            (data['Calories'] >= 400) & (data['Calories'] < 600),
            (data['Calories'] >= 600)
        ]
        choices = ['Light', 'Balanced', 'High-Calorie']
        data['Meal_Category'] = np.select(conditions, choices, default='Balanced')
        
        X = data[['Calories', 'Protein', 'Fat', 'Carbs']]
        y = data['Meal_Category']
        
        if len(X) > 10:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

    def calculate_bmi_category(self, height, weight):
        if height <= 0 or weight <= 0:
            return 'Normal'
        bmi = weight / ((height/100) ** 2)
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    def get_recommendations(self, user_data, num_recommendations=15):
        if self.meals_data is None or self.meals_data.empty:
            return []
        
        # Extract user data (must be provided, no defaults)
        age = user_data['age']
        gender = user_data['gender']
        height = user_data['height']
        weight = user_data['weight']
        goal = user_data.get('goal', 'M')  # L=Lose, M=Maintain, G=Gain
        activity_level = user_data.get('activity_level', 'M')
        
        # Calculate BMI category
        bmi_category = self.calculate_bmi_category(height, weight)
        
        if gender == 'Male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        # Activity factor
        activity_factors = {
            'S': 1.2,   # Sedentary
            'L': 1.375, # Lightly active
            'M': 1.55,  # Moderately active
            'V': 1.725, # Very active
            'E': 1.9    # Extra active
        }
        tdee = bmr * activity_factors.get(activity_level, 1.2)
        
        # Adjust target calories based on goal and BMI
        if bmi_category == 'Underweight' or goal == 'G':
            target_calories = tdee * 1.15  # Gain weight
            max_fat = 100  # Allow higher fat
            max_carbs = 300  # Allow higher carbs
        elif bmi_category == 'Obese' or bmi_category == 'Overweight' or goal == 'L':
            target_calories = tdee * 0.75  # Lose weight - more aggressive
            max_fat = 30   # LOW FAT for weight loss
            max_carbs = 80  # LOW CARB for weight loss
        else:
            target_calories = tdee
            max_fat = 50   # Moderate fat
            max_carbs = 130  # Moderate carbs
        
        # Filter meals by calories
        filtered_meals = self.meals_data.copy()
        calorie_range = target_calories * 0.3  # Per meal target
        
        filtered_meals = filtered_meals[
            (filtered_meals['Calories'] >= calorie_range * 0.4) &
            (filtered_meals['Calories'] <= calorie_range * 1.2)
        ]
        
        # CRITICAL: Filter for LOW FAT, LOW CARB, HIGH PROTEIN foods
        if bmi_category in ['Obese', 'Overweight'] or goal == 'L':
            # Strict filtering for weight loss
            filtered_meals = filtered_meals[
                (filtered_meals['Fat'] <= max_fat) &
                (filtered_meals['Carbs'] <= max_carbs) &
                (filtered_meals['Protein'] >= 10)  # MINIMUM 10g protein
            ]
            
            # Calculate health score (lower is better for weight loss)
            # HEAVILY prioritize high protein, penalize fat and carbs
            filtered_meals['health_score'] = (
                (filtered_meals['Fat'] * 3.0) +          # Penalize fat VERY heavily
                (filtered_meals['Carbs'] * 2.0) -        # Penalize carbs heavily
                (filtered_meals['Protein'] * 5.0) +      # Reward protein MASSIVELY
                abs(filtered_meals['Calories'] - calorie_range) * 0.1
            )
        else:
            # Normal filtering - still prioritize protein
            filtered_meals = filtered_meals[
                (filtered_meals['Fat'] <= max_fat) &
                (filtered_meals['Carbs'] <= max_carbs) &
                (filtered_meals['Protein'] >= 8)  # MINIMUM 8g protein
            ]
            
            # Balanced score - still favor protein
            filtered_meals['health_score'] = (
                (filtered_meals['Fat'] * 1.5) +          # Penalize fat moderately
                (filtered_meals['Carbs'] * 1.0) -        # Penalize carbs lightly
                (filtered_meals['Protein'] * 3.0) +      # Reward protein heavily
                abs(filtered_meals['Calories'] - calorie_range) * 0.2
            )
        
        # Sort by health score (lower is better = high protein, low fat/carbs)
        filtered_meals = filtered_meals.sort_values('health_score')
        
        # Additional protein ranking: calculate protein-to-calorie ratio
        if not filtered_meals.empty:
            filtered_meals['protein_ratio'] = (filtered_meals['Protein'] / filtered_meals['Calories']) * 100
            # Re-sort with protein ratio as secondary sort
            filtered_meals = filtered_meals.sort_values(['health_score', 'protein_ratio'], ascending=[True, False])
        
        recommendations = []
        if not filtered_meals.empty:
            for _, meal in filtered_meals.head(num_recommendations).iterrows():
                recommendations.append({
                    'name': meal['Dish Name'],
                    'calories': int(meal['Calories']),
                    'protein': float(meal['Protein']),
                    'carbs': float(meal['Carbs']),
                    'fat': float(meal['Fat']),
                    'bmi_category': bmi_category,
                    'target_calories': int(target_calories),
                    'goal': goal,
                    'max_fat': max_fat,
                    'max_carbs': max_carbs
                })
        
        return recommendations