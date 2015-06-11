from setuptools import setup, find_packages

setup(
  name = 'recast-dmhiggs-demo',
  version = '0.0.1',
  description = 'recast-dmhiggs-demo',
  url = 'http://github.com/recast-hep/recast-dmhiggs-demo',
  author = 'Lukas Heinrich',
  author_email = 'lukas.heinrich@cern.ch',
  packages = find_packages(),
  include_package_data = True,
  install_requires = [
    'Flask',
    'celery',
    'requests',
    'recast-api',
    'recast-backend',
    'yoda',
    'redis',
    'pyyaml'
  ],
  dependency_links = [      
    'https://github.com/recast-hep/recast-api/tarball/master#egg=recast-api-0.0.1',
    'https://github.com/recast-hep/recast-backend/tarball/master#egg=recast-backend-0.0.1',
  ]
)
