from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, ml_utils
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Churn Prediction API")

@app.post("/customers", response_model=schemas.CustomerSchema)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    prediction_label, probability = ml_utils.get_prediction(**customer.dict())
    
    db_prediction = models.Prediction(
        customer_id=db_customer.id,
        prediction=prediction_label,
        probability=probability
    )
    db.add(db_prediction)
    db.commit()
    
    return db_customer

@app.put("/customers/{customer_id}", response_model=schemas.CustomerSchema)
def update_customer(customer_id: int, customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in customer.dict().items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    
    prediction_label, probability = ml_utils.get_prediction(**customer.dict())
    
    db_prediction = db.query(models.Prediction).filter(models.Prediction.customer_id == customer_id).first()
    if db_prediction:
        db_prediction.prediction = prediction_label
        db_prediction.probability = probability
    else:
        db_prediction = models.Prediction(
            customer_id=db_customer.id,
            prediction=prediction_label,
            probability=probability
        )
        db.add(db_prediction)
    
    db.commit()
    return db_customer

@app.get("/customers", response_model=List[schemas.CustomerSchema])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()

@app.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(models.Customer).count()
    if total == 0:
        return {
            "total_customers": 0,
            "churn_percentage": 0,
            "avg_monthly_charges": 0,
            "high_risk_customers": 0
        }
    
    churn_count = db.query(models.Prediction).filter(models.Prediction.prediction == "Yes").count()
    avg_charges = db.query(models.Customer).with_entities(models.func.avg(models.Customer.MonthlyCharges)).scalar() or 0
    high_risk = db.query(models.Prediction).filter(models.Prediction.probability >= 0.7).count()
    
    return {
        "total_customers": total,
        "churn_percentage": (churn_count / total) * 100,
        "avg_monthly_charges": float(avg_charges),
        "high_risk_customers": high_risk
    }
