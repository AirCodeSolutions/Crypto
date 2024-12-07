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
        st.title("🏆 Top Performances (Prix ≤ 20 USDT)")
        
        # Section Guides
        GuideHelper.show_indicator_help()
        GuideHelper.show_pattern_guide()
        GuideHelper.show_quick_guide()
        
        # Section Vos Paramètres
        st.subheader("💰 Vos Paramètres")
        
        # Votre budget maximum
        budget = st.number_input(
            "Votre budget maximum (USDT)",
            value=100.00,
            min_value=10.00,
            step=10.0,
            key="budget_input"
        )

        # Prix maximum par crypto
        max_price = st.number_input(
            "Prix maximum par crypto (USDT)",
            value=5.00,
            max_value=20.00,
            min_value=0.10,
            step=0.10,
            key="max_price_input"
        )

        # Section Critères de Sécurité
        st.subheader("🛡️ Critères de Sécurité")
        
        # Volume minimum
        min_volume = st.number_input(
            "Volume minimum 24h (USDT)",
            value=50000.00,
            step=10000.0,
            key="volume_input"
        )

        # Score minimum
        min_score = st.slider(
            "Score minimum",
            min_value=0.00,
            max_value=1.00,
            value=0.60,
            key="score_slider"
        )

        if st.button("🔍 Rechercher des Opportunités"):
            with st.spinner("Analyse en cours..."):
                st.info(f"Budget: {budget} USDT, Prix max: {max_price} USDT")
                st.info(f"Volume min: {min_volume} USDT, Score min: {min_score}")
                
                results = self._get_best_opportunities(
                    max_price=max_price,
                    min_volume=min_volume,
                    min_score=min_score,
                    budget=budget
                )
                
                st.write(f"Nombre d'opportunités trouvées: {len(results)}")
                self._show_opportunities(results, budget)
            
                
    def _get_best_opportunities(self, max_price: float, min_volume: float, min_score: float, budget: float):
        """
        Version simplifiée mais efficace pour trouver des opportunités réelles
        """
        try:
            markets = self.exchange.get_available_symbols()
            opportunities = []
            
            for symbol in markets:
                try:
                    # Récupération du ticker
                    ticker = self.exchange.get_ticker(symbol)
                    price = float(ticker['last'])
                    
                    # Filtres de base
                    if price <= max_price and ticker['quoteVolume'] >= min_volume:
                        analysis = self.analyzer.analyze_symbol(symbol)
                        
                        if analysis and analysis['score'] >= min_score:
                            opportunities.append({
                                'symbol': symbol,
                                'price': price,
                                'volume': ticker['quoteVolume'],
                                'change': ticker['percentage'],
                                'score': analysis['score'],
                                'signal': analysis['signal'],
                                'investment': min(budget, price * 100)  # Limite l'investissement
                            })
                    
                except Exception as e:
                    print(f"Erreur pour {symbol}: {str(e)}")
                    continue

            # Tri par score et changement de prix
            return sorted(opportunities, key=lambda x: (x['score'], abs(x['change'])), reverse=True)
            
        except Exception as e:
            st.error(f"Erreur lors de la recherche : {str(e)}")
            return []
    
    def _show_opportunities(self, opportunities: List[Dict], budget: float):
        if not opportunities:
            st.info("Aucune opportunité trouvée avec ces critères")
            return
        
        st.markdown("### ⭐ Meilleures Opportunités Trouvées")
        
        for opp in opportunities:
            with st.container():
                st.markdown(f"#### {opp['symbol']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix", f"${opp['price']:.4f}", f"{opp['change']:+.2f}%")
                    st.write(f"Volume: ${opp['volume']/1e6:.1f}M")
                with col2:
                    tokens = opp['tokens_possible']
                    investment = opp['investment']
                    st.metric(
                        "Tokens possibles",
                        f"{tokens:.2f}",
                        f"Pour ${investment:.2f}"
                    )
                with col3:
                    st.metric("Score", f"{opp['score']:.2f}")
                    st.markdown(f"Signal: **{opp['signal']}**")
                
                st.markdown(f"💡 Avec {budget} USDT, vous pouvez acheter "
                        f"**{tokens:.2f}** tokens à **${opp['price']:.4f}**")
                
                st.markdown("---")