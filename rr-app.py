import os
import pandas as pd
import random
import plotly.graph_objects as go
import dash
from dash import dcc, html

# Load precomputed data from the new JSON file
url = 'https://raw.githubusercontent.com/itzbana/phaethon/refs/heads/main/precomputed_kepler_data.json'
df = pd.read_json(url)

# Generate random colors for each object
colors = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(len(df))]

# Create hover text that includes the full name, eccentric anomaly, and true anomaly
hover_texts = []
for index, row in df.iterrows():
    hover_texts.append(f"{row['full_name']}<br>True Anomaly: {row['true_anomaly']:.2f} degrees<br>Eccentricity: {row['e']}")

# Earth's coordinates and hover text
earth_x, earth_y, earth_z = 0, 0, 0  # Earth's position at the center
earth_hover_text = "Earth<br>True Anomaly: 0.00 degrees<br>Eccentricity: 0.0167"  # Earth's precomputed data

# Create a Dash app
app = dash.Dash(__name__)

# Layout with dcc.Store to hold preloaded data
app.layout = html.Div([
    dcc.Store(id='data-store', data=df.to_dict('records')),  # Store the data in dcc.Store
    dcc.Graph(id='3d-graph', style={'height': '100vh', 'width': '100vw'})  # Full-screen layout
], style={'margin': '0', 'padding': '0'})  # Remove default margins/padding for full-screen view

@app.callback(
    dash.dependencies.Output('3d-graph', 'figure'),
    dash.dependencies.Input('data-store', 'data')  # Input from dcc.Store
)
def update_graph(data):
    # Convert the data back to DataFrame
    df_data = pd.DataFrame(data)

    # Use the precomputed coordinates
    x_coords = df_data['x']
    y_coords = df_data['y']
    z_coords = df_data['z']

    # Create a 3D scatter plot with Plotly using scattergl
    fig = go.Figure(data=[go.Scattergl(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        mode='markers',
        marker=dict(
            size=5,
            color=colors  # Random color for each point
        ),
        text=hover_texts,  # Set the hover text to include both full name and precomputed results
        hoverinfo='text'  # Show only the text on hover
    )])

    # Add Earth as a larger point
    fig.add_trace(go.Scattergl(
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
    
    return fig

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=True)
