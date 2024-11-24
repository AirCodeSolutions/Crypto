# Dans utils.py ou config-and-utils.py

import streamlit as st
import ccxt

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
        # Ajout de vérification de base
        if not symbol:
            return None
            
        # Formatage du symbol
        symbol = symbol.upper().strip()
        
        # Chargement des marchés disponibles
        markets = exchange.load_markets()
        
        # Vérification des différents formats possibles
        possible_pairs = [
            f"{symbol}/USDT",
            f"{symbol}/USDT:USDT",
            f"{symbol}USDT"  # Certains exchanges utilisent ce format
        ]
        
        for pair in possible_pairs:
            if pair in markets:
                return pair
                
        return None
        
    except Exception as e:
        st.error(f"Erreur lors de la vérification du symbole: {str(e)}")
        return None

# Utilisation dans LiveAnalysisPage
class LiveAnalysisPage:
    def __init__(self, exchange, ta_analyzer, portfolio_manager):
        self.exchange = exchange
        self.ta = ta_analyzer
        self.portfolio = portfolio_manager
        
    def _manage_tracked_coins(self, symbol):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ajouter à la liste de suivi"):
                if symbol and symbol not in st.session_state.tracked_coins:
                    # Utilisation de get_valid_symbol comme fonction
                    valid_symbol = get_valid_symbol(self.exchange, symbol)
                    if valid_symbol:
                        st.session_state.tracked_coins.add(symbol)
                        st.success(f"{symbol} ajouté à la liste de suivi")
                    else:
                        st.error(f"{symbol} n'est pas une crypto valide")

        with col2:
            if st.button("Supprimer de la liste"):
                if symbol in st.session_state.tracked_coins:
                    st.session_state.tracked_coins.remove(symbol)
                    st.info(f"{symbol} retiré de la liste de suivi")

    def _analyze_and_display_coin(self, coin):
        try:
            # Vérification du symbole valide
            valid_symbol = get_valid_symbol(self.exchange, coin)
            if valid_symbol:
                # Récupération des données
                ticker = self.exchange.fetch_ticker(valid_symbol)
                df = calculate_timeframe_data(self.exchange, valid_symbol, '1h', 100)
                
                if df is not None:
                    # Analyse technique
                    analysis = self.ta.analyze_market_data(df, ticker['last'])
                    
                    # Affichage des résultats
                    self._display_coin_analysis(coin, analysis, df)
                    
        except Exception as e:
            st.error(f"Erreur pour {coin}: {str(e)}")
