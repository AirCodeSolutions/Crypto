# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from interface import (
    TradingChart, 
    ChartConfig,
    AlertSystem,
    StyledButton,
    StatusIndicator
)

def create_sample_data():
    """Crée des données de test pour le graphique"""
    dates = pd.date_range(start='2024-01-01', end='2024-02-01', freq='1H')
    df = pd.DataFrame(index=dates)
    df['close'] = 100 + np.random.randn(len(df)).cumsum()
    df['open'] = df['close'] + np.random.randn(len(df))
    df['high'] = np.maximum(df['open'], df['close']) + np.random.rand(len(df))
    df['low'] = np.minimum(df['open'], df['close']) - np.random.rand(len(df))
    df['volume'] = np.random.rand(len(df)) * 1000000
    return df
def main():
    # Configuration de la page
    st.set_page_config(
        page_title="Crypto Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Styles CSS pour optimisation mobile
    st.markdown("""
        <style>
        .main h1 {
            font-size: 1.2rem !important;
            margin-bottom: 0.5rem !important;
        }
        .main h3 {
            font-size: 0.9rem !important;
            color: #555;
            margin-bottom: 0.3rem !important;
        }
        @media (max-width: 640px) {
            .element-container {
                padding: 0.5rem 0 !important;
            }
            .plotly-graph-div {
                min-height: 300px !important;
            }
        }
        .stButton button {
            width: 100%;
            padding: 0.5rem;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("# 📱 Crypto Analyzer")

    # Définition des cryptos disponibles
    crypto_options = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "SOL": "Solana",
        "BNB": "Binance Coin",
        "XRP": "Ripple"
    }
    
    # Sélecteur de crypto
    selected_crypto = st.selectbox(
        "Sélectionner une crypto",
        options=list(crypto_options.keys()),
        format_func=lambda x: f"{x} - {crypto_options[x]}"
    )

    # Création des colonnes principales
    if st.session_state.get('mobile_view', True):
        # Vue mobile : affichage en colonnes empilées
        chart_container = st.container()
        alerts_container = st.container()
    else:
        # Vue desktop : affichage en colonnes côte à côte
        chart_container, alerts_container = st.columns([2, 1])

    # Fonction pour générer les données selon la crypto
    def get_crypto_data(symbol: str) -> pd.DataFrame:
        df = create_sample_data()
        
        multipliers = {
            "BTC": 40000,
            "ETH": 2000,
            "SOL": 100,
            "BNB": 300,
            "XRP": 1
        }
        
        multiplier = multipliers.get(symbol, 1)
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col] * multiplier
            
        return df

    # Section graphique
    with chart_container:
        st.markdown(f"### {crypto_options[selected_crypto]} ({selected_crypto}/USDT)")
        df = get_crypto_data(selected_crypto)
        chart_height = 300 if st.session_state.get('mobile_view', True) else 400
        config = ChartConfig(height=chart_height)
        chart = TradingChart(config)
        chart.render(df, f"{selected_crypto}/USDT")

    # Section alertes
    with alerts_container:
        alert_system = AlertSystem()
        
        col1, col2 = st.columns(2)
        with col1:
            if StyledButton.render("Analyser", "analyze_btn", "primary"):
                StatusIndicator.render("loading", "Analyse...")
                alert_system.add_notification(
                    f"Analyse {selected_crypto} terminée",
                    "success",
                    {"Score": "0.85"}
                )
        
        with col2:
            if StyledButton.render("Alertes", "alert_btn", "warning"):
                alert_system.add_notification(
                    f"Prix cible {selected_crypto} atteint",
                    "warning",
                    {"Prix": f"{selected_crypto} 50K"}
                )

        st.markdown("### 🔔 Notifications")
        alert_system.render()

if __name__ == "__main__":
    main()