ALLOWED_HOSTS = ['your-render-app-url.onrender.com', 'localhost', '127.0.0.1']

# For production
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

LOGIN_URL = '/login/'
