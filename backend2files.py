from flask import Flask, jsonify, render_template
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import numpy as np
import os
import json

app = Flask(__name__)

cred = credentials.Certificate("iot-project-e5a3f-8dd21e2b07ef.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref = db.collection("iot-db")
data_files = ['data1.json', 'data2.json']
data_file = 'data.json'

def fetch_and_store_data():
    print("fetching data form database", end="")
    component_data = {}
    docs = collection_ref.get()
    print(len(docs))
    for doc in docs:
        data = doc.to_dict()
        for component, value in data.items():
            if component not in component_data:
                component_data[component] = []
            component_data[component].append(value)

    with open(data_file, 'w') as f:
        json.dump(component_data, f)

    return component_data

def load_data_from_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return json.load(f)
    return {}

def get_data():
    if not all(os.path.exists(file) for file in data_files):
        return fetch_and_store_data()
    else:
        print("fetching data from files")
        data1 = load_data_from_file(data_files[0])
        data2 = load_data_from_file(data_files[1])
        
        combined_data = {}
        for key in set(data1.keys()).union(data2.keys()):
            combined_data[key] = data1.get(key, []) + data2.get(key, [])
        return combined_data

@app.route('/')
def index():
    return render_template('frontend.html')

@app.route('/component-data')
def component_data():
    data = get_data()
    return jsonify(data)

@app.route('/correlation-data')
def correlation_data():
    data = get_data()

    temp_data = data.get('temp', [])
    motion_data = data.get('motion', [])
    humidity_data = data.get('humidity', [])
    water_data = data.get('water', [])

    min_length = min(len(temp_data), len(motion_data), len(humidity_data), len(water_data))

    temp_array = np.array(temp_data[:min_length])
    motion_array = np.array(motion_data[:min_length])
    humidity_array = np.array(humidity_data[:min_length])
    water_array = np.array(water_data[:min_length])

    temp_motion_corr = np.corrcoef(temp_array, motion_array)[0, 1]
    temp_humidity_corr = np.corrcoef(temp_array, humidity_array)[0, 1]
    temp_water_corr = np.corrcoef(temp_array, water_array)[0, 1]
    motion_humidity_corr = np.corrcoef(motion_array, humidity_array)[0, 1]
    motion_water_corr = np.corrcoef(motion_array, water_array)[0, 1]
    humidity_water_corr = np.corrcoef(humidity_array, water_array)[0, 1]

    correlations = {
        'Temp vs Motion': temp_motion_corr,
        'Temp vs Humidity': temp_humidity_corr,
        'Temp vs Water': temp_water_corr,
        'Motion vs Humidity': motion_humidity_corr,
        'Motion vs Water': motion_water_corr,
        'Humidity vs Water': humidity_water_corr
    }

    return jsonify(correlations)


if __name__ == '__main__':
    app.run(debug=True)
