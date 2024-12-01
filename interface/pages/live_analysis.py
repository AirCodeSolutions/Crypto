# interface/pages/live_analysis.py
import streamlit as st
from ..components.dashboard_manager import DashboardManager

class LiveAnalysisPage:
    def __init__(self):
        self.dashboard = DashboardManager()
    
    def render(self):
        st.title("📈 Analyse en Direct")
        
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