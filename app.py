# app.py
import streamlit as st
from interface import TimeSelector, TradingChart, ChartConfig, AlertSystem
from services.exchange import ExchangeService
from core.analysis import MarketAnalyzer

def main():
    """Application principale avec les composants réintégrés"""
    st.title("Crypto Analyzer Pro")
    
    # Test de chaque composant un par un
    # 1. TimeSelector
    selected_timeframe = TimeSelector.render("timeframe")
    st.write(f"Période sélectionnée : {selected_timeframe}")
    
    # 2. Chart (si nous avons des données)
    try:
        exchange = ExchangeService()
        df = exchange.get_ohlcv("BTC", selected_timeframe)
        
        config = ChartConfig(height=400)
        chart = TradingChart(config)
        chart.render(df, "BTC/USDT")
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")

if __name__ == "__main__":
    main()