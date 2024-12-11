from typing import Optional
import streamlit as st
from ..components.widgets import TimeSelector
from ..components.guide_helper import GuideHelper
from ..components.chart_components import TradingChart, ChartConfig
import logging

logger = logging.getLogger(__name__)

class LiveAnalysisPage:
    def __init__(self, exchange_service, analyzer_service):
        """Initialise la page avec les services nécessaires"""
        self.exchange = exchange_service
        self.analyzer = analyzer_service

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
        search_col1, search_col2 = st.columns([1, 3])
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
        chart_col, analysis_col = st.columns([2, 1])
        
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
                config = ChartConfig(height=400, show_volume=True)
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

        except Exception as e:
            logger.error(f"Erreur affichage analyse: {e}")
            st.error("Erreur lors de l'analyse")