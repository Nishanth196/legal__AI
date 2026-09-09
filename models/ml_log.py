from datetime import datetime
from app import db

class ModelTrainingLog(db.Model):
    __tablename__ = 'model_training_logs'

    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(255), nullable=False)
    accuracy = db.Column(db.Float)
    precision_val = db.Column(db.Float)  # Using precision_val to avoid SQL keyword conflicts
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    training_time = db.Column(db.Float)
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Success')

    def __repr__(self):
        return f"<ModelTrainingLog {self.id} - {self.dataset_name} ({self.status})>"
