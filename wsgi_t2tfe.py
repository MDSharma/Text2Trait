"""
WSGI Entry Point for Text2Trait Frontend Application
======================================================

This module provides a Gunicorn-compatible WSGI entry point for the Text2Trait
frontend Dash application.

Usage with Gunicorn:
    gunicorn wsgi_t2tfe:server --bind 127.0.0.1:8050 --workers 4

Environment Setup:
    1. Install dependencies from text2trait_forntend_app/src/pyproject.toml
       (Note: directory name has typo 'forntend' - this is intentional, matching repo structure)
    2. Ensure all data files are in place
    3. Set appropriate environment variables if needed

The application is a Dash-based frontend that provides:
    - Multi-page navigation
    - Text2Trait data visualization
    - Interactive search functionality
    - Results visualization with Cytoscape graphs
"""

import sys
from pathlib import Path

# Add the frontend source directory to Python path
frontend_src = Path(__file__).parent / "text2trait_forntend_app" / "src"
sys.path.insert(0, str(frontend_src))

# Import the Dash app and expose the Flask server
from app import app

# Expose the WSGI server for Gunicorn
server = app.server

# For local testing only
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
