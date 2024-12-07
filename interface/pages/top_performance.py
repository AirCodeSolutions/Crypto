# interface/pages/top_performance.py
import streamlit as st
import pandas as pd
from typing import Dict, List
# Dans TopPerformancePage et autres pages
from interface.components.guide_helper import GuideHelper

class TopPerformancePage:
    def __init__(self, exchange_service, analyzer_service=None):
        self.exchange = exchange_service
        self.analyzer = analyzer_service  # Pour les analyses techniques
        
    def render(self):
        st.title("🏆 Top Performances")

        # Ajouter l'aide en haut
        GuideHelper.show_indicator_help()
        GuideHelper.show_quick_guide()
        # Section paramètres d'investissement
        with st.expander("💰 Paramètres d'investissement", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                budget = st.number_input(
                    "Budget disponible (USDT)",
                    min_value=10.0,
                    value=100.0,
                    step=10.0,
                    help="Montant que vous souhaitez investir"
                )
            with col2:
                risk_percent = st.slider(
                    "Risque par position (%)",
                    min_value=1,
                    max_value=10,
                    value=2,
                    help="Pourcentage du budget par position"
                )

        # Filtres de recherche améliorés
        col1, col2, col3 = st.columns(3)
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
        with col3:
            min_score = st.slider(
                "Score minimum",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                help="Score technique minimum (0-1)"
            )

        if st.button("🔄 Rechercher"):
            with st.spinner("Recherche des meilleures opportunités..."):
                try:
                    markets = self.exchange.get_available_symbols()
                    opportunities = []
                    
                    progress_bar = st.progress(0)
                    for i, symbol in enumerate(markets):
                        try:
                            ticker = self.exchange.get_ticker(symbol)
                            if ticker['quoteVolume'] >= min_volume:
                                # Analyse technique
                                analysis = self.analyzer.analyze_symbol(symbol)
                                
                                if analysis and analysis['score'] >= min_score:
                                    # Calcul du nombre de tokens achetables
                                    position_size = budget * (risk_percent / 100)
                                    tokens = position_size / ticker['last']
                                    
                                    opportunities.append({
                                        'symbol': symbol,
                                        'price': ticker['last'],
                                        'change': ticker['percentage'],
                                        'volume': ticker['quoteVolume'],
                                        'score': analysis['score'],
                                        'rsi': analysis['rsi'],
                                        'signal': analysis['signal'],
                                        'tokens_possible': tokens,
                                        'investment_needed': position_size
                                    })
                            
                            progress_bar.progress((i + 1) / len(markets))
                            
                        except Exception:
                            continue

                    # Tri des meilleures opportunités
                    opportunities.sort(key=lambda x: (x['score'], abs(x['change'])), reverse=True)
                    top_opportunities = opportunities[:10]

                    # Affichage des résultats
                    if top_opportunities:
                        for opp in top_opportunities:
                            with st.container():
                                st.markdown(f"### {opp['symbol']}")
                                
                                # Métriques principales
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric(
                                        "Prix",
                                        f"${opp['price']:,.4f}",
                                        f"{opp['change']:+.2f}%"
                                    )
                                with col2:
                                    st.metric(
                                        "Score",
                                        f"{opp['score']:.2f}",
                                        help="Score > 0.7 recommandé"
                                    )
                                with col3:
                                    st.metric(
                                        "RSI",
                                        f"{opp['rsi']:.1f}",
                                        help="RSI 30-70: Zone optimale"
                                    )
                                with col4:
                                    st.metric(
                                        "Volume 24h",
                                        f"${opp['volume']/1e6:.1f}M"
                                    )
                                
                                # Informations d'investissement
                                info_cols = st.columns(2)
                                with info_cols[0]:
                                    st.info(f"💰 Investissement suggéré: ${opp['investment_needed']:,.2f}")
                                with info_cols[1]:
                                    st.info(f"🔢 Tokens possibles: {opp['tokens_possible']:.4f}")
                                
                                # Signal et actions
                                action_cols = st.columns(2)
                                with action_cols[0]:
                                    signal_color = "green" if opp['signal'] in ['STRONG_BUY', 'BUY'] else "red"
                                    st.markdown(f"Signal: <span style='color:{signal_color}'>{opp['signal']}</span>", unsafe_allow_html=True)
                                with action_cols[1]:
                                    if st.button("📊 Analyser en détail", key=f"analyze_{opp['symbol']}"):
                                        st.session_state.selected_crypto = opp['symbol']
                                
                                st.markdown("---")
                    else:
                        st.info("Aucune opportunité ne correspond à vos critères")
                        
                except Exception as e:
                    st.error(f"Erreur lors de la recherche : {str(e)}")