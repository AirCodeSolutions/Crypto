# interface/pages/top_performance.py
import streamlit as st
import pandas as pd
from typing import Dict, List
class TopPerformancePage:
    """Page des meilleures performances"""
    
    def __init__(self, exchange_service):
        self.exchange = exchange_service
        
    def render(self):
        st.title("🏆 Top Performances")
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            timeframe = st.selectbox(
                "Période",
                ["24h", "7j", "30j"],
                index=0
            )
        with col2:
            min_volume = st.number_input(
                "Volume minimum (USDT)",
                value=100000,
                step=50000
            )
            
        # Affichage du chargement
        with st.spinner("Recherche des meilleures performances..."):
            try:
                top_cryptos = self._get_top_performers(timeframe, min_volume)
                
                # Affichage des résultats
                for crypto in top_cryptos:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.metric(
                                crypto['symbol'],
                                f"${crypto['price']:,.2f}",
                                f"{crypto['change']:+.2f}%"
                            )
                        with col2:
                            st.metric(
                                "Volume 24h",
                                f"${crypto['volume']/1e6:.1f}M"
                            )
                        with col3:
                            if st.button("Analyser", key=f"analyze_{crypto['symbol']}"):
                                st.session_state.selected_crypto = crypto['symbol']
                                
            except Exception as e:
                st.error("Erreur lors de la récupération des données")
                
    def _get_top_performers(self, timeframe: str, min_volume: float) -> List[Dict]:
        """Récupère les cryptos les plus performantes"""
        # À implémenter : logique de récupération des top performers
        pass