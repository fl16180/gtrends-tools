from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()


SHORT_DESCRIPTION = 'Interface for retrieving data from Google Health Trends API'
VERSION = '0.1'
URL = 'https://github.com/fl16180/gtrends-tools'


setup(
    name='gtrends-tools',
    description=SHORT_DESCRIPTION,
    version=VERSION,
    url=URL,

    author='Fred Lu',
    author_email='fredlu.flac@gmail.com',

    long_description=readme(),

    license='MIT',
    packages=['healthtrends'],
    install_requires=['google-api-python-client'],

    scripts=['bin/tmp.sh'],
)
