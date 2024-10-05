import numpy as np
import pandas as pd
from scipy.optimize import newton

# Function to solve Kepler's equation using Newton-Raphson method
def solve_kepler(M, e):
    M = np.radians(M)  # Convert to radians
    return newton(lambda E: E - e * np.sin(E) - M, M)

# Vectorized function to compute heliocentric coordinates and anomalies
def compute_heliocentric_and_anomalies(df):
    M = np.radians(df['M'])  # Mean anomaly in radians
    e = df['e']  # Eccentricity

    # Solve for Eccentric Anomaly (E)
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

    # Rotate to heliocentric ecliptic coordinates
    x = (np.cos(Omega) * np.cos(omega) - np.sin(Omega) * np.sin(omega) * np.cos(i)) * x_prime + \
        (-np.cos(Omega) * np.sin(omega) - np.sin(Omega) * np.cos(omega) * np.cos(i)) * y_prime
    y = (np.sin(Omega) * np.cos(omega) + np.cos(Omega) * np.sin(omega) * np.cos(i)) * x_prime + \
        (-np.sin(Omega) * np.sin(omega) + np.cos(Omega) * np.cos(omega) * np.cos(i)) * y_prime
    z = (np.sin(i) * np.sin(omega)) * x_prime + (np.sin(i) * np.cos(omega)) * y_prime
    
    return x, y, z, E, nu

# Load the JSON data
df = pd.read_json('csvjson.json')

# Precompute coordinates and anomalies
x_coords, y_coords, z_coords, eccentric_anomalies, true_anomalies = compute_heliocentric_and_anomalies(df)

# Add the results to the DataFrame
df['x'] = x_coords
df['y'] = y_coords
df['z'] = z_coords
df['eccentric_anomaly'] = np.degrees(eccentric_anomalies)  # Convert to degrees
df['true_anomaly'] = np.degrees(true_anomalies)  # Convert to degrees

# Save the DataFrame with the new columns to a new JSON file
df.to_json('precomputed_kepler_data.json', orient='records')
