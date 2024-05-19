import json
import random

def generate_sample_data(num_records):
    data = {
        'temp': [],
        'motion': [],
        'humidity': [],
        'water': []
    }
    
    for _ in range(num_records):
        temp = round(random.uniform(30, 40), 2)       
        motion = random.choice([0, 1])                
        humidity = round(random.uniform(60, 100), 2)   
        water = round(random.uniform(1800, 4500), 2)  
        
        data['temp'].append(temp)
        data['motion'].append(motion)
        data['humidity'].append(humidity)
        data['water'].append(water)
    
    return data

num_records = 20000
sample_data = generate_sample_data(num_records)

data_file = 'data.json'
with open(data_file, 'w') as f:
    json.dump(sample_data, f)

print(f'{num_records} records generated and stored in {data_file}')
