# pages.py
import streamlit as st
from datetime import datetime
import pandas as pd

class LiveAnalysisPage:
    def __init__(self, exchange, ta_analyzer, portfolio_manager):
        self.exchange = exchange
        self.ta = ta_analyzer
        self.portfolio = portfolio_manager
        
    def render(self):
        st.title("📈 Analyse en Direct")
        
        # Input pour ajouter une crypto
        col1, col2 = st.columns([3, 1])
        with col1:
            symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC, ETH)", "").upper()

        # Gestion des cryptos suivies
        self._manage_tracked_coins(symbol)
        
        # Affichage des analyses
        if st.session_state.tracked_coins:
            self._display_tracked_coins()

    def _manage_tracked_coins(self, symbol):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ajouter à la liste de suivi"):
                if symbol and symbol not in st.session_state.tracked_coins:
                    if self.exchange.get_valid_symbol(symbol):
                        st.session_state.tracked_coins.add(symbol)
                        st.success(f"{symbol} ajouté à la liste de suivi")
                    else:
                        st.error(f"{symbol} n'est pas une crypto valide")

        with col2:
            if st.button("Supprimer de la liste"):
                if symbol in st.session_state.tracked_coins:
                    st.session_state.tracked_coins.remove(symbol)
                    st.info(f"{symbol} retiré de la liste de suivi")

    def _display_tracked_coins(self):
        st.subheader("Cryptos suivies")
        for coin in st.session_state.tracked_coins:
            self._analyze_and_display_coin(coin)

    def _analyze_and_display_coin(self, coin):
        try:
            # Récupération des données
            ticker = self.exchange.fetch_ticker(f"{coin}/USDT")
            df = self.exchange.calculate_timeframe_data(f"{coin}/USDT", '1h', 100)
            
            if df is not None:
                # Analyse technique
                analysis = self.ta.analyze_market_data(df, ticker['last'])
                
                # Affichage des résultats
                self._display_coin_analysis(coin, analysis, df)
                
        except Exception as e:
            st.error(f"Erreur pour {coin}: {str(e)}")

class PortfolioPage:
    def __init__(self, portfolio_manager):
        self.portfolio = portfolio_manager

    def render(self):
        st.title("💼 Gestion du Portefeuille")
        
        # Configuration du capital initial
        self._manage_capital()
        
        # Formulaire d'ajout de position
        self._add_position_form()
        
        # Affichage des positions actuelles
        self._display_current_positions()
        
        # Historique et statistiques
        self._display_history_and_stats()

    def _manage_capital(self):
        if st.session_state.portfolio['capital'] == 0:
            st.session_state.portfolio['capital'] = st.number_input(
                "Capital initial (USDT)",
                min_value=0.0,
                value=1000.0,
                step=100.0
            )
            st.session_state.portfolio['current_capital'] = st.session_state.portfolio['capital']

    def _add_position_form(self):
        with st.expander("➕ Ajouter une nouvelle position"):
            col1, col2 = st.columns(2)
            with col1:
                new_symbol = st.text_input("Symbole (ex: BTC)", "").upper()
                amount = st.number_input("Montant (USDT)", min_value=0.0, value=100.0)
                entry_price = st.number_input("Prix d'entrée", min_value=0.0, value=0.0)
            with col2:
                stop_loss = st.number_input("Stop Loss", min_value=0.0, value=0.0)
                target_1 = st.number_input("Target 1", min_value=0.0, value=0.0)
                target_2 = st.number_input("Target 2", min_value=0.0, value=0.0)
            
            if st.button("Ajouter la position"):
                self._handle_new_position(new_symbol, amount, entry_price, stop_loss, target_1, target_2)

class OpportunitiesPage:
    def __init__(self, exchange, ta_analyzer):
        self.exchange = exchange
        self.ta = ta_analyzer

    def render(self):
        st.title("🎯 Opportunités Court Terme")
        
        # Filtres
        self._display_filters()
        
        # Recherche d'opportunités
        if st.button("Rechercher"):
            self._search_opportunities()

    def _display_filters(self):
        col1, col2, col3 = st.columns(3)
        with col1:
            min_var = st.number_input("Variation minimum (%)", value=1.0)
        with col2:
            min_vol = st.number_input("Volume minimum (USDT)", value=100000.0)
        with col3:
            min_score = st.slider("Score minimum", 0.0, 1.0, 0.6)
        return min_var, min_vol, min_score

    def _search_opportunities(self):
        # [Code de recherche d'opportunités]
        pass

class HistoricalAnalysisPage:
    def __init__(self, exchange, ta_analyzer):
        self.exchange = exchange
        self.ta = ta_analyzer

    def render(self):
        st.title("📊 Analyse Historique")
        # [Code de l'analyse historique]
        pass

class TopPerformancePage:
    def __init__(self, exchange, ta_analyzer):
        self.exchange = exchange
        self.ta = ta_analyzer

    def render(self):
        st.title("🏆 Top Performances")
        # [Code des top performances]
        pass

class GuidePage:
    def render(self):
        st.title("📚 Guide de Trading Crypto Avancé")
        # [Code du guide]
        pass

# Main App
class CryptoAnalyzerApp:
    def __init__(self):
        self.exchange = get_exchange()
        self.ta = TechnicalAnalysis()
        self.portfolio = PortfolioManager(self.exchange)
        
        self.pages = {
            "Analyse en Direct": LiveAnalysisPage(self.exchange, self.ta, self.portfolio),
            "Portefeuille": PortfolioPage(self.portfolio),
            "Top Performances": TopPerformancePage(self.exchange, self.ta),
            "Opportunités Court Terme": OpportunitiesPage(self.exchange, self.ta),
            "Analyse Historique": HistoricalAnalysisPage(self.exchange, self.ta),
            "Guide & Explications": GuidePage()
        }

    def run(self):
        st.sidebar.title("Navigation")
        page_name = st.sidebar.selectbox("Choisir une page", list(self.pages.keys()))
        
        # Rendu de la page sélectionnée
        self.pages[page_name].render()
