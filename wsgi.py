import sys
import os

project_home = '/home/yourusername/auth-service'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app.main import app
from asgiref.wsgi import WsgiToAsgi

application = WsgiToAsgi(app)