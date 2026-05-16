"""WSGI 진입점. PythonAnywhere /var/www/tarofortune_pythonanywhere_com_wsgi.py 에서 임포트한다."""
import sys
import os

PROJECT_PATH = '/home/tarofortune/mysite'
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from flask_app import app as application
