# interface/pages/live_analysis.py
import streamlit as st
from typing import Optional
from ..components.widgets import TimeSelector  # Import correct
from ..components.guide_helper import GuideHelper
import logging

logger = logging.getLogger(__name__)

class LiveAnalysisPage:
    def __init__(self, exchange_service, analyzer_service):
        self.exchange = exchange_service
        self.analyzer = analyzer_service
    
    def render(self):
        st.title("📈 Analyse en Direct")
        # Ajouter l'aide en haut
        GuideHelper.show_indicator_help()
        GuideHelper.show_quick_guide()
        GuideHelper.show_pattern_guide()
        
        # Sélection de la crypto
        symbol = st.text_input(
            "Entrez le symbole de la crypto",
            value="BTC"
        ).upper()
        
        if symbol:
            # Récupération des données (à implémenter selon votre logique)
            data = self.get_crypto_data(symbol)
            df = self.get_historical_data(symbol)
            
            # Affichage du dashboard complet
            filters = self.dashboard.render_dashboard(df, symbol)
            
            # Analyse de l'opportunité
            self.dashboard.analyze_trading_opportunity(symbol, data)
            
            # Mise à jour périodique
            if st.button("🔄 Rafraîchir"):
                self.dashboard.update_analysis(symbol, data)

    def main(self):
        """Point d'entrée principal de l'application"""
        try:
            self.setup_page()
            st.title("Crypto Analyzer Pro - AirCodeSolutions ❤️")

            # Section Guide et Aide
            with st.container():
                GuideHelper.show_indicator_help()
                GuideHelper.show_quick_guide()
                
            # Section principale
            col_search, col_spacer = st.columns([1, 3])  # Pour réduire la taille de la barre de recherche
            with col_search:
                search_term = st.text_input("🔍", 
                    value="", 
                    max_chars=5,
                    placeholder="BTC...",
                    key="crypto_search"
                ).upper()

            # Filtrage des cryptos
            available_symbols = self.exchange.get_available_symbols()
            filtered_symbols = [
                symbol for symbol in available_symbols 
                if search_term in symbol
            ] if search_term else available_symbols[:30]

            if filtered_symbols:
                # Interface principale
                chart_col, analysis_col = st.columns([2, 1])
                
                with chart_col:
                    selected_symbol = st.selectbox(
                        "Sélectionner une crypto",
                        filtered_symbols,
                        format_func=self._format_symbol_display
                    )
                    
                    if selected_symbol:  # Si une crypto est sélectionnée
                        status_placeholder = st.empty()  # Pour les messages de statut
                        status_placeholder.info("Chargement du graphique...")
                        
                        timeframe = TimeSelector.render("timeframe_selector")
                        self._display_chart(selected_symbol, timeframe)
                        
                        status_placeholder.empty()  # Effacer le message une fois terminé
                
                with analysis_col:
                    if selected_symbol:
                        self._display_analysis(selected_symbol)
            else:
                st.warning("Aucune crypto trouvée pour votre recherche.")

        except Exception as e:
            st.error(f"Erreur: {str(e)}")
            return []