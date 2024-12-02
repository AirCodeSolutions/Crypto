# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from services.exchange import ExchangeService
from interface import (
    TradingChart, 
    ChartConfig,
    AlertSystem,
    StyledButton,
    StatusIndicator
)

def setup_page_config():
    """Configure la page et les styles"""
    st.set_page_config(
        page_title="Crypto Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

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
        .stButton button {
            width: 100%;
            padding: 0.5rem;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    # Configuration initiale
    setup_page_config()
    st.markdown("# 📱 Crypto Analyzer")

    # Initialisation des services
    exchange = ExchangeService()
    alert_system = AlertSystem()

    # Sélection de la crypto
    crypto_options = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "SOL": "Solana",
        "BNB": "Binance Coin",
        "XRP": "Ripple"
    }
    
    selected_crypto = st.selectbox(
        "Sélectionner une crypto",
        options=list(crypto_options.keys()),
        format_func=lambda x: f"{x} - {crypto_options[x]}"
    )

    # Création du layout
    is_mobile = st.session_state.get('mobile_view', True)
    if is_mobile:
        chart_col = st.container()
        alerts_col = st.container()
    else:
        chart_col, alerts_col = st.columns([2, 1])

    # Affichage du graphique
    with chart_col:
        st.markdown(f"### {crypto_options[selected_crypto]} ({selected_crypto}/USDT)")
        try:
            # Récupération des données réelles
            ohlcv = exchange.get_ohlcv(selected_crypto)
            if ohlcv:
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)

                # Affichage du graphique
                chart_height = 300 if is_mobile else 400
                config = ChartConfig(height=chart_height)
                chart = TradingChart(config)
                chart.render(df, f"{selected_crypto}/USDT")
            else:
                st.warning("Aucune donnée disponible pour cette crypto")
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données: {str(e)}")

    # Section alertes et actions
    with alerts_col:
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
                try:
                    ticker = exchange.get_ticker(selected_crypto)
                    alert_system.add_notification(
                        f"Prix actuel {selected_crypto}",
                        "info",
                        {
                            "Prix": f"${ticker['last']:.2f}",
                            "Volume 24h": f"${ticker['quoteVolume']/1e6:.1f}M"
                        }
                    )
                except Exception as e:
                    alert_system.add_notification(
                        "Erreur de récupération des prix",
                        "error",
                        {"Erreur": str(e)}
                    )

        st.markdown("### 🔔 Notifications")
        alert_system.render()

if __name__ == "__main__":
    main()