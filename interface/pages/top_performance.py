# interface/pages/top_performance.py
import streamlit as st
import time
from typing import List, Dict
from ..components.guide_helper import GuideHelper
import logging

class TopPerformancePage:
    def __init__(self, exchange_service, analyzer_service):
        """Initialise la page avec les services nécessaires"""
        self.exchange = exchange_service
        self.analyzer = analyzer_service
        
    def render(self):
        st.title("🏆 Top Performances ")
        # Section Guides
       # GuideHelper.show_indicator_help()
       # GuideHelper.show_pattern_guide()
       # GuideHelper.show_quick_guide()
        GuideHelper.show_opportunites_guide()

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
            st.subheader("🛡️ Critères de Sécurité")
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
                value=0.6
            )

        if st.button("🔍 Rechercher des Opportunités"):
            with st.spinner("Analyse du marché en cours..."):
                results = self._get_best_opportunities(
                    max_price=max_price,
                    min_volume=min_volume,
                    min_score=min_score,
                    budget=budget
                )
                
                if results:
                    st.success(f"🎯 {len(results)} opportunités trouvées !")
                    self._show_opportunities(results, budget)
                else:
                    st.warning("🔍 Aucune opportunité ne correspond aux critères actuels.")
                    st.info("""
                    💡 Suggestions pour trouver des opportunités:
                    - Augmentez le prix maximum (actuellement: {}$ USDT)
                    - Réduisez le volume minimum (actuellement: {}k USDT)
                    - Baissez le score minimum (actuellement: {})
                    - Revenez vérifier dans quelques minutes
                    """.format(max_price, min_volume/1000, min_score))
                    
                    # Afficher les meilleurs volumes même s'ils ne correspondent pas aux critères
                    self._show_top_volumes(max_price)

    def _get_best_opportunities(self, max_price: float, min_volume: float, min_score: float, budget: float) -> List[Dict]:
        try:
            status_text = st.empty()
            status_text.text("Récupération des données du marché...")
            
            tickers = self.exchange.exchange.fetch_tickers()
            candidates = []
            
            status_text.text("Analyse des pairs...")
            for symbol, ticker in tickers.items():
                if not symbol.endswith('/USDT'):
                    continue
                    
                try:
                    price = float(ticker['last'])
                    volume = float(ticker.get('quoteVolume', 0))
                    change = float(ticker.get('percentage', 0))
                    
                    if (0 < price <= max_price and 
                        volume >= min_volume and 
                        -10 <= change <= 20):
                        
                        candidates.append({
                            'symbol': symbol.split('/')[0],
                            'price': price,
                            'volume': volume,
                            'change': change
                        })
                        
                except:
                    continue
            
            candidates.sort(key=lambda x: x['volume'], reverse=True)
            candidates = candidates[:20]
            
            opportunities = []
            status_text.text("Analyse technique des meilleures pairs...")
            
            for candidate in candidates:
                try:
                    analysis = self.analyzer.analyze_symbol(candidate['symbol'])
                    if analysis and analysis['score'] >= min_score:
                        tokens_possible = budget/candidate['price']
                        
                        opportunities.append({
                            **candidate,
                            'score': analysis['score'],
                            'rsi': analysis.get('rsi', 50),
                            'signal': analysis['signal'],
                            'tokens_possible': tokens_possible,
                            'investment': min(budget, tokens_possible * candidate['price'])
                        })
                        
                except Exception as e:
                    continue
                    
            status_text.empty()
            return sorted(opportunities, key=lambda x: x['score'], reverse=True)
            def _analyze_candles(self, df):
                """Analyse les bougies et retourne le nombre de vertes consécutives"""
                try:
                    last_candles = df.tail(5)
                    green_count = 0
                    
                    for _, candle in last_candles.iterrows():
                        if candle['close'] > candle['open']:
                            green_count += 1
                        else:
                            break
                            
                    return green_count
                except Exception as e:
                    return 0

        except Exception as e:
            st.error(f"Erreur lors de la recherche : {str(e)}")
            return []

    def _show_opportunities(self, opportunities: List[Dict], budget: float):
        for opp in opportunities:
            with st.expander(f"💫 {opp['symbol']} - Score: {opp['score']:.2f}"):
                # Métriques principales - Style 1
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix", f"${opp['price']:.8f}", f"{opp['change']:+.2f}%")
                with col2:
                    st.metric("RSI", f"{opp['rsi']:.1f}")
                with col3:
                    st.metric("Distance Support", f"{opp.get('distance_to_support', 0):.1f}%")

                # Section Confirmations - Style 1
                st.markdown("#### ✅ Confirmations")
                conf_col1, conf_col2 = st.columns(2)
                with conf_col1:
                    st.write(f"• {opp.get('green_candles', 0)} bougies vertes consécutives")
                    st.write(f"• Volume {opp.get('volume_trend', 'N/A')}")
                with conf_col2:
                    st.write(f"• Score technique: {opp['score']:.2f}")
                    st.write(f"• RSI: {opp['rsi']:.1f}")

                # Niveaux suggérés - Style 2
                st.markdown("### 📊 Position Suggérée")
                stop_loss = opp['price'] * 0.985
                target_1 = opp['price'] * 1.03
                target_2 = opp['price'] * 1.05
                
                level_col1, level_col2, level_col3 = st.columns(3)
                with level_col1:
                    st.write("🛡️ Stop Loss", f"${stop_loss:.8f}")
                with level_col2:
                    st.write("🎯 Target 1", f"${target_1:.8f}")
                with level_col3:
                    st.write("🎯 Target 2", f"${target_2:.8f}")

                # Informations investissement
                st.markdown(f"""
                💰 **Position suggérée:**
                - Montant: ${opp['investment']:.2f} USDT
                - Tokens: {opp['tokens_possible']:.2f}
                - R/R Ratio: {((target_1 - opp['price']) / (opp['price'] - stop_loss)):.2f}
                """)

                # Bouton de préparation trade
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
                    st.success(f"✅ Trade préparé pour {opp['symbol']}! Allez dans Portfolio pour finaliser.")

                st.markdown("---")

    def _show_top_volumes(self, max_price: float):
        """Affiche les cryptos avec les plus gros volumes même si elles ne correspondent pas aux critères"""
        st.markdown("### 📊 Top Volumes (pour information)")
        try:
            tickers = self.exchange.exchange.fetch_tickers()
            volumes = []
            
            for symbol, ticker in tickers.items():
                if not symbol.endswith('/USDT'):
                    continue
                    
                try:
                    # Vérification et conversion sécurisée des valeurs
                    price = ticker.get('last')
                    volume = ticker.get('quoteVolume')
                    change = ticker.get('percentage')
                    
                    if price is not None and volume is not None and change is not None:
                        price = float(price)
                        if price <= max_price:
                            volumes.append({
                                'symbol': symbol.split('/')[0],
                                'price': price,
                                'volume': float(volume),
                                'change': float(change)
                            })
                except (TypeError, ValueError):
                    continue
            
            volumes.sort(key=lambda x: x['volume'], reverse=True)
            
            if volumes:
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.markdown("**Symbole**")
                with col2:
                    st.markdown("**Informations**")
                
                for v in volumes[:5]:  # Afficher les 5 plus gros volumes
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        st.markdown(f"**{v['symbol']}**")
                    with col2:
                        st.markdown(
                            f"Prix: ${v['price']:.4f} | "
                            f"Vol: ${v['volume']/1e6:.1f}M | "
                            f"Var: {v['change']:+.2f}%"
                        )
                        
            else:
                st.info("Aucune crypto ne correspond aux critères de prix actuels")
                        
        except Exception as e:
            st.warning(f"Note: Certaines données de volume peuvent être incomplètes")