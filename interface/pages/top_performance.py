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
            # 1. Récupération groupée de tous les tickers USDT
            all_tickers = self.exchange.exchange.fetch_tickers()
            
            # 2. Pré-filtrage initial des paires USDT qui respectent les critères de base
            filtered_pairs = {
                symbol: ticker for symbol, ticker in all_tickers.items()
                if (symbol.endswith('/USDT') and 
                    0 < float(ticker['last']) <= max_price and 
                    float(ticker.get('quoteVolume', 0)) >= min_volume)
            }

            # 3. Traitement par lots de 10 paires
            batch_size = 10
            opportunities = []
            total_batches = len(filtered_pairs) // batch_size + 1
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for batch_num in range(total_batches):
                batch_start = batch_num * batch_size
                batch_end = min((batch_num + 1) * batch_size, len(filtered_pairs))
                
                # Traiter le lot actuel
                batch_symbols = list(filtered_pairs.items())[batch_start:batch_end]
                status_text.text(f"Analyse du lot {batch_num + 1}/{total_batches}...")
                
                batch_opportunities = []
                for symbol, ticker in batch_symbols:
                    try:
                        base_symbol = symbol.split('/')[0]
                        analysis = self.analyzer.analyze_symbol(base_symbol)
                        
                        if analysis and analysis['score'] >= min_score:
                            price = float(ticker['last'])
                            volume = float(ticker['quoteVolume'])
                            tokens_possible = min(budget/price, volume/(price*10))
                            
                            batch_opportunities.append({
                                'symbol': base_symbol,
                                'price': price,
                                'volume': volume,
                                'change': ticker['percentage'],
                                'score': analysis['score'],
                                'rsi': analysis.get('rsi', 50),
                                'signal': analysis['signal'],
                                'tokens_possible': tokens_possible,
                                'investment': min(budget, tokens_possible * price)
                            })
                            
                    except Exception as e:
                        continue
                
                opportunities.extend(batch_opportunities)
                progress_bar.progress((batch_num + 1) / total_batches)

                # Si on a déjà trouvé 10 bonnes opportunités, on peut s'arrêter
                if len(opportunities) >= 10:
                    break
            
            status_text.empty()
            progress_bar.empty()

            # 4. Retourner les 10 meilleures opportunités
            sorted_opportunities = sorted(
                opportunities,
                key=lambda x: (x['score'], x['volume']),
                reverse=True
            )[:10]

            st.success(f"✅ Analyse terminée ! {len(sorted_opportunities)} opportunités trouvées")
            return sorted_opportunities

        except Exception as e:
            logger.error(f"Erreur _get_best_opportunities: {e}")
            st.error(f"Une erreur est survenue: {str(e)}")
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