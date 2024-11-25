# utils.py
import streamlit as st
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

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
                'capital': 0,
                'current_capital': 0
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

@st.cache_resource
def get_exchange():
    """
    Initialise et retourne l'objet exchange
    """
    return ccxt.kucoin({
        'adjustForTimeDifference': True,
        'timeout': 30000,
    })

def get_valid_symbol(_exchange, symbol):
    """
    Vérifie et formate le symbole pour l'exchange
    """
    try:
        if not symbol:
            return None
            
        symbol = symbol.upper().strip()
        markets = _exchange.load_markets()
        
        possible_pairs = [
            f"{symbol}/USDT",
            f"{symbol}/USDT:USDT",
            f"{symbol}USDT"
        ]
        
        for pair in possible_pairs:
            if pair in markets:
                return pair
                
        return None
        
    except Exception as e:
        st.error(f"Erreur lors de la vérification du symbole: {str(e)}")
        return None
    
@st.cache_data(ttl=300)  # Cache de 5 minutes
def calculate_timeframe_data(_exchange, symbol, timeframe='1h', limit=100):
    """
    Récupère et calcule les données pour un timeframe donné
    Note: Le préfixe _ sur _exchange empêche Streamlit de hasher cet argument
    """
    try:
        ohlcv = _exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Erreur lors du calcul des données {timeframe}: {str(e)}")
        return None

# Dans utils.py
def format_number(number, decimals=8):
    """
    Formate les nombres pour l'affichage
    """
    if number is None:
        return "N/A"
    try:
        if number >= 1e6:
            return f"{number/1e6:.2f}M"
        elif number >= 1e3:
            return f"{number/1e3:.2f}K"
        else:
            return f"{number:.{decimals}f}"
    except Exception as e:
        return str(number)
    
def time_to_str(timestamp):
    """
    Convertit un timestamp en chaîne de caractères formatée
    """
    if isinstance(timestamp, (int, float)):
        timestamp = datetime.fromtimestamp(timestamp/1000)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

@st.cache_data(ttl=60)  # Cache de 1 minute
def get_market_data(_exchange, symbols):
    """
    Récupère les données de marché pour plusieurs symboles
    """
    data = {}
    for symbol in symbols:
        try:
            ticker = _exchange.fetch_ticker(f"{symbol}/USDT")
            data[symbol] = {
                'price': ticker['last'],
                'volume': ticker['quoteVolume'],
                'change': ticker['percentage']
            }
        except Exception as e:
            st.error(f"Erreur pour {symbol}: {str(e)}")
    return data

def display_error_message(error):
    """
    Affiche un message d'erreur formaté
    """
    st.error(f"""
    ⚠️ Une erreur s'est produite:
    {str(error)}
    
    Veuillez réessayer ou contacter le support si l'erreur persiste.
    """)

def load_css():
    """
    Charge les styles CSS personnalisés
    """
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
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        .stAlert {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

def setup_page():
    """
    Configuration initiale de la page
    """
    st.set_page_config(
        page_title="Analyseur Crypto Avancé",
        page_icon="📊",
        layout="wide"
    )
    load_css()

# Fonction utilitaire pour calculer les variations de prix
def calculate_price_change(current, previous):
    """
    Calcule la variation de prix en pourcentage
    """
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def validate_number_input(value, min_value=None, max_value=None):
    """
    Valide une entrée numérique
    """
    try:
        num = float(value)
        if min_value is not None and num < min_value:
            return False, f"La valeur doit être supérieure à {min_value}"
        if max_value is not None and num > max_value:
            return False, f"La valeur doit être inférieure à {max_value}"
        return True, num
    except ValueError:
        return False, "Veuillez entrer un nombre valide"
