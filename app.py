# main.py
import streamlit as st
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import time
import ta

# Configuration initiale
st.set_page_config(
    page_title="Analyseur Crypto Avancé",
    page_icon="📊",
    layout="wide"
)

# Importation de toutes les classes
from utils import get_valid_symbol, get_exchange  
from technical_analysis import TechnicalAnalysis, SignalGenerator
from portfolio_management import PortfolioManager
from interface import (LiveAnalysisPage, PortfolioPage, OpportunitiesPage,
                     HistoricalAnalysisPage, TopPerformancePage)
from guide import TradingGuide, Documentation

class CryptoAnalyzerApp:
    def __init__(self):
        # Initialisation des composants principaux
        self.session_state = SessionState()
        self.exchange = get_exchange()
        self.ta_analyzer = TechnicalAnalysis()
        self.portfolio_manager = PortfolioManager(self.exchange)
        
        # Initialisation des pages
        self.pages = {
            "Analyse en Direct": LiveAnalysisPage(
                self.exchange,
                self.ta_analyzer,
                self.portfolio_manager
            ),
            "Portefeuille": PortfolioPage(
                self.portfolio_manager
            ),
            "Top Performances": TopPerformancePage(
                self.exchange,
                self.ta_analyzer
            ),
            "Opportunités Court Terme": OpportunitiesPage(
                self.exchange,
                self.ta_analyzer
            ),
            "Analyse Historique": HistoricalAnalysisPage(
                self.exchange,
                self.ta_analyzer
            ),
            "Guide & Explications": TradingGuide()
        }

    def run(self):
        # Configuration du sidebar
        with st.sidebar:
            st.title("🚀 Crypto Analyzer")
            selected_page = st.selectbox(
                "Navigation",
                list(self.pages.keys())
            )
            
            # Informations générales dans le sidebar
            if st.session_state.portfolio['capital'] > 0:
                st.sidebar.markdown("---")
                st.sidebar.markdown("### 💰 Portfolio")
                st.sidebar.metric(
                    "Capital actuel",
                    f"{format_number(st.session_state.portfolio['current_capital'])} USDT",
                    f"{((st.session_state.portfolio['current_capital'] / st.session_state.portfolio['capital']) - 1) * 100:.2f}%"
                )

            # État du marché
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📊 État du Marché")
            try:
                btc_ticker = self.exchange.fetch_ticker("BTC/USDT")
                eth_ticker = self.exchange.fetch_ticker("ETH/USDT")
                
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    st.metric("BTC", f"{btc_ticker['last']:,.0f}", 
                             f"{btc_ticker['percentage']:.1f}%")
                with col2:
                    st.metric("ETH", f"{eth_ticker['last']:.0f}", 
                             f"{eth_ticker['percentage']:.1f}%")
            except:
                st.sidebar.error("Erreur de connexion au marché")

        # Rendu de la page sélectionnée
        try:
            self.pages[selected_page].render()
        except Exception as e:
            st.error(f"Erreur lors du chargement de la page: {str(e)}")

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center'>
            <p>Développé avec ❤️ | Données fournies par KuCoin</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Mise en place du try-except global
    try:
        # Configuration des styles CSS
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

        # Initialisation et lancement de l'application
        app = CryptoAnalyzerApp()
        app.run()

    except Exception as e:
        st.error(f"""
        ⚠️ Une erreur s'est produite lors du démarrage de l'application:
        {str(e)}
        
        Veuillez rafraîchir la page ou contacter le support si l'erreur persiste.
        """)

# Point d'entrée de l'application
if __name__ == "__main__":
    main()
