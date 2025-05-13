import os
from django.core.wsgi import get_wsgi_application

# Update the settings module to reflect your actual project directory name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot.settings')

application = get_wsgi_application()
