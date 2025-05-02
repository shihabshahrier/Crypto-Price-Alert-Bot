from app import app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response
from flask import Response as FlaskResponse
from asgiref.wsgi import WsgiToAsgi

asgi_app = WsgiToAsgi(app)
