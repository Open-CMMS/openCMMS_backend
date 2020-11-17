"""
WSGI config for openCMMS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if 'pic_settings.py' not in os.listdir():
    print('je suis la')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openCMMS.base_settings')
else :
    print('Jsuis rentré ici')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openCMMS.pic_settings')

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openCMMS.settings')

application = get_wsgi_application()
