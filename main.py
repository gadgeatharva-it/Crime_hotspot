import psycopg2
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import folium
from folium.plugins import MarkerCluster, HeatMap

# -------------------------------
# STEP 1: CONNECT TO DATABASE
# -------------------------------
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="123456",   # <-- your password
    host="localhost",
    port="5432"
)

# -------------------------------
# STEP 2: LOAD DATA
# -------------------------------
query = """
    SELECT latitude, longitude, crime_desc, crime_domain,
           city, victim_age, victim_gender, weapon_used,
           date_occurred, case_status
    FROM crime_incidents;
"""
df = pd.read_sql(query, conn)
conn.close()

print(f"✅ Data Loaded: {len(df)} records")
print(df.head())

# Clean data – drop rows with missing lat/lon
df = df.dropna(subset=['latitude', 'longitude'])
df = df[(df['latitude'] != 0) & (df['longitude'] != 0)]

# -------------------------------
# STEP 3: APPLY K-MEANS
# -------------------------------
N_CLUSTERS = 6
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(df[['latitude', 'longitude']])
df['cluster'] = df['cluster'].astype(int)

print(f"\n✅ K-Means clustering done ({N_CLUSTERS} clusters)")
print(df['cluster'].value_counts().sort_index())

# Cluster centers for summary markers
centers = kmeans.cluster_centers_

# -------------------------------
# STEP 4: CONFIGURE MAP STYLE
# -------------------------------

# Vibrant, distinct colors for each cluster
CLUSTER_COLORS = [
    '#e74c3c',   # Red
    '#3498db',   # Blue
    '#2ecc71',   # Green
    '#9b59b6',   # Purple
    '#f39c12',   # Orange
    '#1abc9c',   # Teal
]

CLUSTER_NAMES = [f'Hotspot Zone {i+1}' for i in range(N_CLUSTERS)]

# Folium icon colors (closest named colors for CircleMarker)
FOLIUM_COLORS = ['red', 'blue', 'green', 'purple', 'orange', 'darkgreen']

# Map center
center_lat = df['latitude'].mean()
center_lon = df['longitude'].mean()

# Create base map with a dark, attractive tile layer
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=5,
    tiles=None,       # We add tiles manually for layer control
    control_scale=True,
    prefer_canvas=True  # Better performance for many markers
)

# --- Multiple Tile Layers ---
folium.TileLayer(
    tiles='CartoDB dark_matter',
    name='🌙 Dark Mode',
    control=True
).add_to(m)

folium.TileLayer(
    tiles='CartoDB positron',
    name='☀️ Light Mode',
    control=True
).add_to(m)

folium.TileLayer(
    tiles='OpenStreetMap',
    name='🗺️ Street Map',
    control=True
).add_to(m)

# ========================================
# LAYER 1: HEATMAP (Background density)
# ========================================
heat_data = df[['latitude', 'longitude']].values.tolist()
heat_layer = folium.FeatureGroup(name='🔥 Crime Heatmap', show=True)
HeatMap(
    heat_data,
    min_opacity=0.3,
    max_zoom=13,
    radius=18,
    blur=22,
    gradient={
        '0.2': '#0d0887',
        '0.4': '#7e03a8',
        '0.6': '#cc4778',
        '0.8': '#f89540',
        '1.0': '#f0f921'
    }
).add_to(heat_layer)
heat_layer.add_to(m)

# ========================================
# LAYER 2: MARKER CLUSTERS (Detailed view)
# ========================================
# Create a MarkerCluster group per K-Means cluster so they are color-coded
for cluster_id in range(N_CLUSTERS):
    cluster_df = df[df['cluster'] == cluster_id]
    color = CLUSTER_COLORS[cluster_id]
    folium_color = FOLIUM_COLORS[cluster_id % len(FOLIUM_COLORS)]

    # Create a MarkerCluster with custom icon styling
    cluster_group = MarkerCluster(
        name=f'📍 {CLUSTER_NAMES[cluster_id]} ({len(cluster_df):,} crimes)',
        show=True,
        options={
            'maxClusterRadius': 50,
            'spiderfyOnMaxZoom': True,
            'showCoverageOnHover': True,
            'zoomToBoundsOnClick': True,
            'disableClusteringAtZoom': 14,
        }
    )

    # Sample markers if too many (performance guard; still shows all in clusters)
    # For full detail: iterate all rows
    for _, row in cluster_df.iterrows():
        # Build a rich HTML popup
        crime_desc = row.get('crime_desc', 'N/A')
        crime_domain = row.get('crime_domain', 'N/A')
        city = row.get('city', 'N/A')
        victim_age = row.get('victim_age', 'N/A')
        victim_gender = row.get('victim_gender', 'N/A')
        weapon = row.get('weapon_used', 'N/A')
        date_occ = row.get('date_occurred', 'N/A')
        case_status = row.get('case_status', 'N/A')

        # Status badge color
        status_bg = '#27ae60' if str(case_status).strip().lower() == 'closed' else '#e74c3c'

        popup_html = f"""
        <div style="font-family:'Segoe UI',Roboto,sans-serif; width:280px; padding:0; margin:0;">
            <div style="background:linear-gradient(135deg, {color}, #2c3e50); padding:10px 14px;
                        border-radius:8px 8px 0 0; color:white;">
                <div style="font-size:13px; font-weight:700; text-transform:uppercase;
                            letter-spacing:0.5px;">⚠️ {crime_desc}</div>
                <div style="font-size:11px; margin-top:4px; opacity:0.85;">{crime_domain}</div>
            </div>
            <div style="padding:10px 14px; background:#1a1a2e; color:#eee;
                        border-radius:0 0 8px 8px; font-size:12px; line-height:1.7;">
                <div>📍 <b>City:</b> {city}</div>
                <div>📅 <b>Date:</b> {date_occ}</div>
                <div>👤 <b>Victim:</b> Age {victim_age}, {victim_gender}</div>
                <div>🔫 <b>Weapon:</b> {weapon}</div>
                <div style="margin-top:6px;">
                    <span style="background:{status_bg}; color:white; padding:2px 8px;
                                 border-radius:10px; font-size:11px; font-weight:600;">
                        {case_status}
                    </span>
                </div>
            </div>
        </div>
        """

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            weight=1,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{crime_desc} — {city}"
        ).add_to(cluster_group)

    cluster_group.add_to(m)

# ========================================
# LAYER 3: CLUSTER CENTER SUMMARY MARKERS
# ========================================
centers_group = folium.FeatureGroup(name='🎯 Cluster Centers (Summary)', show=True)

for cluster_id in range(N_CLUSTERS):
    clat, clon = centers[cluster_id]
    cluster_df = df[df['cluster'] == cluster_id]
    color = CLUSTER_COLORS[cluster_id]
    count = len(cluster_df)

    # Compute summary stats for this cluster
    top_crimes = cluster_df['crime_desc'].value_counts().head(3)
    top_cities = cluster_df['city'].value_counts().head(3)
    closed_pct = (cluster_df['case_status'].str.strip().str.lower() == 'closed').mean() * 100

    top_crimes_html = ''.join(
        f'<div style="display:flex;justify-content:space-between;">'
        f'<span>{crime}</span><span style="font-weight:700">{cnt}</span></div>'
        for crime, cnt in top_crimes.items()
    )
    top_cities_html = ''.join(
        f'<div style="display:flex;justify-content:space-between;">'
        f'<span>{city}</span><span style="font-weight:700">{cnt}</span></div>'
        for city, cnt in top_cities.items()
    )

    summary_html = f"""
    <div style="font-family:'Segoe UI',Roboto,sans-serif; width:300px;">
        <div style="background:linear-gradient(135deg, {color}, #0f0f1a); padding:12px 16px;
                    border-radius:10px 10px 0 0; color:white; text-align:center;">
            <div style="font-size:15px; font-weight:800; letter-spacing:1px;">
                🎯 {CLUSTER_NAMES[cluster_id]}
            </div>
            <div style="font-size:28px; font-weight:900; margin:4px 0;">{count:,}</div>
            <div style="font-size:11px; opacity:0.8;">Total Crimes</div>
        </div>
        <div style="padding:12px 16px; background:#16213e; color:#ddd;
                    font-size:12px; line-height:1.6;">
            <div style="font-weight:700; color:{color}; margin-bottom:4px; font-size:13px;">
                🔝 Top Crimes
            </div>
            {top_crimes_html}
            <hr style="border:0; border-top:1px solid #333; margin:8px 0;">
            <div style="font-weight:700; color:{color}; margin-bottom:4px; font-size:13px;">
                🏙️ Top Cities
            </div>
            {top_cities_html}
            <hr style="border:0; border-top:1px solid #333; margin:8px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span>📊 Case Closure Rate</span>
                <span style="font-weight:800; font-size:14px; color:#2ecc71;">
                    {closed_pct:.1f}%
                </span>
            </div>
        </div>
        <div style="background:#0f0f1a; padding:6px; border-radius:0 0 10px 10px;
                    text-align:center; font-size:10px; color:#666;">
            Lat: {clat:.4f} | Lon: {clon:.4f}
        </div>
    </div>
    """

    folium.Marker(
        location=[clat, clon],
        popup=folium.Popup(summary_html, max_width=320),
        tooltip=f"🎯 {CLUSTER_NAMES[cluster_id]} — {count:,} crimes",
        icon=folium.DivIcon(
            icon_size=(44, 44),
            icon_anchor=(22, 22),
            html=f"""
            <div style="
                background: radial-gradient(circle, {color}, #0f0f1a);
                width:44px; height:44px; border-radius:50%;
                display:flex; align-items:center; justify-content:center;
                color:white; font-weight:900; font-size:14px;
                border:3px solid white; box-shadow:0 0 15px {color}88;
                font-family:'Segoe UI',sans-serif;">
                {cluster_id+1}
            </div>
            """
        )
    ).add_to(centers_group)

centers_group.add_to(m)

# ========================================
# LEGEND
# ========================================
legend_items = ''.join(
    f'<div style="display:flex; align-items:center; margin:4px 0;">'
    f'<span style="width:14px; height:14px; background:{CLUSTER_COLORS[i]}; '
    f'border-radius:50%; display:inline-block; margin-right:8px; '
    f'box-shadow:0 0 6px {CLUSTER_COLORS[i]}88;"></span>'
    f'<span>{CLUSTER_NAMES[i]}</span></div>'
    for i in range(N_CLUSTERS)
)

legend_html = f"""
<div style="
    position:fixed; bottom:30px; left:30px; z-index:9999;
    background:rgba(15,15,26,0.92); padding:16px 20px;
    border-radius:12px; border:1px solid #333;
    color:#eee; font-family:'Segoe UI',Roboto,sans-serif;
    font-size:12px; backdrop-filter:blur(10px);
    box-shadow:0 8px 32px rgba(0,0,0,0.4);">
    <div style="font-weight:800; font-size:14px; margin-bottom:8px;
                letter-spacing:0.5px; color:#f39c12;">
        🗺️ CRIME HOTSPOT CLUSTERS
    </div>
    {legend_items}
    <hr style="border:0; border-top:1px solid #333; margin:8px 0;">
    <div style="font-size:10px; color:#888;">
        K-Means Clustering (k={N_CLUSTERS})<br>
        Total Records: {len(df):,}
    </div>
</div>
"""

m.get_root().html.add_child(folium.Element(legend_html))

# --- Title Banner ---
title_html = """
<div style="
    position:fixed; top:10px; left:50%; transform:translateX(-50%);
    z-index:9999; background:rgba(15,15,26,0.88); padding:10px 28px;
    border-radius:30px; border:1px solid #333;
    color:white; font-family:'Segoe UI',Roboto,sans-serif;
    font-size:16px; font-weight:700; letter-spacing:1px;
    backdrop-filter:blur(10px); box-shadow:0 4px 20px rgba(0,0,0,0.3);
    text-align:center;">
    🔍 Crime Hotspot Analysis — India &nbsp;
    <span style="font-size:11px; color:#f39c12; font-weight:400;">
        Powered by K-Means Clustering
    </span>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# --- Layer Control ---
folium.LayerControl(collapsed=False, position='topright').add_to(m)

# -------------------------------
# STEP 5: SAVE MAP
# -------------------------------
m.save("crime_hotspots.html")

print(f"\n✅ Enhanced map saved! Open 'crime_hotspots.html'")
print(f"   📊 {len(df):,} crime records mapped across {N_CLUSTERS} clusters")
print(f"   🗺️  Features: MarkerCluster, HeatMap, Detailed Popups, Layer Controls")