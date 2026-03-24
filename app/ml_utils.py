import joblib
import pandas as pd
import os

MODEL_PATH = r'c:\Users\anasr\Downloads\aa\model.pkl'

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

model = None

def get_prediction(gender: str, SeniorCitizen: int, Partner: str, Dependents: str, 
                   tenure: int, PhoneService: str, MultipleLines: str, 
                   InternetService: str, OnlineSecurity: str, OnlineBackup: str, 
                   DeviceProtection: str, TechSupport: str, StreamingTV: str, 
                   StreamingMovies: str, Contract: str, PaperlessBilling: str, 
                   PaymentMethod: str, MonthlyCharges: float, TotalCharges: float):
    global model
    if model is None:
        model = load_model()
    
    input_data = pd.DataFrame([{
        'gender': gender,
        'seniorcitizen': SeniorCitizen,
        'partner': Partner,
        'dependents': Dependents,
        'tenure': tenure,
        'phoneservice': PhoneService,
        'multiplelines': MultipleLines,
        'internetservice': InternetService,
        'onlinesecurity': OnlineSecurity,
        'onlinebackup': OnlineBackup,
        'deviceprotection': DeviceProtection,
        'techsupport': TechSupport,
        'streamingtv': StreamingTV,
        'streamingmovies': StreamingMovies,
        'contract': Contract,
        'paperlessbilling': PaperlessBilling,
        'paymentmethod': PaymentMethod,
        'monthlycharges': MonthlyCharges,
        'totalcharges': TotalCharges
    }])
    
    prob = model.predict_proba(input_data)[0][1]
    pred_label = "Yes" if prob >= 0.5 else "No"
    
    return pred_label, float(prob)
