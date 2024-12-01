# setup.py
from setuptools import setup, find_packages

setup(
    name="crypto_analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'ta'
    ]
)