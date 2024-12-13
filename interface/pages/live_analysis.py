from typing import Optional, Dict
import streamlit as st
from ..components.widgets import TimeSelector
from ..components.guide_helper import GuideHelper
from ..components.chart_components import TradingChart, ChartConfig
from ..components.alerts import AlertSystem
import logging

logger = logging.getLogger(__name__)

class LiveAnalysisPage:
    def __init__(self, exchange_service, analyzer_service, alert_system):
        """Initialise la page avec les services nécessaires"""
        self.exchange = exchange_service
        self.analyzer = analyzer_service
        self.alert_system = alert_system

    def render(self):
        """Affiche la page d'analyse en direct"""
        st.title("📈 Analyse en Direct")

        # Guide et aide
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                GuideHelper.show_indicator_help()
                GuideHelper.show_pattern_guide()
            with col2:
                GuideHelper.show_quick_guide()

        # Section de recherche
        search_col1, search_col2 = st.columns([1, 2])
        with search_col1:
            search_term = st.text_input(
                "🔍",
                value="",
                max_chars=5,
                placeholder="BTC...",
                key="crypto_search"
            ).upper()

        # Récupération et filtrage des symboles
        available_symbols = self.exchange.get_available_symbols()
        filtered_symbols = [
            symbol for symbol in available_symbols 
            if search_term in symbol
        ] if search_term else available_symbols[:30]

        if not filtered_symbols:
            st.warning("Aucune crypto trouvée pour votre recherche.")
            return

        # Interface principale
        chart_col, analysis_col = st.columns([1, 1])
        
        with chart_col:
            selected_symbol = st.selectbox(
                "Sélectionner une crypto",
                filtered_symbols,
                format_func=self._format_symbol_display
            )
            
            if selected_symbol:
                timeframe = TimeSelector.render("timeframe_selector")
                self._display_chart(selected_symbol, timeframe)

        with analysis_col:
            if selected_symbol:
                self._display_analysis(selected_symbol)

    def _format_symbol_display(self, symbol: str) -> str:
        """Formate l'affichage d'un symbole avec son prix"""
        try:
            ticker = self.exchange.get_ticker(symbol)
            return f"{symbol} - ${ticker['last']:,.2f} USDT"
        except Exception as e:
            logger.error(f"Erreur format symbole: {e}")
            return symbol

    def _display_chart(self, symbol: str, timeframe: str):
        """Affiche le graphique de trading"""
        try:
            df = self.exchange.get_ohlcv(symbol, timeframe)
            if df is not None:
                config = ChartConfig(height=300, show_volume=True, template="plotly_dark")
                chart = TradingChart(config)
                chart.render(df, f"{symbol}/USDT")
            else:
                st.error("Données non disponibles pour le graphique")
        except Exception as e:
            logger.error(f"Erreur affichage graphique: {e}")
            st.error("Impossible d'afficher le graphique")

    def _display_analysis(self, symbol: str):
        """Affiche l'analyse technique"""
        try:
            analysis = self.analyzer.analyze_symbol(symbol)
            if analysis:
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

                # Détails de l'analyse
                if 'analysis' in analysis and isinstance(analysis['analysis'], dict):
                    with st.expander("📊 Détails de l'analyse"):
                        for key, value in analysis['analysis'].items():
                            st.write(f"**{key.title()}:** {value}")

                    with st.expander("🔔 Configurer les Alertes de Prix"):
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
                            self.alert_system.add_notification(
                                f"Alerte configurée pour {symbol} à ${alert_price:.4f}",
                                "info",
                                {
                                    "Prix": f"${alert_price:.4f}",
                                    "Condition": "Au-dessus" if alert_condition == "above" else "En-dessous"
                                }
                            )

                    # Boutons d'action et notifications
                    action_cols = st.columns(2)
                    with action_cols[0]:
                        if st.button("📈 Analyser", key=f"analyze_{symbol}"):
                            self.alert_system.add_notification(
                                f"Analyse de {symbol} terminée",
                                "success",
                                {
                                    "Signal": analysis['signal'],
                                    "RSI": f"{analysis['rsi']:.1f}"
                                }
                            )
                    # Affichage de l'analyse des bougies
                    with st.expander("📊 Analyse des Bougies"):
                        df = self.exchange.get_ohlcv(symbol)
                        candle_analysis = self._analyze_candles(df)
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
    
