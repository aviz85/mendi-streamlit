"""
קובץ כניסה ראשי לאפליקציית Streamlit לעיבוד מסמכים משפטיים

מפעיל את האפליקציה לעיבוד מסמכים משפטיים ומכין את הסביבה הדרושה.
"""

import streamlit as st
import logging
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Import the main application module
from app.document_processor_app import main

# Run the application
if __name__ == "__main__":
    main() 