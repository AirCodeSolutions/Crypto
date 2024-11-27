# app.py
import streamlit as st
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import time
import ta

# Configuration initiale
st.set_page_config(
    page_title="Analyseur Crypto par AirCodeSolutions",
    page_icon="📊",
    layout="wide"
)

from utils import SessionState, format_number, get_exchange, get_valid_symbol  
from technical_analysis import TechnicalAnalysis, SignalGenerator
from portfolio_management import PortfolioManager
from interface import (LiveAnalysisPage, PortfolioPage, OpportunitiesPage,
                     HistoricalAnalysisPage, TopPerformancePage, MicroTradingPage, CryptoAnalyzerApp)

def main():
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
