from setuptools import setup, find_packages


setup(name='dolphin',
      version='0.0.1',
      entry_points={
          'console_scripts': ['dolphind = dolphin.manager:serve_forever']
      },
      packages=find_packages()
)
