from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

class CustomerCreate(CustomerBase):
    pass

class PredictionSchema(BaseModel):
    prediction: str
    probability: float
    timestamp: datetime

    class Config:
        from_attributes = True

class CustomerSchema(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    prediction: Optional[PredictionSchema] = None

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_customers: int
    churn_percentage: float
    avg_monthly_charges: float
    high_risk_customers: int
