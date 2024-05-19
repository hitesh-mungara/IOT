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
data_file = 'data.json'

def fetch_and_store_data():
    print("fetching data from database", end="")
    component_data = {}
    docs = collection_ref.get()
    for doc in docs:
        data = doc.to_dict()
        for component, value in data.items():
            if component not in component_data:
                component_data[component] = []
            component_data[component].append(value)

    with open(data_file, 'w') as f:
        json.dump(component_data, f)

    return component_data

def get_data():
    if not os.path.exists(data_file):
        return fetch_and_store_data()
    else:
        print("fetching data from file")
        with open(data_file, 'r') as f:
            return json.load(f)

@app.route('/')
def index():
    return render_template('observation.html')

@app.route('/component-data')
def component_data():
    data = get_data()
    print(len(data))
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
