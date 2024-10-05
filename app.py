import numpy as np
import pandas as pd
from scipy.optimize import newton
import random
import requests
import plotly.graph_objects as go
import dash
from dash import dcc, html

# Function to solve Kepler's equation using Newton-Raphson method
def solve_kepler(M, e):
    M = np.radians(M)  # Convert to radians
    return newton(lambda E: E - e * np.sin(E) - M, M)

# Vectorized function to compute (x, y, z) heliocentric coordinates for multiple objects
def compute_heliocentric_xyz_vectorized(df):
    M = np.radians(df['M'])  # Mean anomaly in radians
    e = df['e']  # Eccentricity

    # Solve for Eccentric Anomaly (E) using vectorized method
    E = solve_kepler(df['M'], e)

    # Compute true anomaly ν
    nu = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))

    # Compute heliocentric distance (r is in AU)
    a = df['a']  # Semi-major axis in AU
    r = (a * (1 - e**2)) / (1 + e * np.cos(nu))

    # Convert angles to radians (i, Omega, omega are in degrees)
    i = np.radians(df['i'])
    Omega = np.radians(df['node'])
    omega = np.radians(df['peri'])

    # Position in orbital plane
    x_prime = r * np.cos(nu)
    y_prime = r * np.sin(nu)

    # Rotate to heliocentric ecliptic coordinates (vectorized)
    x = (np.cos(Omega) * np.cos(omega) - np.sin(Omega) * np.sin(omega) * np.cos(i)) * x_prime + \
        (-np.cos(Omega) * np.sin(omega) - np.sin(Omega) * np.cos(omega) * np.cos(i)) * y_prime
    y = (np.sin(Omega) * np.cos(omega) + np.cos(Omega) * np.sin(omega) * np.cos(i)) * x_prime + \
        (-np.sin(Omega) * np.sin(omega) + np.cos(Omega) * np.cos(omega) * np.cos(i)) * y_prime
    z = (np.sin(i) * np.sin(omega)) * x_prime + (np.sin(i) * np.cos(omega)) * y_prime
    
    return x, y, z

# Load data from the provided JSON URL
url = 'https://raw.githubusercontent.com/itzbana/phaethon/refs/heads/main/csvtojson.json'
response = requests.get(url)
data = response.json()

# Convert the JSON data to a DataFrame
df = pd.DataFrame(data)

# Compute coordinates
x_coords, y_coords, z_coords = compute_heliocentric_xyz_vectorized(df)

# Generate random colors for each object
colors = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(len(df))]

# Create hover text that includes both the full name and Keplerian results
hover_texts = []
for index, row in df.iterrows():
    M = row['M']  # Mean anomaly
    e = row['e']  # Eccentricity
    E = solve_kepler(M, e)  # Solve for Eccentric Anomaly
    true_anomaly = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))  # Calculate true anomaly

    # Format the hover text
    hover_texts.append(f"{row['full_name']}<br>True Anomaly: {np.degrees(true_anomaly):.2f} degrees<br>Eccentricity: {e}")

# Earth's coordinates and hover text
earth_x, earth_y, earth_z = 0, 0, 0  # Earth's position
earth_hover_text = "Earth<br>True Anomaly: 0.00 degrees<brEccentricity: 0.0167"  # Earth's data

# Create a 3D scatter plot with Plotly
fig = go.Figure(data=[go.Scatter3d(
    x=x_coords,
    y=y_coords,
    z=z_coords,
    mode='markers',
    marker=dict(
        size=5,
        color=colors  # Random color for each point
    ),
    text=hover_texts,  # Set the hover text to include both full name and Keplerian results
    hoverinfo='text'  # Show only the text on hover
)])

# Add Earth as a larger point
fig.add_trace(go.Scatter3d(
    x=[earth_x],
    y=[earth_y],
    z=[earth_z],
    mode='markers',
    marker=dict(
        size=35,  # Increased size for Earth
        color='blue'  # Color for Earth
    ),
    text=[earth_hover_text],
    hoverinfo='text'
))

fig.update_layout(
    scene=dict(
        xaxis_title='X (AU)',
        yaxis_title='Y (AU)',
        zaxis_title='Z (AU)'
    ),
    title="Heliocentric Positions of Objects"
)

# Show the plot in Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(figure=fig, style={'height': '100vh', 'width': '100vw'})  # Full-screen layout
], style={'margin': '0', 'padding': '0'})  # Remove default margins/padding for full-screen view

if __name__ == '__main__':
    app.run_server(debug=True)
