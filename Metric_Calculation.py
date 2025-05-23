import pandas as pd
import os
from datetime import datetime

def load_data():
    data_path = "data"
    os.makedirs(data_path, exist_ok=True)
    try:
        master = pd.read_csv(os.path.join(data_path, "master.csv"))
        device = pd.read_csv(os.path.join(data_path, "device_inventory.csv"))
        disconnected = pd.read_csv(os.path.join(data_path, "disconnected.csv"))
        return master, device, disconnected
    except FileNotFoundError:
        return None, None, None

def calculate_metrics(selected_date, selected_cluster, selected_farm):
    master, device, disconnected = load_data()
    
    # Filter master data
    farm_data = master[(master["cluster"] == selected_cluster) & 
                      (master["farm_name"] == selected_farm)]
    
    # Device calculations
    total_devices = device[device["farm_name"] == selected_farm]["device_id"].nunique()
    gateways = device[device["farm_name"] == selected_farm]["gateway_id"].nunique()
    
    # Disconnected calculations
    disconnected["entry_date"] = pd.to_datetime(disconnected["entry_date"])
    filtered_disconnected = disconnected[
        (disconnected["entry_date"] == pd.to_datetime(selected_date)) &
        (disconnected["farm_name"] == selected_farm) &
        (disconnected["data_quality"] == "disconnected")
    ]
    
    disconnected_count = filtered_disconnected.shape[0]
    c_type_disconnected = filtered_disconnected[
        filtered_disconnected["Device_Type"].str.contains("C")
    ].shape[0]
    
    # Gateway issue check
    gateway_issue = "Yes" if disconnected_count == total_devices else "No"
    
    return {
        "vcm": farm_data["VCM"].values[0] if not farm_data.empty else "N/A",
        "total_devices": total_devices,
        "gateways": gateways,
        "disconnected": disconnected_count,
        "c_type_disconnected": c_type_disconnected,
        "gateway_issue": gateway_issue,
        "disconnected_ids": filtered_disconnected["device_id"].tolist(),
        "device_types": filtered_disconnected["Device_Type"].value_counts()
    }