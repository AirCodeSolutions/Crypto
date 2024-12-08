# interface/pages/top_performance.py
import streamlit as st
import time
from typing import List, Dict
from ..components.guide_helper import GuideHelper
import logging

logger = logging.getLogger(__name__)

class TopPerformancePage:
    def __init__(self, exchange_service, analyzer_service):
        """Initialise la page avec les services nécessaires"""
        self.exchange = exchange_service
        self.analyzer = analyzer_service
        
    def render(self):
        st.title("🏆 Top Performances")
        # Section Guides
        #GuideHelper.show_indicator_help()
        #GuideHelper.show_pattern_guide()
        #GuideHelper.show_quick_guide()
        # Section Guides
        with st.expander("ℹ️ Guide des Opportunités", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🎯 Configuration Idéale
                - Score technique > 0.7
                - RSI entre 30-45
                - Volume croissant
                - Support proche (-1-2%)
                """)
                
            with col2:
                st.markdown("""
                ### 💰 Gestion des Trades
                - Stop loss : -1.5% du prix d'entrée
                - Target 1 : +3%
                - Target 2 : +5%
                - Sortie partielle au T1
                """)

        # Section Paramètres
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Paramètres d'Investissement")
            budget = st.number_input(
                "Budget disponible (USDT)",
                min_value=10.0,
                value=100.0,
                step=10.0
            )
            
            max_price = st.number_input(
                "Prix maximum par crypto (USDT)",
                min_value=0.1,
                max_value=20.0,
                value=5.0
            )

        with col2:
            st.subheader("🔒 Critères de Sécurité")
            min_volume = st.number_input(
                "Volume minimum 24h (USDT)",
                min_value=10000.0,
                value=50000.0,
                step=10000.0
            )
            
            min_score = st.slider(
                "Score minimum",
                min_value=0.0,
                max_value=1.0,
                value=0.7
            )

        if st.button("🔍 Rechercher des Opportunités", type="primary"):
            try:
                with st.spinner("Analyse en cours..."):
                    results = self._get_best_opportunities(
                        max_price=max_price,
                        min_volume=min_volume,
                        min_score=min_score,
                        budget=budget
                    )
                    
                    if results:
                        st.success(f"🎯 {len(results)} opportunités trouvées!")
                        self._show_opportunities(results, budget)
                    else:
                        st.info("Aucune opportunité trouvée avec ces critères")
                        
            except Exception as e:
                st.error(f"Erreur lors de la recherche : {str(e)}")
                logger.error(f"Erreur recherche opportunités: {e}")

    def _get_best_opportunities(self, max_price: float, min_volume: float, min_score: float, budget: float) -> List[Dict]:
        try:
            status_text = st.empty()
            status_text.text("Récupération des données du marché...")
            
            # 1. Récupérer tous les tickers en une seule requête
            tickers = self.exchange.exchange.fetch_tickers()
            
            # 2. Filtrage rapide des paires USDT
            opportunities = []
            status_text.text("Analyse des meilleures opportunités...")
            
            # Première passe ultra rapide : sélectionner les meilleures paires sur critères simples
            candidates = []
            for symbol, ticker in tickers.items():
                if not symbol.endswith('/USDT'):
                    continue
                    
                try:
                    price = float(ticker['last'])
                    volume = float(ticker.get('quoteVolume', 0))
                    change = float(ticker.get('percentage', 0))
                    
                    # Filtres de base
                    if (0 < price <= max_price and 
                        volume >= min_volume and 
                        -5 <= change <= 15):  # Éviter les pumps trop importants
                        
                        candidates.append({
                            'symbol': symbol.split('/')[0],
                            'price': price,
                            'volume': volume,
                            'change': change
                        })
                        
                except:
                    continue
            
            # Limiter aux 20 meilleures paires par volume
            candidates.sort(key=lambda x: x['volume'], reverse=True)
            candidates = candidates[:20]
            
            # Seconde passe : analyse technique uniquement sur les meilleurs candidats
            for candidate in candidates:
                try:
                    analysis = self.analyzer.analyze_symbol(candidate['symbol'])
                    if analysis and analysis['score'] >= min_score:
                        tokens_possible = min(
                            budget/candidate['price'], 
                            candidate['volume']/(candidate['price']*10)
                        )
                        
                        opportunities.append({
                            **candidate,
                            'score': analysis['score'],
                            'rsi': analysis.get('rsi', 50),
                            'signal': analysis['signal'],
                            'tokens_possible': tokens_possible,
                            'investment': min(budget, tokens_possible * candidate['price'])
                        })
                        
                        # S'arrêter si on a assez d'opportunités
                        if len(opportunities) >= 10:
                            break
                            
                except Exception as e:
                    continue
                    
            status_text.empty()

            # Retourner les meilleures opportunités triées
            return sorted(opportunities, key=lambda x: x['score'], reverse=True)

        except Exception as e:
            st.error(f"Erreur lors de la recherche : {str(e)}")
            return []
    def _show_opportunities(self, opportunities: List[Dict], budget: float):
        for opp in opportunities:
            with st.expander(f"💫 {opp['symbol']} - Score: {opp['score']:.2f}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Prix",
                        f"${opp['price']:.4f}",
                        f"{opp['change']:+.2f}%"
                    )
                with col2:
                    st.metric(
                        "Volume 24h",
                        f"${opp['volume']/1e6:.1f}M"
                    )
                with col3:
                    st.metric("RSI", f"{opp['rsi']:.1f}")
                    
                # Calcul des niveaux suggérés
                stop_loss = opp['price'] * 0.985  # -1.5%
                target_1 = opp['price'] * 1.03    # +3%
                target_2 = opp['price'] * 1.05    # +5%
                
                st.markdown("### 📊 Position Suggérée")
                level_col1, level_col2, level_col3 = st.columns(3)
                with level_col1:
                    st.write("🛡️ Stop Loss:", f"${stop_loss:.4f}")
                with level_col2:
                    st.write("🎯 Target 1:", f"${target_1:.4f}")
                with level_col3:
                    st.write("🎯 Target 2:", f"${target_2:.4f}")
                    
                st.markdown(f"💡 Investissement suggéré: **${opp['investment']:.2f}** USDT")
                st.markdown(f"🪙 Nombre de tokens: **{opp['tokens_possible']:.2f}**")
                
                if st.button("📝 Préparer l'ordre", key=f"prep_{opp['symbol']}"):
                    st.session_state['prepared_trade'] = {
                        'symbol': opp['symbol'],
                        'price': opp['price'],
                        'stop_loss': stop_loss,
                        'target_1': target_1,
                        'target_2': target_2,
                        'suggested_amount': opp['investment'],
                        'score': opp['score']
                    }
                    st.success(f"✅ Trade préparé pour {opp['symbol']}! Allez dans Portfolio pour finaliser l'ordre.")

                st.markdown("---")