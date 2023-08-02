
import subprocess

import sys

def install_django_markdownx():
    response = input("Can we Install Django Markdownx")
    if response in ['y', 'Y', 'yes', 'Yes']:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'django-markdownx>=4.0.2'])
    else:
        pass
