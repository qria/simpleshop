""" WSGI file for Heroku Deployment
"""
from simpleshop import create_app

application = app = create_app('simpleshop.settings.ProdConfig')