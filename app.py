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
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAnalyzerApp:
    def __init__(self):
        """Initialise les services et composants nécessaires"""
        try:
            self.exchange = ExchangeService()
            self.analyzer = MarketAnalyzer(self.exchange)
            self.alert_system = AlertSystem()
            
            if 'analyzed_symbols' not in st.session_state:
                st.session_state.analyzed_symbols = set()
                
            logger.info("Application initialisée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            raise

    def setup_page(self):
        """Configure la page et les styles"""
        st.set_page_config(
            page_title="Crypto Analyzer Pro",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
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
            analysis = self.analyzer.analyze_symbol(symbol)
            
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
            
            st.session_state.analyzed_symbols.add(symbol)
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse marché {symbol}: {e}")
            st.error(f"Erreur lors de l'analyse de {symbol}: {str(e)}")
            return None

    def render_chart_section(self, symbol: str, timeframe: str = '1h'):
        """Affiche la section graphique avec les données réelles"""
        try:
            df = self.exchange.get_ohlcv(symbol, timeframe)
            
            config = ChartConfig(
                height=400,
                show_volume=True,
                show_indicators=True
            )
            chart = TradingChart(config)
            chart.render(df, f"{symbol}/USDT")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur graphique {symbol}: {e}")
            st.error(f"Erreur lors du chargement du graphique: {str(e)}")
            return None

    def render_analysis_controls(self, symbol: str):
        """Affiche les contrôles d'analyse"""
        try:
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
                    
        except Exception as e:
            logger.error(f"Erreur contrôles analyse: {e}")
            st.error("Erreur lors de l'affichage des contrôles")

    def main(self):
        """Point d'entrée principal de l'application"""
        try:
            self.setup_page()
            st.title("Crypto Analyzer Pro")
            
            # Récupération et filtrage des symboles
            available_symbols = self.exchange.get_available_symbols()
            search_term = st.text_input("🔍 Rechercher une crypto", "").upper()
            
            filtered_symbols = [
                symbol for symbol in available_symbols 
                if search_term in symbol
            ] if search_term else available_symbols[:30]
            
            if not filtered_symbols:
                st.warning("Aucune crypto trouvée.")
                return

            # Sélection de la crypto
            selected_symbol = st.selectbox(
                "Sélectionner une crypto",
                filtered_symbols,
                format_func=lambda x: f"{x} - {self.exchange.get_ticker(x)['last']:,.2f} USDT",
                key="symbol_selector"
            )

            if selected_symbol:
                # Layout principal
                chart_col, analysis_col = st.columns([2, 1])
                
                with chart_col:
                    timeframe = TimeSelector.render("timeframe_selector")
                    self.render_chart_section(selected_symbol, timeframe)
                    
                with analysis_col:
                    analysis = self.render_market_overview(selected_symbol)
                    if analysis:
                        self.render_analysis_controls(selected_symbol)
                        self.alert_system.render()

        except ConnectionError as e:
            logger.error(f"Erreur de connexion: {e}")
            st.error("❌ Erreur de connexion à l'exchange. Vérifiez votre connexion internet.")
            
        except Exception as e:
            logger.error(f"Erreur application: {e}", exc_info=True)
            st.error(f"❌ Une erreur est survenue: {str(e)}")
            if st.button("🔄 Rafraîchir"):
                st.rerun()

if __name__ == "__main__":
    app = CryptoAnalyzerApp()
    app.main()