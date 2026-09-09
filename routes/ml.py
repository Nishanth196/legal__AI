from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
from ml.train_model import train_and_save_model
from ml.predict_model import predict_document
from models.ml_log import ModelTrainingLog
from app import db

ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/train', methods=['GET', 'POST'])
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
                result = train_and_save_model(filepath)
                
                # Log to database
                log_entry = ModelTrainingLog(
                    dataset_name=filename,
                    accuracy=result['accuracy'],
                    precision_val=result['precision'],
                    recall=result['recall'],
                    f1_score=result['f1_score'],
                    training_time=result['training_time'],
                    status=result['status']
                )
                db.session.add(log_entry)
                db.session.commit()
                
                flash(f'Model trained successfully with {result["accuracy"]*100:.1f}% accuracy!', 'success')
                return render_template('ml/train.html', result=result)
                
            except Exception as e:
                flash(f'Training failed: {str(e)}', 'error')
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            flash('Please upload a valid CSV file.', 'error')
            
    return render_template('ml/train.html')

@ml_bp.route('/predict', methods=['GET', 'POST'])
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
            prediction, confidence = predict_document(b_type, state, r_type, turnover)
            if not prediction:
                flash('No trained model found. Please train first.', 'warning')
                error = True
        except Exception as e:
            flash(f'Prediction error: {str(e)}', 'error')
            error = True
            
    return render_template('ml/predict.html', 
                           prediction=prediction, 
                           confidence=confidence,
                           error=error)
