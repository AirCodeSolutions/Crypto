# interface/pages/live_analysis.py
from typing import Optional, Dict
import streamlit as st
from datetime import datetime
from ..components.widgets import TimeSelector
from ..components.guide_helper import GuideHelper
from ..components.chart_components import TradingChart, ChartConfig
from ..components.alerts import AlertSystem
from core.signal_tracking import SignalHistory  
from services.storage import AirtableService
import logging

logger = logging.getLogger(__name__)

class LiveAnalysisPage:
    def __init__(self, exchange_service, analyzer_service, alert_system, airtable_service):
        self.exchange = exchange_service
        self.analyzer = analyzer_service
        self.alert_system = alert_system
        self.airtable = airtable_service
           
          # Vérifier si l'utilisateur est connecté et récupérer son ID
        if 'user_info' in st.session_state and st.session_state.user_info:
            user_id = st.session_state.user_info['id']
            self.signal_history = SignalHistory(airtable_service=self.airtable, user_id=user_id)
        else:
            logger.warning("Aucun utilisateur connecté")
            self.signal_history = None  # ou gérer autrement le cas où l'utilisateur n'est pas connecté
      
    def render(self):
        st.title("📈 Analyse en Direct", anchor=False)

        # Guide et aide
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
        try:
            ticker = self.exchange.get_ticker(symbol)
            return f"{symbol} - ${ticker['last']:,.2f} USDT"
        except Exception as e:
            logger.error(f"Erreur format symbole: {e}")
            return symbol

    def _display_chart(self, symbol: str, timeframe: str):
        try:
            df = self.exchange.get_ohlcv(symbol, timeframe)
            if df is not None:
                config = ChartConfig(
                    height=600,  # Augmenté pour mieux remplir l'espace
                    show_volume=True,
                    template="plotly_dark"
                )
                chart = TradingChart(config)
                chart.render(df, f"{symbol}/USDT")
            else:
                st.error("Données non disponibles pour le graphique")
        except Exception as e:
            logger.error(f"Erreur affichage graphique: {e}")
            st.error("Impossible d'afficher le graphique")
    
    def _display_performance_dashboard(self):
        """Affiche le tableau de bord des performances des signaux"""
        st.subheader("📊 Performance des Signaux")

        # Statistiques principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Signaux Total",
                self.signal_history.signal_stats['total_signals'],
                help="Nombre total de signaux générés"
            )
        with col2:
            success_rate = (self.signal_history.signal_stats['successful'] / 
                        self.signal_history.signal_stats['total_signals'] * 100) if self.signal_history.signal_stats['total_signals'] > 0 else 0
            st.metric(
                "Taux de Réussite",
                f"{success_rate:.1f}%",
                help="Pourcentage de signaux réussis"
            )
        with col3:
            st.metric(
                "Signaux Actifs",
                self.signal_history.signal_stats['pending'],
                help="Signaux en cours"
            )
        with col4:
            # Calcul du ratio gain/perte moyen des signaux terminés
            avg_profit = self.signal_history.average_profit if hasattr(self.signal_history, 'average_profit') else 0
            st.metric(
                "Profit Moyen",
                f"{avg_profit:.2f}%",
                help="Performance moyenne par signal"
            )

        # Historique des signaux récents
        with st.expander("📜 Historique des Signaux"):
            if self.signal_history.signals:
                for signal in reversed(self.signal_history.signals[-10:]):  # 10 derniers signaux
                    signal_color = {
                        'successful': '🟢',
                        'failed': '🔴',
                        'pending': '⚪'
                    }.get(signal['status'], '⚪')
                    
                    st.write(
                        f"{signal_color} {signal['symbol']} - {signal['type']} - "
                        f"Prix: ${signal['entry_price']:.4f} - "
                        f"Status: {signal['status'].title()} - "
                        f"Date: {signal['timestamp'].strftime('%d/%m/%Y %H:%M')}"
                    )
            else:
                st.info("Aucun signal dans l'historique")

        # Statistiques par type de signal
        st.subheader("📈 Performance par Type de Signal")
        signal_types_col1, signal_types_col2 = st.columns(2)
        
        with signal_types_col1:
            st.markdown("### Signaux d'Achat")
            buy_success = self.signal_history.get_success_rate('BUY')
            st.metric(
                "Taux de Réussite Achats",
                f"{buy_success:.1f}%",
                help="Pourcentage de signaux d'achat réussis"
            )
            
        with signal_types_col2:
            st.markdown("### Signaux de Vente")
            sell_success = self.signal_history.get_success_rate('SELL')
            st.metric(
                "Taux de Réussite Ventes",
                f"{sell_success:.1f}%",
                help="Pourcentage de signaux de vente réussis"
            )

    def _display_analysis(self, symbol: str):
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
                    # Appel de la méthode pour vérifier les alertes RSI
                    self.alert_system.check_rsi_alert(symbol, analysis['rsi'])

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


                
                # Mise à jour des signaux existants avec le prix actuel
                current_price = analysis['price']
                self.signal_history.update_signal_status(symbol, current_price)

                 # Vérifier si un nouveau signal doit être généré
                if analysis['signal'] in ['STRONG_BUY', 'BUY', 'STRONG_SELL', 'SELL']:
                    # Calculer les niveaux de prix
                    stop_loss = current_price * 0.985 if analysis['signal'] in ['STRONG_BUY', 'BUY'] else current_price * 1.015
                    target_price = current_price * 1.03 if analysis['signal'] in ['STRONG_BUY', 'BUY'] else current_price * 0.97

                    # Ajouter le nouveau signal
                    self.signal_history.add_signal(
                        symbol=symbol,
                        signal_type='BUY' if analysis['signal'] in ['STRONG_BUY', 'BUY'] else 'SELL',
                        entry_price=current_price,
                        target_price=target_price,
                        stop_loss=stop_loss
                )

                # Calcul des EMA et vérification des croisements
                df = self.exchange.get_ohlcv(symbol, "1h")  # Exemple : timeframe 1h
                if df is not None:
                    df['EMA_short'] = df['close'].ewm(span=12).mean()  # EMA court (12 périodes)
                    df['EMA_long'] = df['close'].ewm(span=26).mean()  # EMA long (26 périodes)

                    # Vérification du croisement EMA
                    if len(df) > 1:  # Vérifier qu'il y a suffisamment de données
                        short_ema = df['EMA_short'].iloc[-1]
                        long_ema = df['EMA_long'].iloc[-1]
                        self.alert_system.check_ema_crossover(symbol, short_ema, long_ema)

                    # Affichage des EMA dans l'interface
                    st.write(f"**EMA Court (12 périodes)**: {df['EMA_short'].iloc[-1]:.2f}")
                    st.write(f"**EMA Long (26 périodes)**: {df['EMA_long'].iloc[-1]:.2f}")



                # Détails de l'analyse
                with st.expander("📊 Détails techniques"):
                    if 'analysis' in analysis and isinstance(analysis['analysis'], dict):
                        for key, value in analysis['analysis'].items():
                            if key != 'patterns':  # Exclure les patterns car affichés séparément
                                st.write(f"**{key.title()}:** {value}")

                # Analyse des bougies
                with st.expander("🕯️ Analyse des Bougies"):
                    df = self.exchange.get_ohlcv(symbol)
                    candle_analysis = self._analyze_candles(df)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 🟢 Patterns Haussiers")
                        if candle_analysis['bullish_patterns']:
                            for pattern in candle_analysis['bullish_patterns']:
                                st.write(f"✓ {pattern}")
                        else:
                            st.write("Aucun pattern haussier détecté")
                            
                    with col2:
                        st.markdown("### 🔴 Patterns Baissiers")
                        if candle_analysis['bearish_patterns']:
                            for pattern in candle_analysis['bearish_patterns']:
                                st.write(f"✓ {pattern}")
                        else:
                            st.write("Aucun pattern baissier détecté")
                    
                    st.markdown(f"**Tendance actuelle:** {candle_analysis['trend']}")

                # Configuration des alertes
                with st.expander("🔔 Alertes de Prix"):
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

                # Boutons d'action
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📈 Analyser", key=f"analyze_{symbol}"):
                        self.alert_system.add_notification(
                            f"Analyse de {symbol} terminée",
                            "success",
                            {
                                "Signal": analysis['signal'],
                                "RSI": f"{analysis['rsi']:.1f}"
                            }
                        )

                # Affichage des notifications
                st.markdown("### 🔔 Notifications")
                self.alert_system.render()

                 # Ajouter le tableau de bord des performances ici
                st.markdown("---")  # Séparateur visuel
                self._display_performance_dashboard()  # Appel de la nouvelle méthode

        except Exception as e:
            logger.error(f"Erreur affichage analyse: {e}")
            st.error("Erreur lors de l'analyse")

    def _analyze_candles(self, df) -> Dict:
        """Analyse des patterns de bougies"""
        try:
            last_candles = df.tail(5)
            patterns = {
                'bullish_patterns': [],
                'bearish_patterns': [],
                'trend': 'Neutre'
            }
            
            closing_prices = last_candles['close'].values
            opening_prices = last_candles['open'].values
            highs = last_candles['high'].values
            lows = last_candles['low'].values
            
            for i in range(len(last_candles)):
                body = abs(closing_prices[i] - opening_prices[i])
                lower_shadow = min(opening_prices[i], closing_prices[i]) - lows[i]
                upper_shadow = highs[i] - max(opening_prices[i], closing_prices[i])
                
                if lower_shadow > 2 * body and upper_shadow < body:
                    patterns['bullish_patterns'].append("Marteau")
                if upper_shadow > 2 * body and lower_shadow < body:
                    patterns['bearish_patterns'].append("Étoile Filante")
            
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
