"""
Quick ML Model Evaluation - NutriLogic
======================================
Simple script to quickly check model performance metrics

Usage: python quick_model_eval.py
"""

import os
import sys
import django
import numpy as np

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutrilogic.settings')
django.setup()

from health.ml_model import HealthPredictor
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score

def generate_test_data(n=200):
    """Generate simple test data"""
    np.random.seed(42)
    
    age = np.random.randint(18, 80, n)
    bmi = np.random.normal(25, 5, n)
    bmi = np.clip(bmi, 15, 45)
    activity = np.random.beta(2, 2, n)
    diet = np.random.beta(2, 2, n)
    cal_ratio = np.random.normal(1.0, 0.2, n)
    
    X = np.column_stack([age, bmi, activity, diet, cal_ratio])
    
    # True labels
    y = {
        'obesity': (bmi > 30).astype(int),
        'diabetes': ((bmi > 27) & (diet < 0.4) & (age > 40)).astype(int),
        'heart_disease': ((bmi > 28) & (activity < 0.3) & (age > 45)).astype(int),
        'nutrient_deficiency': ((diet < 0.3) | (cal_ratio < 0.7)).astype(int)
    }
    
    return X, y

def evaluate_condition(predictor, condition, X, y_true):
    """Evaluate single condition"""
    print(f"\n{'='*60}")
    print(f"📊 {condition.replace('_', ' ').upper()}")
    print('='*60)
    
    # Normalize features
    X_norm = X.copy()
    X_norm[:, 0] = X_norm[:, 0] / 100
    X_norm[:, 1] = X_norm[:, 1] / 40
    
    # Predict
    model = predictor.models[condition]
    y_pred = model.predict(X_norm)
    
    # Metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    print(f"\n✅ METRICS:")
    print(f"   Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
    print(f"   Precision: {prec:.4f}")
    print(f"   Recall:    {rec:.4f}")
    print(f"   F1-Score:  {f1:.4f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    print(f"\n📈 CONFUSION MATRIX:")
    print(f"              Predicted")
    print(f"           Neg    Pos")
    print(f"   Real N  {cm[0,0]:4d}   {cm[0,1]:4d}")
    print(f"        P  {cm[1,0]:4d}   {cm[1,1]:4d}")
    
    tn, fp, fn, tp = cm.ravel()
    print(f"\n   True Positives:  {tp}")
    print(f"   True Negatives:  {tn}")
    print(f"   False Positives: {fp}")
    print(f"   False Negatives: {fn}")

def main():
    print("\n" + "🔬" * 30)
    print("   NUTRILOGIC - QUICK MODEL EVALUATION")
    print("🔬" * 30 + "\n")
    
    print("📊 Generating test data...")
    X, y_dict = generate_test_data(200)
    print("✅ Generated 200 test samples\n")
    
    predictor = HealthPredictor()
    
    conditions = ['obesity', 'diabetes', 'heart_disease', 'nutrient_deficiency']
    
    for condition in conditions:
        evaluate_condition(predictor, condition, X, y_dict[condition])
    
    print("\n" + "="*60)
    print("✅ EVALUATION COMPLETE!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

