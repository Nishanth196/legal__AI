from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
import os
import json
from werkzeug.utils import secure_filename
from dl.train_dl import train_and_save_dl_model
from dl.predict_dl import predict_document_dl
from models.ml_log import ModelTrainingLog
from app import db

dl_bp = Blueprint('dl', __name__)

DL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@dl_bp.route('/train', methods=['GET', 'POST'])
@login_required
def train():
    if request.method == 'POST':
        if 'dataset' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['dataset']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config.get('UPLOAD_FOLDER', '/tmp'), filename)
            file.save(filepath)
            
            try:
                # Run training
                result = train_and_save_dl_model(filepath)
                
                # Log to database with prefix [DL]
                log_entry = ModelTrainingLog(
                    dataset_name=f"[DL] {filename}",
                    accuracy=result['accuracy'],
                    precision_val=result['precision'],
                    recall=result['recall'],
                    f1_score=result['f1_score'],
                    training_time=result['training_time'],
                    status=result['status']
                )
                db.session.add(log_entry)
                db.session.commit()
                
                flash(f'Deep Learning model trained successfully with {result["accuracy"]*100:.1f}% accuracy!', 'success')
                return render_template('dl/train.html', result=result)
                
            except Exception as e:
                flash(f'Deep Learning training failed: {str(e)}', 'error')
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            flash('Please upload a valid CSV file.', 'error')
            
    return render_template('dl/train.html')

@dl_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    prediction = None
    confidence = None
    error = False
    
    if request.method == 'POST':
        b_type = request.form.get('business_type')
        state = request.form.get('state')
        r_type = request.form.get('registration_type')
        turnover = request.form.get('annual_turnover')
        
        try:
            prediction, confidence = predict_document_dl(b_type, state, r_type, turnover)
            if not prediction:
                flash('No trained Deep Learning model found. Please train first.', 'warning')
                error = True
        except Exception as e:
            flash(f'Prediction error: {str(e)}', 'error')
            error = True
            
    return render_template('dl/predict.html', 
                           prediction=prediction, 
                           confidence=confidence,
                           error=error)

@dl_bp.route('/comparison')
@login_required
def comparison():
    metrics_path = os.path.join(DL_DIR, 'dl', 'dl_metrics.json')
    if not os.path.exists(metrics_path):
        flash('No model comparison data found. Please train the Deep Learning model first.', 'warning')
        return render_template('dl/comparison.html', no_data=True)
        
    try:
        with open(metrics_path, 'r') as f:
            data = json.load(f)
        return render_template('dl/comparison.html', no_data=False, data=data)
    except Exception as e:
        flash(f'Error loading comparison metrics: {str(e)}', 'error')
        return render_template('dl/comparison.html', no_data=True)
