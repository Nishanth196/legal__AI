import os
import time
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

ML_DIR = os.path.dirname(os.path.abspath(__file__))


def load_and_preprocess_data(dataset_path, encoders=None):
    # 1. Load data
    df = pd.read_csv(dataset_path)

    # 2. Data Cleaning
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    # Convert Annual_Turnover_Lakhs to numeric
    if 'Annual_Turnover_Lakhs' in df.columns:
        df['Annual_Turnover_Lakhs'] = (
            df['Annual_Turnover_Lakhs']
            .astype(str)
            .str.replace(',', '', regex=False)
            .astype(float)
        )

    # 3. Label Encoding
    if encoders is None:
        business_encoder = LabelEncoder()
        state_encoder = LabelEncoder()
        registration_encoder = LabelEncoder()
        target_encoder = LabelEncoder()

        df['Business_Type_encoded'] = business_encoder.fit_transform(df['Business_Type'])
        df['State_encoded'] = state_encoder.fit_transform(df['State'])
        df['Registration_Type_encoded'] = registration_encoder.fit_transform(df['Registration_Type'])
        df['Required_Document_encoded'] = target_encoder.fit_transform(df['Required_Document'])

        encoders = {
            'business': business_encoder,
            'state': state_encoder,
            'registration': registration_encoder,
            'target': target_encoder
        }

    else:
        df['Business_Type_encoded'] = encoders['business'].transform(df['Business_Type'])
        df['State_encoded'] = encoders['state'].transform(df['State'])
        df['Registration_Type_encoded'] = encoders['registration'].transform(df['Registration_Type'])
        df['Required_Document_encoded'] = encoders['target'].transform(df['Required_Document'])

    X = df[['Business_Type_encoded', 'State_encoded',
            'Registration_Type_encoded', 'Annual_Turnover_Lakhs']]
    y = df['Required_Document_encoded']

    return X, y, encoders


def train_and_save_model(dataset_path):
    start_time = time.time()

    X, y, encoders = load_and_preprocess_data(dataset_path)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf_classifier = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    rf_classifier.fit(X_train, y_train)

    y_pred = rf_classifier.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()

    joblib.dump(rf_classifier, os.path.join(ML_DIR, "model.pkl"))
    joblib.dump(encoders['business'], os.path.join(ML_DIR, "business_encoder.pkl"))
    joblib.dump(encoders['state'], os.path.join(ML_DIR, "state_encoder.pkl"))
    joblib.dump(encoders['registration'], os.path.join(ML_DIR, "registration_encoder.pkl"))
    joblib.dump(encoders['target'], os.path.join(ML_DIR, "target_encoder.pkl"))

    training_time = time.time() - start_time

    return {
        "status": "Success",
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": cm,
        "training_time": training_time
    }


# ==========================
# Main Program
# ==========================
if __name__ == "__main__":
    dataset_path = os.path.join(ML_DIR, "sample_dataset.csv")

    result = train_and_save_model(dataset_path)

    print("Training Completed!")
    print(result)