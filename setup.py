# setup.py
from setuptools import setup, find_packages

setup(
    name="crypto_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'streamlit>=1.31.0',
        'pandas>=2.2.0',
        'numpy>=1.26.3',
        'ccxt>=4.1.87',
        'ta>=0.10.2',
        'plotly>=5.10.0',
        'pyairtable>=2.2.1',
        'scikit-learn>=1.4.0'
    ],
    author="AirCodeSolutions",
    description="Un analyseur de cryptomonnaies en temps réel",
    python_requires='>=3.8'
)