# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from services.exchange import ExchangeService
from core.analysis import MarketAnalyzer
from interface import (
    TradingChart, 
    ChartConfig,
    AlertSystem,
    StyledButton,
    StatusIndicator,
    TimeSelector
)

class CryptoAnalyzerApp:
    """
    Application principale d'analyse de cryptomonnaies.
    Intègre les données réelles avec une interface utilisateur interactive.
    """
    
    def __init__(self):
        """Initialise les services et composants nécessaires"""
        self.exchange = ExchangeService()
        self.analyzer = MarketAnalyzer(self.exchange)
        self.alert_system = AlertSystem()
        
        # Initialisation de l'état de session
        if 'analyzed_symbols' not in st.session_state:
            st.session_state.analyzed_symbols = set()

    def setup_page(self):
        """Configure la page et les styles"""
        st.set_page_config(
            page_title="Crypto Analyzer Pro",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Styles pour optimisation mobile et desktop
        st.markdown("""
            <style>
            .main h1 { font-size: 1.2rem !important; }
            .crypto-metrics { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; }
            .signal-strong-buy { color: #00ff00; font-weight: bold; }
            .signal-buy { color: #008000; }
            .signal-neutral { color: #808080; }
            .signal-sell { color: #ff0000; }
            </style>
        """, unsafe_allow_html=True)

    def render_market_overview(self, symbol: str):
        """Affiche la vue d'ensemble du marché pour un symbole"""
        try:
            # Récupération et analyse des données
            analysis = self.analyzer.analyze_symbol(symbol)
            
            # Affichage des métriques principales
            cols = st.columns(4)
            with cols[0]:
                st.metric("Prix", f"${analysis['price']:,.2f}", 
                         f"{analysis['change_24h']:+.2f}%")
            with cols[1]:
                st.metric("RSI", f"{analysis['rsi']:.1f}")
            with cols[2]:
                st.metric("Volume 24h", f"${analysis['volume_24h']/1e6:.1f}M")
            with cols[3]:
                signal_color = {
                    "STRONG_BUY": "signal-strong-buy",
                    "BUY": "signal-buy",
                    "NEUTRAL": "signal-neutral",
                    "SELL": "signal-sell"
                }
                st.markdown(f"<div class='{signal_color[analysis['signal']]}'>{analysis['signal']}</div>",
                          unsafe_allow_html=True)
            
            # Ajout à l'historique des analyses
            st.session_state.analyzed_symbols.add(symbol)
            
            return analysis
            
        except Exception as e:
            st.error(f"Erreur lors de l'analyse de {symbol}: {str(e)}")
            return None

    def render_chart_section(self, symbol: str, timeframe: str = '1h'):
        """Affiche la section graphique avec les données réelles"""
        try:
            # Récupération des données OHLCV
            df = self.exchange.get_ohlcv(symbol, timeframe)
            
            # Configuration et affichage du graphique
            config = ChartConfig(
                height=400,
                show_volume=True,
                show_indicators=True
            )
            chart = TradingChart(config)
            chart.render(df, f"{symbol}/USDT")
            
            return df
            
        except Exception as e:
            st.error(f"Erreur lors du chargement du graphique: {str(e)}")
            return None

    def render_analysis_controls(self, symbol: str):
        """Affiche les contrôles d'analyse"""
        col1, col2 = st.columns(2)
        
        with col1:
            if StyledButton.render("Analyser", f"analyze_{symbol}", "primary"):
                with st.spinner("Analyse en cours..."):
                    analysis = self.analyzer.analyze_symbol(symbol)
                    self.alert_system.add_notification(
                        f"Analyse {symbol} terminée",
                        "success",
                        {
                            "Signal": analysis['signal'],
                            "RSI": f"{analysis['rsi']:.1f}",
                            "MACD": f"{analysis['macd']:.2f}"
                        }
                    )
        
        with col2:
            if StyledButton.render("Configurer Alertes", f"alerts_{symbol}", "warning"):
                price = self.exchange.get_ticker(symbol)['last']
                st.session_state[f'price_alert_{symbol}'] = price

    def main(self):
        """Point d'entrée principal de l'application"""
        self.setup_page()
        st.title("Crypto Analyzer Pro")
        
        try:
        # Récupération de tous les symboles disponibles
        available_symbols = self.exchange.get_available_symbols()
        
        # Ajout d'un champ de recherche pour filtrer les cryptos
        search_term = st.text_input("🔍 Rechercher une crypto", "").upper()
        
        # Filtrer les symboles selon la recherche
        filtered_symbols = [
            symbol for symbol in available_symbols 
            if search_term in symbol
        ] if search_term else available_symbols[:30]  # Limite aux 30 premiers si pas de recherche
        
        # Sélection de la crypto avec prix en temps réel
        selected_symbol = st.selectbox(
            "Sélectionner une crypto",
            filtered_symbols,
            format_func=lambda x: f"{x} - {self.exchange.get_ticker(x)['last']:,.2f} USDT",
            key="symbol_selector"
        )
        
        # Création du layout principal
        chart_col, analysis_col = st.columns([2, 1])
        
        with chart_col:
            # Sélecteur de période
            timeframe = TimeSelector.render("timeframe_selector")
            # Affichage du graphique
            self.render_chart_section(selected_symbol, timeframe)
            
        with analysis_col:
            # Vue d'ensemble du marché
            analysis = self.render_market_overview(selected_symbol)
            if analysis:
                # Contrôles d'analyse
                self.render_analysis_controls(selected_symbol)
                # Système d'alertes
                self.alert_system.render()

if __name__ == "__main__":
    app = CryptoAnalyzerApp()
    app.main()