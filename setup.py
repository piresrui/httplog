from setuptools import setup

setup(
    name='httplog',
    version='0.0.1',
    packages=['httplog', 'httplogcli'],
    entry_points={
        'console_scripts': [
            'httplog = httplogcli.__main__:main'
        ]
    })
