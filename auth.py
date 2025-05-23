import streamlit as st
import pandas as pd
import bcrypt
import os

def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    return pd.DataFrame(columns=["username", "password", "role"])

def save_users(users_df):
    users_df.to_csv("users.csv", index=False)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode(), hashed_password.encode())

def login_page():
    st.title("Farm Analytics Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        users_df = load_users()
        user = users_df[users_df["username"] == username]
        if not user.empty and verify_password(password, user.iloc[0]["password"]):
            st.session_state.update({
                "logged_in": True,
                "username": username,
                "role": user.iloc[0]["role"]
            })
            st.rerun()
        else:
            st.error("Invalid credentials")