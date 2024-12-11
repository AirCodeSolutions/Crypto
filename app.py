# app.py
import streamlit as st
import time
import pandas as pd
from datetime import datetime
import logging
from typing import List, Dict
from interface import TimeSelector, TradingChart, ChartConfig, GuideHelper
from services.exchange import ExchangeService
from core.analysis import MarketAnalyzer
from interface.components.alerts import AlertSystem

# Configuration du logging pour un meilleur suivi des erreurs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAnalyzerApp:
    """Application principale d'analyse de cryptomonnaies en temps réel"""
    
    def __init__(self):
        try:
            self.exchange = ExchangeService()
            self.analyzer = MarketAnalyzer(self.exchange)
            self.alert_system = EnhancedAlertSystem()  # Nouveau système d'alertes
            
            if 'analyzed_symbols' not in st.session_state:
                st.session_state.analyzed_symbols = set()
            
            # Initialiser le thread de mise à jour des prix
            if 'last_price_check' not in st.session_state:
                st.session_state.last_price_check = time.time()
            
            logger.info("Application initialisée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur d'initialisation: {e}")
            raise

    def setup_page(self):
        """Configure la mise en page et les styles de l'application"""
        st.set_page_config(
            page_title="Crypto Analyzer Pro",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        st.markdown("""
        <style>
        /* Styles existants */
        .main h1 { font-size: 1.2rem !important; }
        
        /* Style pour la barre de recherche */
        [data-testid="stTextInput"] input {
            max-width: 200px !important;  /* Limite la largeur */
            font-size: 14px !important;   /* Taille de police appropriée */
            padding: 8px !important;      /* Padding réduit */
        }
        </style>
    """, unsafe_allow_html=True)
        
        # Styles CSS pour l'interface
        st.markdown("""
            <style>
            .main h1 { font-size: 1.2rem !important; }
            .crypto-metrics { 
                background-color: #f0f2f6; 
                padding: 1rem; 
                border-radius: 0.5rem; 
                margin: 1rem 0;
            }
            .signal-strong-buy { color: #00ff00; font-weight: bold; }
            .signal-buy { color: #008000; }
            .signal-neutral { color: #808080; }
            .signal-sell { color: #ff0000; }
            </style>
        """, unsafe_allow_html=True)

    def main(self):
        """
        Point d'entrée principal de l'application.
        Gère l'affichage de tous les composants et leur interaction.
        """
        try:
            self.setup_page()
            st.title("Crypto Analyzer by AirCodeSolutions 🚀")
            # Navigation
            page = st.sidebar.selectbox(
                "Navigation",
                ["Analyse en Direct", "Top Performances", "Guide"]
            )
            
            if page == "Analyse en Direct":

                # Section de recherche et sélection de crypto
                search_col1, search_col2 = st.columns([1, 3])  # Colonnes pour meilleure organisation
                with search_col1:
                    search_term = st.text_input(
                        "🔍",  # Juste une icône comme label
                        value="",
                        max_chars=5,
                        placeholder="BTC...",  # Exemple de ce qu'on attend
                        key="crypto_search"
                    ).upper()
                available_symbols = self.exchange.get_available_symbols()
                
                # Filtrage des cryptos selon la recherche
                filtered_symbols = [
                    symbol for symbol in available_symbols 
                    if search_term in symbol
                ] if search_term else available_symbols[:30]

                if not filtered_symbols:
                    st.warning("Aucune crypto trouvée pour votre recherche.")
                    return

                # Interface principale divisée en colonnes
                chart_col, analysis_col = st.columns([2, 1])
                
                with chart_col:
                    # Sélection de la crypto et de la période
                    selected_symbol = st.selectbox(
                        "Sélectionner une crypto",
                        filtered_symbols,
                        format_func=self._format_symbol_display
                    )
                    
                    # Sélecteur de période et affichage du graphique
                    timeframe = TimeSelector.render("timeframe_selector")
                    self._display_chart(selected_symbol, timeframe)

                with analysis_col:
                    self._display_analysis(selected_symbol)
                pass

            elif page == "Top Performances":
                from interface.pages.top_performance import TopPerformancePage
                top_page = TopPerformancePage(
                exchange_service=self.exchange,
                analyzer_service=self.analyzer  # Ajout de l'analyzer
                )
                top_page.render()

        except Exception as e:
            logger.error(f"Erreur dans l'application: {e}", exc_info=True)
            st.error(f"Une erreur est survenue: {str(e)}")
            if st.button("🔄 Rafraîchir"):
                st.rerun()

    def _format_symbol_display(self, symbol: str) -> str:
        """Formate l'affichage d'un symbole avec son prix actuel"""
        try:
            ticker = self.exchange.get_ticker(symbol)
            return f"{symbol} - ${ticker['last']:,.2f} USDT"
        except Exception as e:
            logger.error(f"Erreur format symbole: {e}")
            return symbol

    def _display_chart(self, symbol: str, timeframe: str):
        """Affiche le graphique pour un symbole donné"""
        try:
            df = self.exchange.get_ohlcv(symbol, timeframe)
            config = ChartConfig(height=400, show_volume=True)
            chart = TradingChart(config)
            chart.render(df, f"{symbol}/USDT")
        except Exception as e:
            logger.error(f"Erreur affichage graphique: {e}")
            st.error("Impossible d'afficher le graphique")

    def _display_analysis(self, symbol: str):
        """Affiche l'analyse avec progression et alertes"""
        if not symbol:
            st.info("📝 Sélectionnez une crypto pour voir l'analyse")
            return

        try:
            # Récupération des données et analyse
            analysis = self.analyzer.analyze_symbol(symbol)
            
            if analysis:
                # Affichage des métriques principales
                cols = st.columns([2, 2, 2, 3])
                
                with cols[0]:
                    st.metric(
                        "Prix",
                        f"${analysis['price']:,.2f}",
                        f"{analysis['change_24h']:+.2f}%"
                    )
                with cols[1]:
                    st.metric(
                        "RSI",
                        f"{analysis['rsi']:.1f}",
                        help="RSI > 70: Surachat, RSI < 30: Survente"
                    )
                with cols[2]:
                    st.metric(
                        "Score",
                        f"{analysis['score']:.2f}",
                        help="Score > 0.7: Signal fort"
                    )
                with cols[3]:
                    signal_style = {
                        "STRONG_BUY": "color: #00ff00; font-weight: bold;",
                        "BUY": "color: #008000;",
                        "NEUTRAL": "color: #808080;",
                        "SELL": "color: #ff0000;",
                        "STRONG_SELL": "color: #8b0000; font-weight: bold;"
                    }
                    st.markdown(
                        f"<div style='{signal_style[analysis['signal']]}'>"
                        f"Signal: {analysis['signal']}</div>",
                        unsafe_allow_html=True
                    )

                # Section des alertes de prix
                with st.expander("🔔 Configurer les Alertes de Prix"):
                    # Interface de configuration des alertes
                    col1, col2 = st.columns(2)
                    with col1:
                        alert_price = st.number_input(
                            "Prix d'alerte",
                            min_value=0.0,
                            value=float(analysis['price']),
                            step=0.0001
                        )
                    with col2:
                        alert_condition = st.selectbox(
                            "Condition",
                            options=["above", "below"],
                            format_func=lambda x: "Au-dessus" if x == "above" else "En-dessous"
                        )
                    
                    if st.button("➕ Ajouter l'alerte"):
                        self.alert_system.add_price_alert(symbol, alert_price, alert_condition)
                        st.success(f"Alerte ajoutée pour {symbol} à ${alert_price:.4f}")

                # Vérification des alertes de prix
                current_time = time.time()
                if current_time - st.session_state.last_price_check >= 5:  # Vérifier toutes les 5 secondes
                    self.alert_system.check_alerts(symbol, analysis['price'])
                    st.session_state.last_price_check = current_time

                # Affichage des notifications
                st.markdown("### 🔔 Notifications")
                self.alert_system.render()

        except Exception as e:
            logger.error(f"Erreur affichage analyse: {e}")
            st.error("Erreur lors de l'analyse")   

    def _analyze_candles(self, df) -> Dict:
        """Analyse des patterns de bougies"""
        try:
            last_candles = df.tail(5)  # Analyse des 5 dernières bougies
            
            patterns = {
                'bullish_patterns': [],
                'bearish_patterns': [],
                'trend': 'Neutre'
            }
            
            # Analyse tendance
            closing_prices = last_candles['close'].values
            opening_prices = last_candles['open'].values
            highs = last_candles['high'].values
            lows = last_candles['low'].values
            
            # Détection Marteau
            for i in range(len(last_candles)):
                body = abs(closing_prices[i] - opening_prices[i])
                lower_shadow = min(opening_prices[i], closing_prices[i]) - lows[i]
                upper_shadow = highs[i] - max(opening_prices[i], closing_prices[i])
                
                if lower_shadow > 2 * body and upper_shadow < body:
                    patterns['bullish_patterns'].append("Marteau")
                
                if upper_shadow > 2 * body and lower_shadow < body:
                    patterns['bearish_patterns'].append("Étoile Filante")
            
            # Analyse tendance globale
            if closing_prices[-1] > opening_prices[-1] and closing_prices[-1] > closing_prices[-2]:
                patterns['trend'] = 'Haussière'
            elif closing_prices[-1] < opening_prices[-1] and closing_prices[-1] < closing_prices[-2]:
                patterns['trend'] = 'Baissière'
                
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur analyse des bougies: {e}")
            return {
                'bullish_patterns': [],
                'bearish_patterns': [],
                'trend': 'Indéterminé'
            }

if __name__ == "__main__":
    app = CryptoAnalyzerApp()
    app.main()