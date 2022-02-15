from setuptools import setup

setup(
    name='powerbi_connector',
    version='1.0',
    description='Wrapper for Power BI API and Power BI Admin API',
    author='Guilherme Campiani',
    author_email='guilherme.campiani@gmail.com',
    packages=['powerbi_connector'],
    install_requires=['msal', 'requests']
)
