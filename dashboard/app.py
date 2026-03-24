import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Customer Churn Analytics", layout="wide")

st.title("🚀 Real-Time ML Analytics: Customer Churn")

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

REFRESH_INTERVAL = 60
current_time = time.time()
if current_time - st.session_state.last_refresh > REFRESH_INTERVAL:
    st.session_state.last_refresh = current_time
    st.rerun()

def fetch_dashboard_data():
    try:
        response = requests.get(f"{API_URL}/dashboard")
        if response.status_code == 200:
            return response.json()
    except:
        return None

def fetch_customers():
    try:
        response = requests.get(f"{API_URL}/customers")
        if response.status_code == 200:
            return response.json()
    except:
        return []

stats = fetch_dashboard_data()
customers = fetch_customers()

st.sidebar.header("Customer Management")
mode = st.sidebar.radio("Action", ["Add New Customer", "Update Existing Customer"])

selected_customer = None
if mode == "Update Existing Customer":
    if customers:
        customer_ids = [c['id'] for c in customers]
        target_id = st.sidebar.selectbox("Select Customer ID to Update", customer_ids)
        selected_customer = next((c for c in customers if c['id'] == target_id), None)
    else:
        st.sidebar.warning("No customers found to update.")

with st.sidebar.form("customer_form"):
    st.subheader("Customer Details")
    
    # Pre-fill values if updating
    def get_val(key, default):
        if selected_customer:
            return selected_customer.get(key, default)
        return default

    gender = st.selectbox("Gender", ["Male", "Female"], 
                          index=["Male", "Female"].index(get_val("gender", "Male")))
    senior = st.selectbox("Senior Citizen", [0, 1], 
                          index=[0, 1].index(get_val("SeniorCitizen", 0)))
    partner = st.selectbox("Partner", ["Yes", "No"], 
                           index=["Yes", "No"].index(get_val("Partner", "No")))
    dependents = st.selectbox("Dependents", ["Yes", "No"], 
                              index=["Yes", "No"].index(get_val("Dependents", "No")))
    tenure = st.number_input("Tenure (months)", min_value=0, max_value=100, 
                             value=int(get_val("tenure", 12)))
    phone = st.selectbox("Phone Service", ["Yes", "No"], 
                         index=["Yes", "No"].index(get_val("PhoneService", "Yes")))
    multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"], 
                                  index=["Yes", "No", "No phone service"].index(get_val("MultipleLines", "No")))
    internet = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"], 
                            index=["DSL", "Fiber optic", "No"].index(get_val("InternetService", "Fiber optic")))
    security = st.selectbox("Online Security", ["Yes", "No", "No internet service"], 
                            index=["Yes", "No", "No internet service"].index(get_val("OnlineSecurity", "No")))
    online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"], 
                                 index=["Yes", "No", "No internet service"].index(get_val("OnlineBackup", "No")))
    device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"], 
                                     index=["Yes", "No", "No internet service"].index(get_val("DeviceProtection", "No")))
    tech = st.selectbox("Tech Support", ["Yes", "No", "No internet service"], 
                        index=["Yes", "No", "No internet service"].index(get_val("TechSupport", "No")))
    streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"], 
                                index=["Yes", "No", "No internet service"].index(get_val("StreamingTV", "No")))
    streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"], 
                                    index=["Yes", "No", "No internet service"].index(get_val("StreamingMovies", "No")))
    contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"], 
                            index=["Month-to-month", "One year", "Two year"].index(get_val("Contract", "Month-to-month")))
    paperless = st.selectbox("Paperless Billing", ["Yes", "No"], 
                             index=["Yes", "No"].index(get_val("PaperlessBilling", "Yes")))
    payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"], 
                                  index=["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"].index(get_val("PaymentMethod", "Electronic check")))
    charges = st.number_input("Monthly Charges", min_value=0.0, 
                              value=float(get_val("MonthlyCharges", 50.0)))
    total_charges = st.number_input("Total Charges", min_value=0.0, 
                                    value=float(get_val("TotalCharges", 600.0)))
    
    btn_label = "Predict & Update" if mode == "Update Existing Customer" else "Predict & Add"
    submit = st.form_submit_button(btn_label)
    
    if submit:
        payload = {
            "gender": gender,
            "SeniorCitizen": senior,
            "Partner": partner,
            "Dependents": dependents,
            "tenure": int(tenure),
            "PhoneService": phone,
            "MultipleLines": multiple_lines,
            "InternetService": internet,
            "OnlineSecurity": security,
            "OnlineBackup": online_backup,
            "DeviceProtection": device_protection,
            "TechSupport": tech,
            "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies,
            "Contract": contract,
            "PaperlessBilling": paperless,
            "PaymentMethod": payment_method,
            "MonthlyCharges": float(charges),
            "TotalCharges": float(total_charges)
        }
        
        if mode == "Add New Customer":
            res = requests.post(f"{API_URL}/customers", json=payload)
            msg = "Customer added and prediction generated!"
        else:
            res = requests.put(f"{API_URL}/customers/{selected_customer['id']}", json=payload)
            msg = "Customer updated and prediction recalculated!"
            
        if res.status_code == 200:
            st.sidebar.success(msg)
            st.session_state.last_refresh = 0 
            st.rerun()
        else:
            st.sidebar.error(f"Error: {res.status_code} - {res.text}")

stats = fetch_dashboard_data()
customers = fetch_customers()

if stats:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", stats['total_customers'])
    col2.metric("Churn Percentage", f"{stats['churn_percentage']:.1f}%")
    col3.metric("Avg Monthly Charges", f"${stats['avg_monthly_charges']:.2f}")
    col4.metric("High Risk Customers", stats['high_risk_customers'])

    if customers:
        df = pd.json_normalize(customers)
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Churn Distribution")
            fig_churn = px.pie(df, names='prediction.prediction', title='Churn vs Non-Churn', 
                                color='prediction.prediction', color_discrete_map={'Yes': '#EF553B', 'No': '#636EFA'})
            st.plotly_chart(fig_churn)
            
        with c2:
            st.subheader("Tenure vs Monthly Charges")
            fig_scatter = px.scatter(df, x='tenure', y='MonthlyCharges', color='prediction.prediction',
                                    title='Tenure vs Charges by Churn Prediction',
                                    labels={'prediction.prediction': 'Churn'})
            st.plotly_chart(fig_scatter)

        st.subheader("Recent Updates")
        st.dataframe(df[['id', 'gender', 'tenure', 'MonthlyCharges', 'Contract', 'prediction.prediction', 'prediction.probability']].tail(10))

else:
    st.warning("Could not connect to Backend API. Please ensure FastAPI is running.")

st.sidebar.markdown(f"---")
st.sidebar.caption(f"Last auto-refresh: {time.strftime('%H:%M:%S', time.localtime(st.session_state.last_refresh))}")

st.empty()
time.sleep(REFRESH_INTERVAL)
st.rerun()
