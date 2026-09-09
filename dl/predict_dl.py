import os
import joblib
import numpy as np

# Suppress TensorFlow logging to keep stdout clean
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

DL_DIR = os.path.dirname(os.path.abspath(__file__))

def load_dl_components():
    model_path = os.path.join(DL_DIR, 'dl_model.keras')
    if not os.path.exists(model_path):
        raise FileNotFoundError("Deep Learning model not found")
        
    model = tf.keras.models.load_model(model_path)
    b_encoder = joblib.load(os.path.join(DL_DIR, 'business_encoder.pkl'))
    s_encoder = joblib.load(os.path.join(DL_DIR, 'state_encoder.pkl'))
    r_encoder = joblib.load(os.path.join(DL_DIR, 'registration_encoder.pkl'))
    t_encoder = joblib.load(os.path.join(DL_DIR, 'target_encoder.pkl'))
    
    return model, b_encoder, s_encoder, r_encoder, t_encoder

def safe_encode(encoder, val):
    if val in encoder.classes_:
        return encoder.transform([val])[0]
    return 0

def predict_document_dl(business_type, state, registration_type, turnover):
    try:
        model, b_encoder, s_encoder, r_encoder, t_encoder = load_dl_components()
        
        b_val = safe_encode(b_encoder, business_type)
        s_val = safe_encode(s_encoder, state)
        r_val = safe_encode(r_encoder, registration_type)
        turnover_val = float(turnover or 0)
        
        features = np.array([[b_val, s_val, r_val, turnover_val]], dtype=np.float32)
        
        # Predict
        probs = model.predict(features, verbose=0)[0]
        pred_idx = np.argmax(probs)
        predicted_doc = t_encoder.inverse_transform([pred_idx])[0]
        confidence = round(float(probs[pred_idx]) * 100, 1)
        
        return predicted_doc, confidence
    except FileNotFoundError:
        return None, None
    except Exception as e:
        raise e
    
    # =====================================
# Test Prediction
# =====================================
if __name__ == "__main__":
    try:
        document, confidence = predict_document_dl(
            business_type="Manufacturing",
            state="Tamil Nadu",
            registration_type="Private Limited",
            turnover=500
        )

        print("Predicted Document:", document)
        print("Confidence:", confidence)

    except Exception as e:
        print("Error:", e)

        