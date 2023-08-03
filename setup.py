from setuptools import setup, find_packages

import subprocess

def can_install_markdown():
    choice = subprocess.run(['python3', 'pre_install.py'], capture_output=True, check=True, text=True)
    match choice.stdout.strip():
        case 'Y' | "YES" | 'y' | 'yes' | 'Yes':
            subprocess.run(['pip', 'install', 'django-markdownx>4.0.2'], check=True)
        case _:
            return None


setup(
    name='dj_dynamic_templates',
    version="1.0.1",
    description='An Django python package for dynamic mail templates through admin panel.',
    author="sudheer",
    author_email='sudheer@vishgyana.com',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License", "Operating System :: OS Independent", 'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: Django',
    ],
    install_requires=['Django>=3.0', ],
    url='https://github.com/sudheervgts/dj_dynamic_templates.git',
    license='MIT',
    platforms=['any'],
    package_data={
        'dj_dynamic_templates': ['templates/**/*.html']
    },

)

# can_install_markdown()
