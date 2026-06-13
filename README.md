# 🚨 Crime Hotspot Analysis — India

An interactive geospatial analytics platform that identifies high-risk crime zones using K-Means clustering and visualizes them through dynamic heatmaps.

## 📌 Overview

Analyzed 3.7 lakh+ crime records to detect spatial crime patterns and segment regions into hotspots. The system provides actionable insights to support crime monitoring and efficient resource allocation.

## ⚙️ Features

- 🔍 K-Means clustering (k=6) for hotspot detection
- 🗺️ Interactive map using Folium & Leaflet
- 🔥 Crime heatmap visualization
- 📊 Cluster-wise crime distribution
- 🌙 Dark/Light mode toggle
- 📍 Cluster center summary markers

## 🧠 Tech Stack

- Frontend: HTML, CSS, JavaScript
- Visualization: Folium, Leaflet.js
- Data Analysis: Pandas, NumPy
- ML: Scikit-learn (K-Means)
- Database: PostgreSQL

## 🚀 How It Works

1. Preprocessed and cleaned crime dataset
2. Applied K-Means clustering to identify high-risk zones
3. Generated geospatial heatmaps and cluster markers
4. Visualized insights on an interactive map

## 📂 Project Structure

- backend/ → API & server logic
- frontend/ → UI and visualization
- config.js → API base URL

## 🌐 Setup

1. Run backend: `npm install && npm start`
2. Open frontend `index.html` or deploy
3. Set API URL in config.js

## 📈 Impact

- Identifies crime-prone regions
- Supports data-driven policing
- Improves resource allocation strategies

## 👨‍💻 Author

Atharva Gadge
