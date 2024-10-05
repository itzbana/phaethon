#!/bin/bash

# Start the Dash app using Gunicorn
gunicorn app:app --bind 0.0.0.0:$PORT
