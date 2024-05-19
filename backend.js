
const express = require('express');
const firebaseAdmin = require('firebase-admin');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

// Initialize Express app
const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Firebase Admin Setup
const serviceAccount = require('./firebase-config.json');
firebaseAdmin.initializeApp({
  credential: firebaseAdmin.credential.cert(serviceAccount)
});
const db = firebaseAdmin.firestore();
const collectionRef = db.collection('iot-db');
const dataFile = 'data.json';

// Function to fetch and store data
const fetchAndStoreData = async () => {
  console.log('fetching data from database');
  const componentData = {};
  const snapshot = await collectionRef.get();
  snapshot.forEach(doc => {
    const data = doc.data();
    for (const [component, value] of Object.entries(data)) {
      if (!componentData[component]) {
        componentData[component] = [];
      }
      componentData[component].push(value);
    }
  });

  fs.writeFileSync(dataFile, JSON.stringify(componentData));
  return componentData;
};

// Function to get data
const getData = async () => {
  if (!fs.existsSync(dataFile)) {
    return fetchAndStoreData();
  } else {
    console.log('fetching data from file');
    const data = fs.readFileSync(dataFile, 'utf-8');
    return JSON.parse(data);
  }
};

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'observation.html'));
});

app.get('/component-data', async (req, res) => {
  const data = await getData();
  console.log(Object.keys(data).length);
  res.json(data);
});

app.get('/correlation-data', async (req, res) => {
  const data = await getData();

  const tempData = data.temp || [];
  const motionData = data.motion || [];
  const humidityData = data.humidity || [];
  const waterData = data.water || [];

  const minLength = Math.min(tempData.length, motionData.length, humidityData.length, waterData.length);

  const tempArray = tempData.slice(0, minLength);
  const motionArray = motionData.slice(0, minLength);
  const humidityArray = humidityData.slice(0, minLength);
  const waterArray = waterData.slice(0, minLength);

  const tempMotionCorr = correlation(tempArray, motionArray);
  const tempHumidityCorr = correlation(tempArray, humidityArray);
  const tempWaterCorr = correlation(tempArray, waterArray);
  const motionHumidityCorr = correlation(motionArray, humidityArray);
  const motionWaterCorr = correlation(motionArray, waterArray);
  const humidityWaterCorr = correlation(humidityArray, waterArray);

  const correlations = {
    'Temp vs Motion': tempMotionCorr,
    'Temp vs Humidity': tempHumidityCorr,
    'Temp vs Water': tempWaterCorr,
    'Motion vs Humidity': motionHumidityCorr,
    'Motion vs Water': motionWaterCorr,
    'Humidity vs Water': humidityWaterCorr
  };

  res.json(correlations);
});

// Function to calculate correlation coefficient
const correlation = (x, y) => {
  const n = x.length;
  const meanX = x.reduce((a, b) => a + b, 0) / n;
  const meanY = y.reduce((a, b) => a + b, 0) / n;

  const covariance = x.reduce((sum, xi, i) => sum + (xi - meanX) * (y[i] - meanY), 0) / n;
  const stdDevX = Math.sqrt(x.reduce((sum, xi) => sum + Math.pow(xi - meanX, 2), 0) / n);
  const stdDevY = Math.sqrt(y.reduce((sum, yi) => sum + Math.pow(yi - meanY, 2), 0) / n);

  return covariance / (stdDevX * stdDevY);
};

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});