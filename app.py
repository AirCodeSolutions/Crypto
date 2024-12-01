# app.py
import streamlit as st
from interface.components.alerts import AlertSystem
from interface.components.chart_components import TradingChart, ChartConfig
from interface.components.filter_section import FilterSection
from interface.components.trade_card import TradeCard, TradeCardData
from interface.components.widgets import StyledButton, StatusIndicator, TimeSelector, FormattedInput
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_data():
    """
    Crée des données factices pour tester les composants.
    Cette fonction génère un DataFrame simulant des données de trading.
    """
    dates = pd.date_range(start='2024-01-01', end='2024-02-01', freq='1H')
    df = pd.DataFrame(index=dates)
    
    # Génération de prix simulés
    df['close'] = 100 + np.random.randn(len(df)).cumsum()
    df['open'] = df['close'] + np.random.randn(len(df))
    df['high'] = np.maximum(df['open'], df['close']) + np.random.rand(len(df))
    df['low'] = np.minimum(df['open'], df['close']) - np.random.rand(len(df))
    df['volume'] = np.random.rand(len(df)) * 1000000
    
    return df

def main():
    """
    Point d'entrée principal de l'application.
    Configure la page et gère la navigation entre les différentes sections.
    """
    st.set_page_config(
        page_title="Test des Composants Crypto",
        page_icon="📊",
        layout="wide"
    )

    st.title("🧪 Page de Test des Composants")

    # Création des données de test
    df = create_sample_data()
    
    # Section 1: Test des Widgets de Base
    st.header("1. Test des Widgets de Base")
    col1, col2 = st.columns(2)
    
    with col1:
        StyledButton.render("Bouton Principal", "main_btn", "primary")
        StyledButton.render("Bouton Attention", "warn_btn", "warning")
        StyledButton.render("Bouton Danger", "danger_btn", "danger")
    
    with col2:
        StatusIndicator.render("loading", "Chargement en cours...")
        StatusIndicator.render("success", "Opération réussie")
        StatusIndicator.render("error", "Erreur détectée")

    # Section 2: Test des Entrées Formatées
    st.header("2. Test des Entrées Formatées")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        price = FormattedInput.price_input("Prix d'entrée", "test_price")
    with col2:
        percent = FormattedInput.percentage_input("Stop Loss (%)", "test_percent")
    with col3:
        amount = FormattedInput.amount_input("Montant", "test_amount")

    # Section 3: Test du Graphique
    st.header("3. Test du Graphique")
    
    period = TimeSelector.render("chart_period")
    chart = TradingChart(ChartConfig(height=500))
    chart.render(df, "BTC/USDT", show_signals=True)

    # Section 4: Test des Filtres
    st.header("4. Test des Filtres")
    filter_section = FilterSection()
    filters = filter_section.render()
    
    # Section 5: Test des Alertes
    st.header("5. Test des Alertes")
    alert_system = AlertSystem()
    
    if st.button("Ajouter une alerte de test"):
        alert_system.add_notification(
            "Test de notification",
            "success",
            {"Prix": "$50,000", "Volume": "$1.2M"}
        )
    
    alert_system.render()

    # Section 6: Test de la Carte de Trading
    st.header("6. Test de la Carte de Trading")
    trade_data = TradeCardData(
        symbol="BTC/USDT",
        price=50000.0,
        score=0.85,
        volume=1200000.0,
        change_24h=2.5,
        stop_loss=49000.0,
        target_1=51000.0,
        target_2=52000.0,
        reasons=["RSI en zone optimale", "Volume croissant", "Tendance haussière"]
    )
    
    trade_card = TradeCard(trade_data)
    trade_card.render()

if __name__ == "__main__":
    main()