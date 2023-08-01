from setuptools import setup, find_packages

setup(name='dj_dynamic_templates',
      version="1.0.1",
      description='An Django python package for dynamic mail templates through admin panel.',
      author="sudheer",
      author_email='v.sudheerkumar91@gmail.com',
      packages=find_packages(),
      include_package_data=True,
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Framework :: Django',
      ],
      install_requires=[
            'Django>=3.0',
            'django-markdownx>=4.0.2'
      ],
      url='https://github.com/VSudheerKumar/dj_dynamic_templates',
      license='MIT',
      platforms=['any'],
      package_data={'dj_dynamic_templates': ['templates/**/*.html']}


      )
