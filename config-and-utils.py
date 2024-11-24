# utils.py
import streamlit as st
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import ta

# Configuration de la page
def setup_page():
    st.set_page_config(
        page_title="Analyseur Crypto Avancé",
        page_icon="📊",
        layout="wide"
    )

# Initialisation de l'exchange
@st.cache_resource
def get_exchange():
    return ccxt.kucoin({
        'adjustForTimeDifference': True,
        'timeout': 30000,
    })

def get_valid_symbol(exchange, symbol):
    """
    Vérifie et formate le symbole pour l'exchange
    """
    try:
        markets = exchange.load_markets()
        if f"{symbol}/USDT" in markets:
            return f"{symbol}/USDT"
        elif f"{symbol}/USDT:USDT" in markets:
            return f"{symbol}/USDT:USDT"
        return None
    except Exception as e:
        st.error(f"Erreur lors de la vérification du symbol: {str(e)}")
        return None

def format_number(number, decimals=8):
    """
    Formate les nombres pour l'affichage
    """
    if number >= 1e6:
        return f"{number/1e6:.2f}M"
    elif number >= 1e3:
        return f"{number/1e3:.2f}K"
    else:
        return f"{number:.{decimals}f}"

def time_to_str(timestamp):
    """
    Convertit un timestamp en chaîne de caractères formatée
    """
    if isinstance(timestamp, (int, float)):
        timestamp = datetime.fromtimestamp(timestamp/1000)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def calculate_timeframe_data(exchange, symbol, timeframe='1h', limit=100):
    """
    Récupère et calcule les données pour un timeframe donné
    """
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Erreur lors du calcul des données {timeframe}: {str(e)}")
        return None

def display_error_message(error):
    """
    Affiche un message d'erreur formaté
    """
    st.error(f"""
    ⚠️ Une erreur s'est produite:
    {str(error)}
    
    Veuillez réessayer ou contacter le support si l'erreur persiste.
    """)

class SessionState:
    """
    Gestion de l'état de la session
    """
    def __init__(self):
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            self.initialize_session_state()

    def initialize_session_state(self):
        """
        Initialise les variables de session
        """
        default_states = {
            'tracked_coins': set(),
            'portfolio': {
                'positions': {},
                'history': [],
                'capital': 0
            },
            'settings': {
                'min_volume': 100000,
                'max_price': 20,
                'risk_per_trade': 0.01
            }
        }
        
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get(key, default=None):
        """
        Récupère une valeur de la session
        """
        return st.session_state.get(key, default)

    @staticmethod
    def set(key, value):
        """
        Définit une valeur dans la session
        """
        st.session_state[key] = value

# Configuration des styles CSS personnalisés
def load_css():
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        .trade-card {
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .profit {
            color: green;
        }
        .loss {
            color: red;
        }
        </style>
    """, unsafe_allow_html=True)
