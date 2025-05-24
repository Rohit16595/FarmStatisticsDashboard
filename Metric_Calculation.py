import pandas as pd
import os
from datetime import datetime

def load_data():
    data_path = "data"
    os.makedirs(data_path, exist_ok=True)
    try:
        master = pd.read_csv(os.path.join(data_path, "master.csv"))
        device = pd.read_csv(os.path.join(data_path, "device_inventory.csv"))
        Disconnected = pd.read_csv(os.path.join(data_path, "Disconnected.csv"))
        return master, device, Disconnected
    except FileNotFoundError:
        return None, None, None

def calculate_metrics(selected_date, selected_cluster, selected_farm):
    master, device, Disconnected = load_data()
    
    # Filter master data
    farm_data = master[(master["cluster"] == selected_cluster) & 
                      (master["farm_name"] == selected_farm)]
    
    # Device calculations
    total_devices = device[device["farm_name"] == selected_farm]["device_id"].nunique()
    gateways = device[device["farm_name"] == selected_farm]["gatewayid"].nunique()
    
    # Disconnected calculations
    Disconnected["entry_date"] = pd.to_datetime(Disconnected["entry_date"])
    filtered_Disconnected = Disconnected[
        (Disconnected["entry_date"] == pd.to_datetime(selected_date)) &
        (Disconnected["farm_name"] == selected_farm) &
        (Disconnected["data_quality"] == "Disconnected")
    ]
    
    Disconnected_count = filtered_Disconnected.shape[0]
    c_type_Disconnected = filtered_Disconnected[
        filtered_Disconnected["Device_type"].str.contains("C")
    ].shape[0]
    
    # Gateway issue check
    gateway_issue = "Yes" if Disconnected_count == total_devices else "No"
    
    return {
        "vcm": farm_data["VCM"].values[0] if not farm_data.empty else "N/A",
        "total_devices": total_devices,
        "gateways": gateways,
        "Disconnected": Disconnected_count,
        "c_type_Disconnected": c_type_Disconnected,
        "gateway_issue": gateway_issue,
        "Disconnected_ids": filtered_Disconnected["device_id"].tolist(),
        "Device_types": filtered_Disconnected["Device_type"].value_counts()
    }
