import streamlit as st
import pandas as pd
import plotly.express as px
from auth import login_page, load_users
from data_processor import load_data, calculate_metrics
import os
import bcrypt

# ---------------------------
# ADMIN BACKEND
# ---------------------------
def admin_backend():
    st.title("Admin Dashboard")
    
    # File upload section
    st.header("Data Upload Center")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Master File")
        master_file = st.file_uploader("Upload farm metadata", 
                                      type=["csv", "xlsx"], 
                                      key="master")
        if master_file:
            process_file(master_file, "master.csv")
    
    with col2:
        st.subheader("Device Inventory")
        device_file = st.file_uploader("Upload device details", 
                                      type=["csv", "xlsx"], 
                                      key="device")
        if device_file:
            process_file(device_file, "device_inventory.csv")
    
    with col3:
        st.subheader("Disconnected Devices")
        disconnected_file = st.file_uploader("Upload status data", 
                                           type=["csv", "xlsx"], 
                                           key="disconnected")
        if disconnected_file:
            process_file(disconnected_file, "disconnected.csv")

    # User management
    st.header("User Management")
    with st.form("user_form"):
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["user", "admin"])
        
        if st.form_submit_button("Create User"):
            create_user(new_user, new_pass, new_role)

def process_file(uploaded_file, target_name):
    try:
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        df.to_csv(os.path.join("data", target_name), index=False)
        st.success(f"{target_name.replace('.csv', '")} uploaded successfully!")
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def create_user(username, password, role):
    users_df = load_users()
    if username in users_df["username"].values:
        st.error("Username already exists!")
    else:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_user = pd.DataFrame([{
            "username": username,
            "password": hashed_pw,
            "role": role
        }])
        users_df = pd.concat([users_df, new_user])
        users_df.to_csv("users.csv", index=False)
        st.success(f"User {username} created!")

# ---------------------------
# USER FRONTEND
# ---------------------------
def user_frontend():
    st.title("Farm Analytics Dashboard")
    
    master, device, disconnected = load_data()
    
    # Date selection
    if disconnected is not None:
        dates = pd.to_datetime(disconnected["entry_date"]).dt.date.unique()
        default_date = pd.to_datetime(disconnected["entry_date"]).max().date()
    else:
        dates = []
        default_date = pd.to_datetime("today").date()
    
    selected_date = st.date_input("Select Date", value=default_date)
    
    if master is not None:
        # Farm selection
        selected_cluster = st.selectbox("Cluster", master["cluster"].unique())
        farms = master[master["cluster"] == selected_cluster]["farm_name"].unique()
        selected_farm = st.selectbox("Farm", farms)
        
        # Get metrics
        metrics = calculate_metrics(selected_date, selected_cluster, selected_farm)
        
        # Display farm info
        col1, col2, col3 = st.columns(3)
        col1.metric("Farm Name", selected_farm)
        col2.metric("Cluster", selected_cluster)
        col3.metric("VCM", metrics["vcm"])
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Devices", metrics["total_devices"])
        col2.metric("Gateways", metrics["gateways"])
        col3.metric("Disconnected", metrics["disconnected"])
        col4.metric("C-Type Disconnected", metrics["c_type_disconnected"])
        
        # Pie chart
        if not metrics["device_types"].empty:
            fig = px.pie(metrics["device_types"], 
                         values=metrics["device_types"].values,
                         names=metrics["device_types"].index,
                         title="Device Type Distribution")
            st.plotly_chart(fig)
        
        # Disconnected devices list
        st.subheader("Disconnected Devices")
        if metrics["disconnected_ids"]:
            st.write(metrics["disconnected_ids"])
        else:
            st.info("No disconnected devices")
        
        # Gateway status
        st.metric("Gateway Issue", metrics["gateway_issue"])
    else:
        st.warning("No data available. Please contact admin.")

# ---------------------------
# MAIN APP
# ---------------------------
def main():
    if "logged_in" not in st.session_state:
        login_page()
    else:
        if st.session_state["role"] == "admin":
            admin_backend()
        else:
            user_frontend()

if __name__ == "__main__":
    main()