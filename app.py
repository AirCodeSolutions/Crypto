# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
from interface import TimeSelector, TradingChart, ChartConfig, AlertSystem
from services.exchange import ExchangeService
from core.analysis import MarketAnalyzer

# Configuration du logging pour un meilleur suivi des erreurs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAnalyzerApp:
    """Application principale d'analyse de cryptomonnaies en temps réel"""
    
    def __init__(self):
        """
        Initialise l'application avec tous les services nécessaires.
        Configure également l'état de session pour la persistance des données.
        """
        try:
            self.exchange = ExchangeService()
            self.analyzer = MarketAnalyzer(self.exchange)
            self.alert_system = AlertSystem()
            
            # État de session pour le suivi des analyses
            if 'analyzed_symbols' not in st.session_state:
                st.session_state.analyzed_symbols = set()
            
            logger.info("Application initialisée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur d'initialisation: {e}")
            raise

    def setup_page(self):
        """Configure la mise en page et les styles de l'application"""
        st.set_page_config(
            page_title="Crypto Analyzer Pro",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Styles CSS pour l'interface
        st.markdown("""
            <style>
            .main h1 { font-size: 1.2rem !important; }
            .crypto-metrics { 
                background-color: #f0f2f6; 
                padding: 1rem; 
                border-radius: 0.5rem; 
                margin: 1rem 0;
            }
            .signal-strong-buy { color: #00ff00; font-weight: bold; }
            .signal-buy { color: #008000; }
            .signal-neutral { color: #808080; }
            .signal-sell { color: #ff0000; }
            </style>
        """, unsafe_allow_html=True)

    def main(self):
        """
        Point d'entrée principal de l'application.
        Gère l'affichage de tous les composants et leur interaction.
        """
        try:
            self.setup_page()
            st.title("Crypto Analyzer Pro")
            
            # Section de recherche et sélection de crypto
            search_term = st.text_input("🔍 Rechercher une crypto", "").upper()
            available_symbols = self.exchange.get_available_symbols()
            
            # Filtrage des cryptos selon la recherche
            filtered_symbols = [
                symbol for symbol in available_symbols 
                if search_term in symbol
            ] if search_term else available_symbols[:30]

            if not filtered_symbols:
                st.warning("Aucune crypto trouvée pour votre recherche.")
                return

            # Interface principale divisée en colonnes
            chart_col, analysis_col = st.columns([2, 1])
            
            with chart_col:
                # Sélection de la crypto et de la période
                selected_symbol = st.selectbox(
                    "Sélectionner une crypto",
                    filtered_symbols,
                    format_func=self._format_symbol_display
                )
                
                # Sélecteur de période et affichage du graphique
                timeframe = TimeSelector.render("timeframe_selector")
                self._display_chart(selected_symbol, timeframe)

            with analysis_col:
                self._display_analysis(selected_symbol)

        except Exception as e:
            logger.error(f"Erreur dans l'application: {e}", exc_info=True)
            st.error(f"Une erreur est survenue: {str(e)}")
            if st.button("🔄 Rafraîchir"):
                st.rerun()

    def _format_symbol_display(self, symbol: str) -> str:
        """Formate l'affichage d'un symbole avec son prix actuel"""
        try:
            ticker = self.exchange.get_ticker(symbol)
            return f"{symbol} - ${ticker['last']:,.2f} USDT"
        except Exception as e:
            logger.error(f"Erreur format symbole: {e}")
            return symbol

    def _display_chart(self, symbol: str, timeframe: str):
        """Affiche le graphique pour un symbole donné"""
        try:
            df = self.exchange.get_ohlcv(symbol, timeframe)
            config = ChartConfig(height=400, show_volume=True)
            chart = TradingChart(config)
            chart.render(df, f"{symbol}/USDT")
        except Exception as e:
            logger.error(f"Erreur affichage graphique: {e}")
            st.error("Impossible d'afficher le graphique")

    def _display_analysis(self, symbol: str):
        """Affiche l'analyse complète pour un symbole"""
        try:
            analysis = self.analyzer.analyze_symbol(symbol)
            if analysis:
                # Métriques principales
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Prix", f"${analysis['price']:,.2f}")
                with cols[1]:
                    st.metric("RSI", f"{analysis['rsi']:.1f}")
                
                # Signal de trading
                st.markdown(f"Signal: {analysis['signal']}")
                
                # Système d'alertes
                self.alert_system.render()
        except Exception as e:
            logger.error(f"Erreur affichage analyse: {e}")
            st.error("Impossible d'afficher l'analyse")

if __name__ == "__main__":
    app = CryptoAnalyzerApp()
    app.main()