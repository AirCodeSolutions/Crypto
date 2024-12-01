# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Imports des composants
from interface.components.chart_components import TradingChart, ChartConfig
from interface.components.alerts import AlertSystem
from interface.components.widgets import StyledButton, StatusIndicator

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
    st.set_page_config(page_title="Crypto Analyzer - Test", layout="wide")
    st.title("🚀 Test de l'Interface Crypto")

    # Initialisation des composants
    alert_system = AlertSystem()
    
    # Création des colonnes principales
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Section Graphique
        st.header("📊 Analyse Technique")
        df = create_sample_data()
        config = ChartConfig(height=400)
        chart = TradingChart(config)
        chart.render(df, "BTC/USDT")
        
    with col2:
        # Section Alertes et Actions
        st.header("🔔 Actions & Alertes")
        
        # Boutons de test
        if StyledButton.render("Analyser", "analyze_btn", "primary"):
            StatusIndicator.render("loading", "Analyse en cours...")
            alert_system.add_notification(
                "Analyse technique terminée",
                "success",
                {"Score": "0.85", "Signal": "Achat"}
            )
        
        if StyledButton.render("Simuler Alerte", "alert_btn", "warning"):
            alert_system.add_notification(
                "Niveau de prix atteint !",
                "warning",
                {"Prix": "$50,000", "Type": "Résistance"}
            )
            
        # Affichage des alertes
        st.markdown("### Dernières Notifications")
        alert_system.render()

if __name__ == "__main__":
    main()