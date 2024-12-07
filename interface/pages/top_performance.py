# interface/pages/top_performance.py
import streamlit as st
import time
from typing import List, Dict
from ..components.guide_helper import GuideHelper

class TopPerformancePage:
    """Page d'analyse des meilleures performances"""
    
    def __init__(self, exchange_service, analyzer_service):
        """Initialise la page avec les services nécessaires"""
        self.exchange = exchange_service
        self.analyzer = analyzer_service
        
    def render(self):
        """Affiche la page de top performance"""
        st.title("🏆 Top Performances")
        
        # Affichage du guide
        GuideHelper.show_indicator_help()
        
        # Configuration des filtres
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
                step=10000
            )

        # Bouton de recherche
        if st.button("🔍 Rechercher"):
            self._display_top_performers(timeframe, min_volume)
            
    def _display_top_performers(self, timeframe: str, min_volume: float):
        """Affiche les meilleures performances"""
        with st.spinner("Analyse en cours..."):
            try:
                performers = self._get_top_performers(timeframe, min_volume)
                self._render_results(performers)
            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {str(e)}")
                
    def _get_top_performers(self, timeframe: str, min_volume: float) -> List[Dict]:
        """Récupère les meilleures performances"""
        performers = []
        symbols = self.exchange.get_available_symbols()
        
        progress = st.progress(0.0)
        total = len(symbols)
        
        for i, symbol in enumerate(symbols[:50]):  # Limite aux 50 premiers
            try:
                ticker = self.exchange.get_ticker(symbol)
                if ticker['quoteVolume'] >= min_volume:
                    analysis = self.analyzer.analyze_symbol(symbol)
                    if analysis:
                        performers.append({
                            'symbol': symbol,
                            'price': ticker['last'],
                            'volume': ticker['quoteVolume'],
                            'change': ticker['percentage'],
                            'score': analysis['score'],
                            'signal': analysis['signal']
                        })
                progress.progress((i + 1) / total)
            except Exception:
                continue
                
        # Tri par score et changement de prix
        return sorted(
            performers,
            key=lambda x: (x['score'], abs(x['change'])),
            reverse=True
        )[:10]
        
    def _render_results(self, performers: List[Dict]):
        """Affiche les résultats"""
        if not performers:
            st.info("Aucun résultat trouvé")
            return
            
        for perf in performers:
            with st.container():
                cols = st.columns([2, 2, 2, 2])
                with cols[0]:
                    st.metric(
                        perf['symbol'],
                        f"${perf['price']:,.2f}",
                        f"{perf['change']:+.2f}%"
                    )
                with cols[1]:
                    st.metric(
                        "Volume 24h",
                        f"${perf['volume']/1e6:.1f}M"
                    )
                with cols[2]:
                    st.metric(
                        "Score",
                        f"{perf['score']:.2f}"
                    )
                with cols[3]:
                    st.write(f"Signal: {perf['signal']}")