# app.py
import streamlit as st
import ccxt
import os 
from datetime import datetime
from utils import SessionState, format_number, get_exchange
from technical_analysis import TechnicalAnalysis
from portfolio_management import PortfolioManager
from interface import (LiveAnalysisPage, PortfolioPage, OpportunitiesPage, 
                      HistoricalAnalysisPage, TopPerformancePage, MicroTradingPage, GuidePage)
from ai_predictor import AIPredictor

class CryptoAnalyzerApp:
    def __init__(self):
        self.exchange = get_exchange()
        self.ta = TechnicalAnalysis()
        self.portfolio = PortfolioManager(self.exchange)
        self.ai = AIPredictor()
        try:
            self.version = st.secrets["app_version"]
        except:
            self.version = "local"
        self.pages = {
            "Analyse en Direct": LiveAnalysisPage(self.exchange, self.ta, self.portfolio),
            "Trading Micro-Budget": MicroTradingPage(self.exchange, self.portfolio, self.ai),
            "Portefeuille": PortfolioPage(self.portfolio),
            "Top Performances": TopPerformancePage(self.exchange, self.ta),
            "Opportunités Court Terme": OpportunitiesPage(self.exchange, self.ta),
            "Analyse Historique": HistoricalAnalysisPage(self.exchange, self.ta),
            "Guide & Explications": GuidePage()
        }

    def run(self):
        st.sidebar.title("Navigation")
        # Affichage de la version dans la sidebar
        st.sidebar.markdown(f"**Version**: {self.version}")
        page_name = st.sidebar.selectbox("Choisir une page", list(self.pages.keys()))
        
        if st.session_state.portfolio['capital'] > 0:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 💰 Portfolio")
            st.sidebar.metric(
                "Capital actuel",
                f"{format_number(st.session_state.portfolio['current_capital'])} USDT",
                f"{((st.session_state.portfolio['current_capital'] / st.session_state.portfolio['capital']) - 1) * 100:.2f}%"
            )
            
        try:
            self.pages[page_name].render()
        except Exception as e:
            st.error(f"Erreur lors du chargement de la page: {str(e)}")

def main():
    try:
        # Configuration des styles CSS
        st.set_page_config(
            page_title="Analyseur Crypto par AirCodeSolutions",
            page_icon="📊",
            layout="wide"
        )
        # Ajoutons un indicateur de branche
        import os
        branch = os.environ.get('BRANCH', 'unknown')
        st.sidebar.markdown(f"Version: {branch}")
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
            </style>
        """, unsafe_allow_html=True)

        # Initialisation de l'état de session
        session_state = SessionState()
        
        # Initialisation et lancement de l'application
        app = CryptoAnalyzerApp()
        app.run()

    except Exception as e:
        st.error(f"""
        ⚠️ Une erreur s'est produite lors du démarrage de l'application:
        {str(e)}
        
        Veuillez rafraîchir la page ou contacter le support si l'erreur persiste.
        """)

if __name__ == "__main__":
    main()
