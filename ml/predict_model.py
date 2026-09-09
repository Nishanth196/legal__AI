import os
import joblib
import numpy as np

ML_DIR = os.path.dirname(os.path.abspath(__file__))


def load_ml_components():
    """Load trained model and label encoders."""

    model_path = os.path.join(ML_DIR, "model.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            "Model not found. Please run train_model.py first."
        )

    model = joblib.load(model_path)
    business_encoder = joblib.load(os.path.join(ML_DIR, "business_encoder.pkl"))
    state_encoder = joblib.load(os.path.join(ML_DIR, "state_encoder.pkl"))
    registration_encoder = joblib.load(os.path.join(ML_DIR, "registration_encoder.pkl"))
    target_encoder = joblib.load(os.path.join(ML_DIR, "target_encoder.pkl"))

    return (
        model,
        business_encoder,
        state_encoder,
        registration_encoder,
        target_encoder
    )


def safe_encode(encoder, value, field_name):
    """
    Encode categorical value safely.
    Raises an error if value is not present in the trained encoder.
    """

    value = str(value).strip()

    if value not in encoder.classes_:
        raise ValueError(
            f"'{value}' is not a valid {field_name}. "
            f"Available values: {', '.join(encoder.classes_)}"
        )

    return encoder.transform([value])[0]


def predict_document(
    business_type,
    state,
    registration_type,
    turnover
):
    """
    Predict required legal document.
    Returns:
        predicted_document
        confidence (%)
    """

    model, b_encoder, s_encoder, r_encoder, t_encoder = load_ml_components()

    # Encode categorical values
    b_val = safe_encode(
        b_encoder,
        business_type,
        "Business Type"
    )

    s_val = safe_encode(
        s_encoder,
        state,
        "State"
    )

    r_val = safe_encode(
        r_encoder,
        registration_type,
        "Registration Type"
    )

    # Validate turnover
    try:
        turnover = float(turnover)
    except:
        raise ValueError("Annual Turnover must be a numeric value.")

    # Create feature array
    features = np.array([
        [
            b_val,
            s_val,
            r_val,
            turnover
        ]
    ])

    # Prediction
    prediction = model.predict(features)[0]

    predicted_document = t_encoder.inverse_transform(
        [prediction]
    )[0]

    # Confidence
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        confidence = round(
            probabilities[prediction] * 100,
            2
        )
    else:
        confidence = None

    return predicted_document, confidence


# ---------------------------------------
# Test Prediction
# ---------------------------------------
if __name__ == "__main__":

    try:

        document, confidence = predict_document(
            business_type="Manufacturing",
            state="Tamil Nadu",
            registration_type="Private Limited",
            turnover=500
        )

        print("\nPrediction Successful")
        print("----------------------------")
        print("Predicted Document :", document)
        print("Confidence         :", confidence, "%")

    except Exception as e:
        print("Error:", e)