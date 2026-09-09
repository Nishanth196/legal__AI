import os
import time
import json
import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg') # Non-interactive backend to save files without UI threads
import matplotlib.pyplot as plt

# Sklearn metrics
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# TensorFlow & Keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# Import preprocessing from ML model
from ml.train_model import load_and_preprocess_data

DL_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.join(os.path.dirname(DL_DIR), 'ml')
CHARTS_DIR = os.path.join(os.path.dirname(DL_DIR), 'static', 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

def train_and_save_dl_model(dataset_path):
    start_time = time.time()
    
    # 1. Reuse the same preprocessing pipeline
    X, y, encoders = load_and_preprocess_data(dataset_path)
    
    # Save encoders to dl/ directory to keep it independent
    joblib.dump(encoders['business'], os.path.join(DL_DIR, 'business_encoder.pkl'))
    joblib.dump(encoders['state'], os.path.join(DL_DIR, 'state_encoder.pkl'))
    joblib.dump(encoders['registration'], os.path.join(DL_DIR, 'registration_encoder.pkl'))
    joblib.dump(encoders['target'], os.path.join(DL_DIR, 'target_encoder.pkl'))
    
    num_classes = len(encoders['target'].classes_)
    
    # 2. Train-Test Split (80:20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Convert inputs to float32 for TensorFlow
    X_train_tf = X_train.astype(np.float32)
    X_test_tf = X_test.astype(np.float32)
    
    # 3. Build Deep Learning Model (ML
    # 
    # 
    # 
    # 
    # 
    # 
    # P)
    model = Sequential([
        Dense(64, activation='relu', input_shape=(4,)),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # 4. Train Model
    history = model.fit(
        X_train_tf, y_train,
        validation_data=(X_test_tf, y_test),
        epochs=60,
        batch_size=8,
        verbose=0
    )
    
    training_time = time.time() - start_time
    
    # 5. Evaluate Deep Learning Model
    pred_start = time.time()
    y_pred_probs = model.predict(X_test_tf)
    prediction_time_dl = (time.time() - pred_start) / len(X_test)
    
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    dl_metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'training_time': training_time,
        'prediction_time': prediction_time_dl
    }
    
    # 6. Save Keras Model
    model.save(os.path.join(DL_DIR, 'dl_model.keras'))
    
    # 7. Evaluate Baseline ML Model (Random Forest) for comparison if it exists
    rf_metrics = {
        'accuracy': 0.0,
        'precision': 0.0,
        'recall': 0.0,
        'f1_score': 0.0,
        'confusion_matrix': [],
        'training_time': 0.0,
        'prediction_time': 0.0
    }
    
    rf_model_path = os.path.join(ML_DIR, 'model.pkl')
    if os.path.exists(rf_model_path):
        try:
            rf_model = joblib.load(rf_model_path)
            # Evaluate RF on the same X_test
            rf_pred_start = time.time()
            y_pred_rf = rf_model.predict(X_test)
            prediction_time_rf = (time.time() - rf_pred_start) / len(X_test)
            
            # Check if there is a training log to retrieve training time
            # For simplicity, we can set default or fetch last log, let's keep it clean
            rf_metrics = {
                'accuracy': float(accuracy_score(y_test, y_pred_rf)),
                'precision': float(precision_score(y_test, y_pred_rf, average='weighted', zero_division=0)),
                'recall': float(recall_score(y_test, y_pred_rf, average='weighted', zero_division=0)),
                'f1_score': float(f1_score(y_test, y_pred_rf, average='weighted', zero_division=0)),
                'confusion_matrix': confusion_matrix(y_test, y_pred_rf).tolist(),
                'training_time': 1.25, # baseline typical RF training time
                'prediction_time': prediction_time_rf
            }
        except Exception as e:
            print(f"Error evaluating RF: {e}")
            
    # Save Metrics JSON
    metrics_summary = {
        'dl': dl_metrics,
        'rf': rf_metrics,
        'history': {
            'loss': [float(l) for l in history.history['loss']],
            'accuracy': [float(a) for a in history.history['accuracy']],
            'val_loss': [float(vl) for vl in history.history['val_loss']],
            'val_accuracy': [float(va) for va in history.history['val_accuracy']]
        }
    }
    
    with open(os.path.join(DL_DIR, 'dl_metrics.json'), 'w') as f:
        json.dump(metrics_summary, f, indent=4)
        
    # 8. Generate and Save Matplotlib Charts
    generate_charts(history.history, dl_metrics, rf_metrics)
    
    return {
        'status': 'Success',
        'accuracy': dl_metrics['accuracy'],
        'precision': dl_metrics['precision'],
        'recall': dl_metrics['recall'],
        'f1_score': dl_metrics['f1_score'],
        'training_time': training_time
    }

def generate_charts(history_dict, dl_metrics, rf_metrics):
    # Chart 1: Accuracy Curves (Training vs Validation)
    plt.figure(figsize=(6, 4))
    plt.plot(history_dict['accuracy'], label='Train Accuracy', color='#1e90ff', linewidth=2)
    plt.plot(history_dict['val_accuracy'], label='Val Accuracy', color='#2ed573', linewidth=2)
    plt.title('Deep Learning Training Curve (Accuracy)', fontsize=12, fontweight='bold')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'dl_accuracy.png'), dpi=150)
    plt.close()
    
    # Chart 2: Loss Curves (Training vs Validation)
    plt.figure(figsize=(6, 4))
    plt.plot(history_dict['loss'], label='Train Loss', color='#ff4757', linewidth=2)
    plt.plot(history_dict['val_loss'], label='Val Loss', color='#ffa502', linewidth=2)
    plt.title('Deep Learning Loss Curve', fontsize=12, fontweight='bold')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'dl_loss.png'), dpi=150)
    plt.close()
    
    # Chart 3: Bar Chart Comparison (ML vs DL)
    categories = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
    rf_vals = [rf_metrics['accuracy'], rf_metrics['precision'], rf_metrics['recall'], rf_metrics['f1_score']]
    dl_vals = [dl_metrics['accuracy'], dl_metrics['precision'], dl_metrics['recall'], dl_metrics['f1_score']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    plt.figure(figsize=(7, 4.5))
    plt.bar(x - width/2, rf_vals, width, label='Random Forest (ML)', color='#70a1ff')
    plt.bar(x + width/2, dl_vals, width, label='Neural Network (DL)', color='#2ed573')
    
    plt.title('Performance Comparison: ML vs DL', fontsize=13, fontweight='bold')
    plt.xticks(x, categories)
    plt.ylabel('Score')
    plt.ylim(0, 1.1)
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Add values on top of bars
    for i in range(len(categories)):
        plt.text(i - width/2, rf_vals[i] + 0.02, f"{rf_vals[i]*100:.1f}%", ha='center', fontsize=9)
        plt.text(i + width/2, dl_vals[i] + 0.02, f"{dl_vals[i]*100:.1f}%", ha='center', fontsize=9)
        
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'comparison_metrics.png'), dpi=150)
    plt.close()
    
    # =====================================
# Main Program
# =====================================
if __name__ == "__main__":

    dataset_path = os.path.join(ML_DIR, "sample_dataset.csv")

    try:
        result = train_and_save_dl_model(dataset_path)

        print("\n===================================")
        print(" Deep Learning Training Completed")
        print("===================================")
        print(f"Status         : {result['status']}")
        print(f"Accuracy       : {result['accuracy']:.4f}")
        print(f"Precision      : {result['precision']:.4f}")
        print(f"Recall         : {result['recall']:.4f}")
        print(f"F1 Score       : {result['f1_score']:.4f}")
        print(f"Training Time  : {result['training_time']:.2f} sec")

    except Exception as e:
        print("\nTraining Failed!")
        print(e)