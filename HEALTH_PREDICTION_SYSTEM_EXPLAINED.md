# 🏥 Health Prediction System - How It Works

## 📊 Overview

The NutriLogic health prediction system uses **Machine Learning (ML)** to predict the risk of various health conditions based on user profile data and lifestyle inputs. This is a **premium feature** requiring an active subscription.

---

## 🎯 What It Predicts

The system predicts risk levels for **4 health conditions**:

1. **Obesity** - Risk of being overweight/obese
2. **Diabetes** - Risk of developing diabetes
3. **Heart Disease** - Risk of cardiovascular issues
4. **Nutrient Deficiency** - Risk of nutritional deficiencies

### Risk Levels
- 🟢 **Low Risk** (L) - Probability < 30%
- 🟡 **Moderate Risk** (M) - Probability 30-70%
- 🔴 **High Risk** (H) - Probability > 70%

---

## 🔧 How It Works - Step by Step

### Step 1: Data Collection (User Input)

The system collects **5 key features** from the user:

```python
user_data = {
    'age': profile.age,                    # From user profile
    'bmi': profile.calculate_bmi(),        # Calculated: weight/height²
    'activity_level': 0.2-1.0,             # Converted from activity choice
    'diet_score': 0-1.0,                   # User input (diet quality)
    'calorie_ratio': consumed/target        # Actual vs target calories
}
```

#### Feature Details:

1. **Age** (from profile)
   - Normalized: age / 100
   - Example: 30 years → 0.30

2. **BMI** (Body Mass Index)
   - Formula: `weight (kg) / height (m)²`
   - Normalized: bmi / 40
   - Example: BMI 25 → 0.625

3. **Activity Level** (from profile)
   - Sedentary (S) → 0.2
   - Light (L) → 0.4
   - Moderate (M) → 0.6
   - Active (A) → 0.8
   - Very Active (V) → 1.0

4. **Diet Score** (user input via form)
   - Range: 0.0 (poor) to 1.0 (excellent)
   - Represents overall diet quality

5. **Calorie Ratio** (user input)
   - Formula: `calories_consumed / daily_calorie_target`
   - Example: 2000/2000 = 1.0 (perfect)
   - <1.0 = under-eating, >1.0 = over-eating

---

### Step 2: ML Model Processing

The system uses **Random Forest Classifier** models:

```python
class HealthPredictor:
    def __init__(self):
        self.models = {
            'obesity': RandomForestClassifier(),
            'diabetes': RandomForestClassifier(),
            'heart_disease': RandomForestClassifier(),
            'nutrient_deficiency': RandomForestClassifier()
        }
```

#### Model Architecture:
- **Algorithm**: Random Forest (ensemble of decision trees)
- **Number of Trees**: 10 estimators
- **Features**: 5 input features
- **Output**: Binary classification (Risk/No Risk) with probability

---

### Step 3: Prediction Logic

Each condition uses different logic for risk assessment:

#### 🔴 Obesity Prediction
```python
# High BMI → Obesity Risk
if BMI > 0.7 (normalized):  # ~28+ actual BMI
    risk = HIGH
```
**Key Factor**: Primarily BMI-based

#### 🔴 Diabetes Prediction
```python
# High BMI + Poor Diet → Diabetes Risk
if (BMI > 0.6) AND (diet_score < 0.4):
    risk = HIGH
```
**Key Factors**: BMI and diet quality

#### 🔴 Heart Disease Prediction
```python
# High BMI + Low Activity → Heart Disease Risk
if (BMI > 0.6) AND (activity_level < 0.3):
    risk = HIGH
```
**Key Factors**: BMI and physical activity

#### 🔴 Nutrient Deficiency Prediction
```python
# Poor Diet → Nutrient Deficiency Risk
if diet_score < 0.3:
    risk = HIGH
```
**Key Factor**: Diet quality

---

### Step 4: Risk Level Classification

The ML model outputs a **probability score** (0-1), which is then classified:

```python
if probability < 0.3:
    risk_level = 'L'  # Low Risk (Green)
elif probability < 0.7:
    risk_level = 'M'  # Moderate Risk (Yellow)
else:
    risk_level = 'H'  # High Risk (Red)
```

---

### Step 5: Database Storage

Results are saved to the database:

```python
HealthPrediction.objects.create(
    user=request.user,
    condition_type='obesity',      # or diabetes, heart_disease, etc.
    risk_level='M',                # L, M, or H
    prediction_score=0.65,         # 0-1 probability
    input_data={...},              # User data used for prediction
    prediction_date=now()
)
```

---

## 🗂️ Database Schema

```sql
HealthPrediction Table:
┌─────────────────┬──────────────┬─────────────────────────┐
│ Field           │ Type         │ Description             │
├─────────────────┼──────────────┼─────────────────────────┤
│ id              │ AutoField    │ Primary key             │
│ user_id         │ ForeignKey   │ Links to User           │
│ condition_type  │ CharField    │ obesity/diabetes/etc.   │
│ risk_level      │ CharField    │ L/M/H                   │
│ prediction_score│ FloatField   │ 0-1 probability         │
│ input_data      │ JSONField    │ Input features stored   │
│ prediction_date │ DateTime     │ When prediction made    │
│ notes           │ TextField    │ Optional notes          │
└─────────────────┴──────────────┴─────────────────────────┘
```

---

## 🔄 Complete Flow Diagram

```
User Profile Data + Form Input
         ↓
    ┌─────────────────────┐
    │  Data Collection    │
    │  - Age              │
    │  - BMI              │
    │  - Activity Level   │
    │  - Diet Score       │
    │  - Calorie Ratio    │
    └─────────────────────┘
         ↓
    ┌─────────────────────┐
    │  Normalization      │
    │  (Scale to 0-1)     │
    └─────────────────────┘
         ↓
    ┌─────────────────────────────────────┐
    │  ML Models (4 Random Forests)       │
    │  ┌───────────┬──────────────────┐   │
    │  │ Obesity   │ → Probability    │   │
    │  │ Diabetes  │ → Probability    │   │
    │  │ Heart     │ → Probability    │   │
    │  │ Nutrients │ → Probability    │   │
    │  └───────────┴──────────────────┘   │
    └─────────────────────────────────────┘
         ↓
    ┌─────────────────────┐
    │  Risk Classification│
    │  prob < 0.3 → Low   │
    │  prob < 0.7 → Mod   │
    │  prob ≥ 0.7 → High  │
    └─────────────────────┘
         ↓
    ┌─────────────────────┐
    │  Save to Database   │
    │  + Display Results  │
    └─────────────────────┘
```

---

## 💻 Code Structure

### 1. **Models** (`health/models.py`)
Defines the database structure for storing predictions.

### 2. **ML Engine** (`health/ml_model.py`)
Contains the `HealthPredictor` class with:
- Model initialization
- Feature engineering
- Prediction logic
- Risk classification

### 3. **Views** (`health/views.py`)
Handles the web interface:
- `health_home()` - Dashboard
- `predict_health()` - Form and prediction
- `health_results()` - Display results
- `prediction_history()` - Historical data

### 4. **Templates**
- `predict_form.html` - Input form
- `health_results.html` - Results display
- `prediction_history.html` - History view

---

## 🎓 ML Model Details

### Current Implementation: Demo Models

The system currently uses **demonstration models** created on-the-fly:

```python
def _create_demo_model(self, condition_type):
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    
    # Train with 100 random samples
    X = np.random.rand(100, 5)  # 5 features
    
    # Create labels based on condition logic
    if condition_type == 'obesity':
        y = (X[:, 1] > 0.7).astype(int)  # High BMI
    elif condition_type == 'diabetes':
        y = ((X[:, 1] > 0.6) & (X[:, 3] < 0.4)).astype(int)
    # ... etc
    
    model.fit(X, y)
    return model
```

### Why Demo Models?

1. **No Pre-trained Models**: The system doesn't have pre-trained models saved in `health/ml_models/`
2. **Instant Deployment**: Works out-of-the-box without large model files
3. **Demonstration Purpose**: Shows how the system works

### Upgrading to Real Models

To use actual trained models:

1. **Create training data** from real health datasets
2. **Train models** with proper validation
3. **Save models** using joblib:
   ```python
   joblib.dump(model, 'health/ml_models/obesity_model.joblib')
   ```
4. **Models auto-load** if files exist in `health/ml_models/`

---

## 🔒 Security & Access Control

### Premium Feature Check
```python
# Before allowing prediction
try:
    subscription = request.user.subscription
    if not subscription.is_active():
        redirect('premium-home')
except:
    redirect('premium-home')
```

Only users with **active subscriptions** can:
- Generate predictions
- View results
- Access prediction history

---

## 📈 Interpretation Guide

### Example Results:

**User Input:**
- Age: 35
- BMI: 28.5 (Overweight)
- Activity: Sedentary (0.2)
- Diet Score: 0.4 (Fair)
- Calorie Ratio: 1.2 (Over-eating)

**Predictions:**
```
Obesity:            High Risk (H)   - 85% probability
Diabetes:           Moderate (M)    - 55% probability
Heart Disease:      Moderate (M)    - 60% probability
Nutrient Deficiency: Low (L)        - 25% probability
```

**Interpretation:**
- 🔴 **Obesity**: High BMI (28.5) + over-eating → High risk
- 🟡 **Diabetes**: High BMI + fair diet → Moderate risk
- 🟡 **Heart**: High BMI + sedentary → Moderate risk
- 🟢 **Nutrients**: Diet not terrible → Low risk

---

## 🚀 Future Enhancements

### Potential Improvements:

1. **Real Dataset Training**
   - Use actual health datasets (CDC, WHO data)
   - Train on thousands of real cases
   - Validate with medical research

2. **More Features**
   - Family history
   - Blood pressure
   - Cholesterol levels
   - Sleep patterns
   - Stress levels

3. **Advanced Algorithms**
   - Neural Networks
   - Gradient Boosting (XGBoost)
   - Ensemble methods

4. **Personalized Recommendations**
   - Custom diet plans based on risks
   - Exercise recommendations
   - Lifestyle changes

5. **Trend Analysis**
   - Track risk changes over time
   - Visualize improvement
   - Goal tracking

---

## 📊 Data Flow Example

```
User: John (35 years, 75kg, 1.70m)
↓
Profile Data:
- Age: 35
- Height: 170 cm
- Weight: 75 kg
- Activity: Sedentary
↓
Calculated:
- BMI: 75 / (1.7²) = 25.95
↓
Form Input:
- Diet Score: 0.6 (Good)
- Calorie Ratio: 1.1 (Slightly over)
↓
Feature Vector:
[0.35, 0.648, 0.2, 0.6, 1.1]
↓
ML Processing:
- Obesity Model:     prob = 0.72 → High Risk
- Diabetes Model:    prob = 0.45 → Moderate
- Heart Model:       prob = 0.58 → Moderate
- Nutrient Model:    prob = 0.25 → Low
↓
Database:
4 HealthPrediction records created
↓
Display:
User sees results with recommendations
```

---

## 🎯 Summary

The health prediction system:

✅ Collects 5 key health metrics  
✅ Uses Random Forest ML models  
✅ Predicts 4 health conditions  
✅ Classifies into 3 risk levels  
✅ Stores results in database  
✅ Premium-only feature  
✅ Currently uses demo models (can be upgraded)

**Key Strength**: Provides instant, data-driven health insights to users based on their profile and lifestyle choices.

**Note**: This is a demonstration system. For medical use, it would need:
- Real medical datasets
- Clinical validation
- Regulatory approval
- Disclaimer that it's not medical advice

---

**Last Updated**: October 2025  
**System**: NutriLogic Health Prediction Module  
**ML Framework**: Scikit-learn (RandomForestClassifier)

