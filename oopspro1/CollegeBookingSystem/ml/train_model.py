"""
============================================================
 train_model.py — ML Model Training Script
============================================================
 Trains 3 ML models on booking data:
   1. Random Forest Classifier
   2. Decision Tree Classifier  
   3. Logistic Regression

 Saves the best model as best_model.pkl
 This script can be run standalone or imported by Flask.
============================================================
"""

import os
import sys
import json
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
import warnings
warnings.filterwarnings('ignore')

# ── Configuration ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "training_data.csv")

VALID_SLOTS = ["9-10", "10-11", "11-12", "12-1", "2-3", "3-4"]

def generate_synthetic_data(n_samples=1500):
    """Generate synthetic booking data for model training."""
    print(f"[ML] Generating {n_samples} synthetic data samples...")
    
    users = [f"S{i}" for i in range(1001, 1051)] + [f"F{i}" for i in range(101, 121)]
    
    rooms = []
    for floor in range(1, 5):
        for room in range(1, 411):
            rooms.append(floor * 1000 + room)
    
    # Use a subset of popular rooms
    popular_rooms = random.sample(rooms, min(300, len(rooms)))
    
    data = []
    for _ in range(n_samples):
        user = random.choice(users)
        room = random.choice(popular_rooms)
        slot_idx = random.randint(0, len(VALID_SLOTS) - 1)
        slot = VALID_SLOTS[slot_idx]
        
        # Booking probability influenced by:
        # - Time slot (morning slots are more popular)
        # - Room floor (lower floors slightly more popular)
        # - User type (S = student, F = faculty)
        
        floor_num = room // 1000
        is_student = user.startswith('S')
        
        # Base probability
        prob = 0.5
        
        # Morning slots more popular
        if slot_idx < 3:
            prob += 0.15
        
        # Lower floors slightly more popular
        prob += (5 - floor_num) * 0.03
        
        # Students book more
        if is_student:
            prob += 0.05
        
        # Add some noise
        prob += random.uniform(-0.2, 0.2)
        prob = max(0, min(1, prob))
        
        booked = 1 if random.random() < prob else 0
        
        data.append({
            'user': user,
            'room': room,
            'slot': slot,
            'slot_idx': slot_idx,
            'floor': floor_num,
            'is_student': 1 if is_student else 0,
            'booked': booked
        })
    
    df = pd.DataFrame(data)
    df.to_csv(DATA_PATH, index=False)
    print(f"[ML] Data saved to {DATA_PATH}")
    return df

def load_data():
    """Load or generate training data."""
    if os.path.exists(DATA_PATH):
        print(f"[ML] Loading data from {DATA_PATH}...")
        df = pd.read_csv(DATA_PATH)
        if len(df) >= 1000:
            return df
    
    return generate_synthetic_data()

def train_models():
    """Train all 3 models and save the best one."""
    print("\n" + "="*60)
    print("  ML MODEL TRAINING")
    print("="*60)
    
    # Load data
    df = load_data()
    print(f"\n[ML] Dataset: {len(df)} samples")
    print(f"[ML] Features: room, slot_idx, floor, is_student")
    print(f"[ML] Target: booked (0/1)")
    print(f"[ML] Class distribution: {dict(df['booked'].value_counts())}")
    
    # Prepare features
    X = df[['room', 'slot_idx', 'floor', 'is_student']].values
    y = df['booked'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n[ML] Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # ── Model 1: Random Forest ──
    print("\n── Model 1: Random Forest ──")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    rf_cm = confusion_matrix(y_test, rf_pred)
    print(f"   Accuracy: {rf_acc:.4f}")
    print(f"   Confusion Matrix:\n{rf_cm}")
    
    # ── Model 2: Decision Tree ──
    print("\n── Model 2: Decision Tree ──")
    dt = DecisionTreeClassifier(random_state=42, max_depth=8)
    dt.fit(X_train, y_train)
    dt_pred = dt.predict(X_test)
    dt_acc = accuracy_score(y_test, dt_pred)
    dt_cm = confusion_matrix(y_test, dt_pred)
    print(f"   Accuracy: {dt_acc:.4f}")
    print(f"   Confusion Matrix:\n{dt_cm}")
    
    # ── Model 3: Logistic Regression ──
    print("\n── Model 3: Logistic Regression ──")
    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_pred)
    lr_cm = confusion_matrix(y_test, lr_pred)
    print(f"   Accuracy: {lr_acc:.4f}")
    print(f"   Confusion Matrix:\n{lr_cm}")
    
    # ── Compare and select best ──
    print("\n" + "="*60)
    print("  MODEL COMPARISON")
    print("="*60)
    
    models = {
        'Random Forest': (rf, rf_acc),
        'Decision Tree': (dt, dt_acc),
        'Logistic Regression': (lr, lr_acc)
    }
    
    print(f"\n  {'Model':<24} {'Accuracy':>10}")
    print(f"  {'─'*34}")
    
    best_name = None
    best_model = None
    best_acc = 0
    
    for name, (model, acc) in models.items():
        marker = ""
        if acc > best_acc:
            best_acc = acc
            best_name = name
            best_model = model
        print(f"  {name:<24} {acc:>10.4f}")
    
    print(f"\n  ★ Best Model: {best_name} ({best_acc:.4f})")
    
    # Save best model
    joblib.dump(best_model, MODEL_PATH)
    print(f"  ✓ Model saved to: {MODEL_PATH}")
    
    # Save results
    results = {
        'models': {
            'Random Forest': {'accuracy': round(rf_acc, 4), 'confusion_matrix': rf_cm.tolist()},
            'Decision Tree': {'accuracy': round(dt_acc, 4), 'confusion_matrix': dt_cm.tolist()},
            'Logistic Regression': {'accuracy': round(lr_acc, 4), 'confusion_matrix': lr_cm.tolist()},
        },
        'best_model': best_name,
        'best_accuracy': round(best_acc, 4),
        'dataset_size': len(df),
        'train_size': len(X_train),
        'test_size': len(X_test)
    }
    
    results_path = os.path.join(BASE_DIR, "training_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ Results saved to: {results_path}")
    
    print("\n" + "="*60)
    print("  TRAINING COMPLETE")
    print("="*60 + "\n")
    
    return best_model, results

if __name__ == '__main__':
    train_models()
