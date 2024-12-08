# interface/pages/top_performance.py
import streamlit as st
import time
import ta
from typing import List, Dict
from ..components.guide_helper import GuideHelper

class TopPerformancePage:
    def __init__(self, exchange_service, analyzer_service):
        self.exchange = exchange_service
        self.analyzer = analyzer_service

    def render(self):
        st.title("🏆 Top Opportunités d'Achat")
        # Section Guides
        GuideHelper.show_indicator_help()
        GuideHelper.show_pattern_guide()
        GuideHelper.show_quick_guide()
        # Section configuration
        col1, col2 = st.columns(2)
        with col1:
            # Paramètres d'investissement
            st.subheader("💰 Paramètres d'Investissement")
            budget = st.number_input(
                "Budget disponible (USDT)",
                min_value=10.0,
                value=100.0,
                step=10.0,
                help="Votre budget total d'investissement"
            )
            
            max_price = st.number_input(
                "Prix maximum par crypto (USDT)",
                min_value=0.1,
                max_value=20.0,
                value=5.0,
                help="Prix unitaire maximum acceptable"
            )

        with col2:
            # Critères techniques
            st.subheader("📊 Critères Techniques")
            min_volume = st.number_input(
                "Volume minimum 24h (USDT)",
                min_value=10000.0,
                value=50000.0,
                step=10000.0,
                help="Volume minimum pour assurer la liquidité"
            )
            
            min_score = st.slider(
                "Score technique minimum",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                help="Score basé sur les indicateurs techniques (RSI, MACD, etc.)"
            )

        if st.button("🔍 Rechercher les Meilleures Opportunités"):
            with st.spinner("Analyse du marché en cours..."):
                opportunities = self._find_opportunities(budget, max_price, min_volume, min_score)
                self._display_opportunities(opportunities, budget)

    def _find_opportunities(self, budget: float, max_price: float, min_volume: float, min_score: float) -> List[Dict]:
        try:
            opportunities = []
            progress = st.progress(0)
            
            # Récupération de tous les symboles disponibles
            symbols = self.exchange.get_available_symbols()
            
            for i, symbol in enumerate(symbols):
                try:
                    # Récupération des données de base
                    ticker = self.exchange.get_ticker(symbol)
                    price = float(ticker['last'])
                    volume = float(ticker['quoteVolume'])

                    # Filtres préliminaires
                    if price <= max_price and volume >= min_volume:
                        # Analyse technique
                        df = self.exchange.get_ohlcv(symbol)
                        if df is not None and not df.empty:
                            analysis = self.analyzer.analyze_symbol(symbol)
                            
                            if analysis['score'] >= min_score:
                                max_tokens = min(budget/price, volume/price/10)  # Maximum 10% du volume
                                
                                opportunities.append({
                                    'symbol': symbol,
                                    'price': price,
                                    'volume_24h': volume,
                                    'change_24h': ticker['percentage'],
                                    'score': analysis['score'],
                                    'rsi': analysis['rsi'],
                                    'signal': analysis['signal'],
                                    'max_tokens': max_tokens,
                                    'suggested_investment': min(budget, max_tokens * price),
                                    'support_price': price * 0.985,  # Support estimé à -1.5%
                                    'target_price': price * 1.03    # Cible à +3%
                                })

                    # Mise à jour de la progression
                    progress.progress((i + 1) / len(symbols))
                    
                except Exception as e:
                    continue
                
                time.sleep(0.1)  # Rate limiting
            
            progress.empty()
            
            # Tri des opportunités
            return sorted(opportunities, 
                        key=lambda x: (x['score'], x['volume_24h']), 
                        reverse=True)
                        
        except Exception as e:
            st.error(f"Erreur lors de la recherche: {str(e)}")
            return []

    def _display_opportunities(self, opportunities: List[Dict], budget: float):
        if not opportunities:
            st.info("Aucune opportunité trouvée avec ces critères")
            return

        for opp in opportunities:
            with st.expander(f"💫 {opp['symbol']} - Score: {opp['score']:.2f}"):
                # Informations principales
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Prix", f"${opp['price']:.4f}", f"{opp['change_24h']:+.2f}%")
                with cols[1]:
                    st.metric("Volume 24h", f"${opp['volume_24h']/1e6:.1f}M")
                with cols[2]:
                    st.metric("RSI", f"{opp['rsi']:.1f}")
                with cols[3]:
                    st.metric("Signal", opp['signal'])

                # Position suggérée
                st.markdown("### 📊 Position Suggérée")
                position_cols = st.columns(3)
                with position_cols[0]:
                    st.write("💰 Investissement suggéré:", f"${opp['suggested_investment']:.2f}")
                with position_cols[1]:
                    st.write("🎯 Prix cible:", f"${opp['target_price']:.4f}")
                with position_cols[2]:
                    st.write("🛡️ Support:", f"${opp['support_price']:.4f}")

                # Calculateur de position
                if st.button("📝 Préparer l'ordre", key=f"prep_{opp['symbol']}"):
                    st.session_state['prepared_trade'] = {
                        'symbol': opp['symbol'],
                        'price': opp['price'],
                        'stop_loss': opp['support_price'],
                        'target_1': opp['target_price'],
                        'target_2': opp['price'] * 1.05,
                        'suggested_amount': opp['suggested_investment'],
                        'score': opp['score']
                    }
                    st.success("✅ Trade préparé! Allez dans Portfolio pour finaliser.")

                st.markdown("---")