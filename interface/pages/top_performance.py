# interface/pages/top_performance.py
import streamlit as st
from typing import Dict, List

class TopPerformancePage:
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
                step=10000,
                format="%d"
            )

        if st.button("🔄 Rechercher"):
            with st.spinner("Recherche des meilleures performances..."):
                try:
                    # Récupération des données
                    markets = self.exchange.get_available_symbols()
                    top_performers = []
                    
                    # Progress bar pour montrer l'avancement
                    progress_bar = st.progress(0)
                    total_markets = len(markets)
                    
                    for i, symbol in enumerate(markets):
                        try:
                            ticker = self.exchange.get_ticker(symbol)
                            if ticker.get('quoteVolume', 0) >= min_volume:
                                top_performers.append({
                                    'symbol': symbol,
                                    'price': ticker['last'],
                                    'change': ticker['percentage'],
                                    'volume': ticker['quoteVolume']
                                })
                            # Update progress
                            progress_bar.progress((i + 1) / total_markets)
                        except Exception:
                            continue
                            
                    # Tri des résultats
                    top_performers.sort(key=lambda x: abs(x['change']), reverse=True)
                    top_performers = top_performers[:10]  # Top 10
                    
                    # Affichage des résultats
                    if top_performers:
                        for crypto in top_performers:
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
                    else:
                        st.info("Aucune crypto ne correspond aux critères")
                        
                except Exception as e:
                    st.error(f"Erreur lors de la récupération des données : {str(e)}")