# app.py
import streamlit as st
import time
import pandas as pd
from datetime import datetime
import logging
from typing import List, Dict
from interface import TimeSelector, TradingChart, ChartConfig, GuideHelper
from services.exchange import ExchangeService
from services.storage import AirtableService
from core.analysis import MarketAnalyzer
from interface.components.alerts import AlertSystem
from interface.components.auth_manager import AuthManager
from interface.pages.live_analysis import LiveAnalysisPage

# Configuration du logging pour un meilleur suivi des erreurs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAnalyzerApp:
    """Application principale d'analyse de cryptomonnaies en temps réel"""
    
    def __init__(self):
        try:
            self.exchange = ExchangeService()
            self.analyzer = MarketAnalyzer(self.exchange)
            self.alert_system = AlertSystem()  # Nouveau système d'alertes
            self.airtable = AirtableService()
            self.auth_manager = AuthManager(self.airtable)
            
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
            page_title="Crypto Analyzer by AirCodeSolutions",
            page_icon="📊",
            layout="wide",
            #initial_sidebar_state="collapsed"
            initial_sidebar_state="auto"
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
       
        self.setup_page()
        # Gestion de l'authentification
        if not st.session_state.logged_in:
            self._show_auth_page()
            return
            
        # Navigation pour les utilisateurs connectés
        self._show_main_interface()

    def _show_auth_page(self):
        """Affiche la page d'authentification"""
        st.title("Crypto Analyzer Pro - AirCodeSolutions ❤️")
        
        tab1, tab2 = st.tabs(["Connexion", "Inscription"])
        
        with tab1:
            self.auth_manager.render_login_form()
            
        with tab2:
            self.auth_manager.render_register_form()

    def _show_main_interface(self):
        """Affiche l'interface principale pour les utilisateurs connectés"""
        st.sidebar.title(f"👤 {st.session_state.user_info['username']}")
        
        if st.sidebar.button("📤 Déconnexion"):
            self.auth_manager.logout()
            st.rerun()

        # Navigation
        page = st.sidebar.selectbox(
            "Navigation",
            ["Analyse en Direct", "Top Performances", "Portfolio", "Paramétres", "Guide"]
            )
            
        # Affichage de la page sélectionnée
        if page == "Analyse en Direct":
            LiveAnalysisPage(
                exchange_service=self.exchange,
                analyzer_service=self.analyzer
            ).render()

        elif page == "Top Performances":
            from interface.pages.top_performance import TopPerformancePage
            top_page = TopPerformancePage(
            exchange_service=self.exchange,
            analyzer_service=self.analyzer  # Ajout de l'analyzer
            )
            top_page.render()

        elif page == "Portfolio":
           self._show_portfolio_page()
                        
        elif page == "Paramètres":
            self._show_settings_page()

    def _show_portfolio_page(self):
        """Affiche la page du portfolio"""
        st.title("💼 Portfolio")
        # Vous pouvez implémenter le contenu du portfolio ici...

    def _show_settings_page(self):
        """Affiche la page des paramètres"""
        st.title("⚙️ Paramètres")
        
        settings = st.session_state.user_info.get('settings', {})
        
        with st.form("settings_form"):
            new_capital = st.number_input(
                "Capital initial (USDT)",
                min_value=0.0,
                value=float(settings.get('initial_capital', 1000))
            )
            
            new_risk = st.slider(
                "Risque par trade (%)",
                min_value=0.5,
                max_value=5.0,
                value=float(settings.get('risk_per_trade', 1.5)),
                step=0.5
            )
            
            if st.form_submit_button("Sauvegarder"):
                try:
                    self.airtable.utilisateurs.update(
                        st.session_state.user_info['id'],
                        {
                            "settings": {
                                "initial_capital": new_capital,
                                "risk_per_trade": new_risk
                            }
                        }
                    )
                    st.success("Paramètres sauvegardés !")
                    
                    # Mise à jour des informations en session
                    st.session_state.user_info['settings'] = {
                        "initial_capital": new_capital,
                        "risk_per_trade": new_risk
                    }
                    
                except Exception as e:
                    st.error(f"Erreur lors de la sauvegarde: {str(e)}")        

       

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
        """Affiche l'analyse avec progression et guide"""
        if not symbol:
            st.info("📝 Sélectionnez une crypto pour voir l'analyse")
            return
            
        # Conteneur pour le guide
        with st.container():
            GuideHelper.show_indicator_help()

        # Message et barre de progression
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        try:
            # Étape 1: Chargement initial
            progress_text.text("Chargement des données...")
            progress_bar.progress(25)
            
            # Étape 2: Analyse
            progress_text.text("Analyse en cours...")
            analysis = self.analyzer.analyze_symbol(symbol)
            progress_bar.progress(75)

            if analysis:
                # Nettoyage des indicateurs de progression
                progress_text.empty()
                progress_bar.empty()        
                
                # Métriques principales
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

                # Section des alertes de prix
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
                        self.alert_system.add_price_alert(symbol, alert_price, alert_condition)
                        st.success(f"Alerte ajoutée pour {symbol} à ${alert_price:.4f}")

                # Boutons d'action
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
                    
                with action_cols[1]:
                    if st.button("🔔 Configurer Alertes", key=f"alerts_{symbol}"):
                        self.alert_system.add_notification(
                            f"Alerte configurée pour {symbol}",
                            "info",
                            {"Prix": f"${analysis['price']:,.2f}"}
                        )

                # Vérification des alertes de prix
                current_time = time.time()
                if current_time - st.session_state.get('last_price_check', 0) >= 5:
                    self.alert_system.check_alerts(symbol, analysis['price'])
                    st.session_state['last_price_check'] = current_time

                # Affichage des notifications
                st.markdown("### 🔔 Notifications")
                self.alert_system.render()

                # Analyse des bougies
                if analysis:
                    # Ajout de l'analyse des bougies
                    with st.expander("📊 Analyse des Bougies"):
                        df = self.exchange.get_ohlcv(symbol)
                        candle_analysis = self._analyze_candles(df)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### 🟢 Patterns Haussiers")
                            for pattern in candle_analysis['bullish_patterns']:
                                st.write(f"✓ {pattern}")
                        with col2:
                            st.markdown("### 🔴 Patterns Baissiers")
                            for pattern in candle_analysis['bearish_patterns']:
                                st.write(f"✓ {pattern}")

                        st.markdown(f"**Tendance actuelle:** {candle_analysis['trend']}")

            else:
                st.warning("Aucune donnée disponible pour cette crypto")

        except Exception as e:
            progress_text.empty()
            progress_bar.empty()
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