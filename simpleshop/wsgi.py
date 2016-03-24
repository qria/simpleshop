""" WSGI file for Heroku Deployment
"""
from simpleshop import create_app

app = create_app('simpleshop.settings.ProdConfig')