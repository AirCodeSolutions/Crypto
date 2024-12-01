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
    # Configuration de la page avec des paramètres adaptés au mobile
    st.set_page_config(
        page_title="Crypto Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"  # Cache la barre latérale sur mobile
    )

    # Styles CSS personnalisés pour l'affichage mobile
    st.markdown("""
        <style>
        /* Réduction de la taille des titres sur mobile */
        @media (max-width: 640px) {
            .main h1 {
                font-size: 1.5rem !important;
            }
            .main h2 {
                font-size: 1.2rem !important;
            }
            .main h3 {
                font-size: 1rem !important;
            }
            /* Ajustement des marges */
            .element-container {
                padding: 0.5rem 0 !important;
            }
            /* Amélioration de la lisibilité des graphiques */
            .plotly-graph-div {
                min-height: 300px !important;
            }
        }
        /* Styles généraux pour améliorer la lisibilité */
        .stButton button {
            width: 100%;
            padding: 0.5rem;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Titre principal plus compact
    st.markdown("# 📱 Crypto Analyzer")

    # Utilisation de conteneurs pour une meilleure organisation
    with st.container():
        # Sur mobile, les colonnes se transformeront en lignes
        if st.session_state.get('mobile_view', True):
            main_chart_container = st
            alerts_container = st
        else:
            main_chart_container, alerts_container = st.columns([2, 1])

        with main_chart_container:
            st.markdown("### 📊 Analyse Technique")
            df = create_sample_data()
            
            # Configuration adaptative du graphique
            chart_height = 300 if st.session_state.get('mobile_view', True) else 400
            config = ChartConfig(height=chart_height)
            chart = TradingChart(config)
            chart.render(df, "BTC/USDT")

        with alerts_container:
            alert_system = AlertSystem()
            
            # Boutons plus compacts sur mobile
            col1, col2 = st.columns(2)
            with col1:
                if StyledButton.render("Analyser", "analyze_btn", "primary"):
                    StatusIndicator.render("loading", "Analyse...")
                    alert_system.add_notification(
                        "Analyse terminée",
                        "success",
                        {"Score": "0.85"}
                    )
            
            with col2:
                if StyledButton.render("Alertes", "alert_btn", "warning"):
                    alert_system.add_notification(
                        "Prix cible atteint",
                        "warning",
                        {"Prix": "50K"}
                    )

            # Section alertes plus compacte
            st.markdown("### 🔔 Notifications")
            alert_system.render()

if __name__ == "__main__":
    main()