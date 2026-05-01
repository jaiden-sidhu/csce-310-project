"""
Configuration settings for the Online Bookstore application
"""

# Database configuration
DB_CONFIG = {
    'user': '[enter user here]',
    'password': '[enter password here]',
    'host': '[enter host here]',
    'database': '[enter database name here]'
}

# Flask configuration
FLASK_PORT = 5000
FLASK_HOST = 'localhost'

# API endpoints
API_BASE_URL = f'http://{FLASK_HOST}:{FLASK_PORT}/api'

# Bill directory
BILL_DIRECTORY = './bills'
