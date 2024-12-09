# interface/pages/top_performance.py
import streamlit as st
import time
from typing import List, Dict
from ..components.guide_helper import GuideHelper
from ..components.styles import MOBILE_STYLES
import logging

class TopPerformancePage:
    def __init__(self, exchange_service, analyzer_service):
        """Initialise la page avec les services nécessaires"""
        self.exchange = exchange_service
        self.analyzer = analyzer_service
        
    def render(self):
        # Appliquer les styles mobile en premier
        st.markdown(MOBILE_STYLES, unsafe_allow_html=True)
        st.title("🏆 Opportunités ")
        # Section Guides
        #GuideHelper.show_indicator_help()
        #GuideHelper.show_pattern_guide()
        #GuideHelper.show_quick_guide()
        GuideHelper.show_opportunites_guide()
        
        # Initialisation correcte des préférences utilisateur avec dict()
        if 'user_preferences' not in st.session_state:
            st.session_state['user_preferences'] = dict({
                'budget': 100.0,
                'max_price': 5.0,
                'min_volume': 50000.0,
                'min_score': 0.6,
                'timeframe': '1h'
            })
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💰 Paramètres d'Investissement")
            budget = st.number_input(
                "Budget disponible (USDT)",
                min_value=10.0,
                value=st.session_state['user_preferences']['budget'],
                step=10.0
            )
            
            max_price = st.number_input(
                "Prix maximum par crypto (USDT)",
                min_value=0.1,
                max_value=20.0,
                value=st.session_state['user_preferences']['max_price']
            )

            # Ajout de la sélection du timeframe
            col1, col2 = st.columns(2)
            with col1:
                timeframe = st.selectbox(
                    "Timeframe",
                    options=["5m", "15m", "1h", "4h"],
                    index=2,  # 1h par défaut
                    help="""
                    5m : Trading ultra court terme (très risqué)
                    15m : Trading intraday
                    1h : Recommandé pour débutants
                    4h : Trades plus sûrs mais moins fréquents
                    """
                )

        with col2:
            st.subheader("🛡️ Critères de Sécurité")
            min_volume = st.number_input(
                "Volume minimum 24h (USDT)",
                min_value=10000.0,
                value=st.session_state['user_preferences']['min_volume'],
                step=10000.0
            )
            
            min_score = st.slider(
                "Score minimum",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state['user_preferences']['min_score']
            )


        # Mise à jour des préférences
            st.session_state['user_preferences'].update({
                'budget': budget,
                'max_price': max_price,
                'min_volume': min_volume,
                'min_score': min_score,
                'timeframe': timeframe
            })

        if st.button("🔍 Rechercher des Opportunités"):
            with st.spinner("Analyse en cours..."):
                results = self._get_best_opportunities(
                    max_price=max_price,
                    min_volume=min_volume,
                    min_score=min_score,
                    budget=budget,
                    timeframe=timeframe
                )
                #if results:
                #    st.session_state['current_results'] = results
                #    st.session_state['show_sort'] = True
                #else:
                #    st.warning("Aucune opportunité ne correspond aux critères actuels.")
                #    st.session_state['show_sort'] = False

                # Affichage du résumé
                strict_results = []
                potential_results = []
                
                # Tri des résultats en deux catégories
                for opp in results:
                    if (opp.get('score', 0) >= min_score and 
                        30 <= opp.get('rsi', 0) <= 45 and 
                        opp.get('green_candles', 0) >= 3):
                        strict_results.append(opp)
                    else:
                        potential_results.append(opp)

                # Stockage dans session_state
                st.session_state['strict_results'] = strict_results
                st.session_state['potential_results'] = potential_results

                # Affichage du résumé
                strict_count = len(strict_results)
                potential_count = len(potential_results)
                
                if strict_count > 0:
                    st.success(f"🎯 {strict_count} opportunité{'s' if strict_count > 1 else ''} correspond{'ent' if strict_count > 1 else ''} à tous les critères")
                else:
                    st.warning("Aucune opportunité ne correspond à tous les critères")

                if potential_count > 0:
                    st.info(f"👀 {potential_count} opportunité{'s' if potential_count > 1 else ''} à surveiller (ne correspond{'ent' if potential_count > 1 else ''} pas à tous les critères)")

                st.session_state['show_sort'] = True

            # Affichage des résultats et du tri
        if st.session_state.get('show_sort', False):
            sort_by = st.selectbox(
                "Trier par",
                ["Score", "Volume", "RSI"],
                key="sort_opportunities"
            )

            # Fonction de tri
            def get_sort_key(x):
                if sort_by == "Score":
                    return float(x.get('score', 0))
                elif sort_by == "Volume":
                    return float(x.get('volume', 0))
                else:  # RSI
                    return abs(float(x.get('rsi', 50)) - 40)

            # Affichage des opportunités strictes
            if st.session_state.get('strict_results'):
                st.markdown("### ✅ Opportunités Idéales")
                sorted_strict = sorted(
                    st.session_state['strict_results'],
                    key=get_sort_key,
                    reverse=(sort_by != "RSI")
                )
                for opp in sorted_strict:
                    self._show_opportunities(opp, budget)

            # Affichage des opportunités potentielles
            if st.session_state.get('potential_results'):
                st.markdown("### 👀 Opportunités à Surveiller")
                sorted_potential = sorted(
                    st.session_state['potential_results'],
                    key=get_sort_key,
                    reverse=(sort_by != "RSI")
                )
                for opp in sorted_potential:
                    self._show_opportunities(opp, budget)
        

    def _get_best_opportunities(self, max_price: float, min_volume: float, min_score: float, budget: float, timeframe: str = '1h') -> List[Dict]:
        try:
            # 1. Une seule requête pour tous les tickers
            all_tickers = self.exchange.exchange.fetch_tickers()

            # 2. Filtrage rapide et création des opportunités en une passe
            opportunities = []
            for symbol, ticker in all_tickers.items():
                try:
                    # Vérifier si c'est une paire USDT valide
                    if not symbol.endswith('/USDT'):
                        continue

                    price = float(ticker['last'])
                    volume = float(ticker.get('quoteVolume', 0))
                    change = float(ticker.get('percentage', 0))

                    # Filtres de base rapides
                    if not (0 < price <= max_price and volume >= min_volume):
                        continue

                    # Calculs simples sans appels API
                    tokens_possible = budget/price
                    gain_potentiel = tokens_possible * (price * 0.03)

                    opportunities.append({
                        'symbol': symbol.split('/')[0],
                        'price': price,
                        'volume': volume,
                        'change': change,
                        'tokens_possible': tokens_possible,
                        'investment': min(budget, tokens_possible * price),
                        'gain_potentiel': gain_potentiel
                    })

                except Exception as e:
                    continue

            # 3. Tri par volume et limitation aux 10 meilleurs
            opportunities.sort(key=lambda x: x['volume'], reverse=True)
            top_opportunities = opportunities[:10]

            # 4. Analyse technique uniquement sur le top 10
            #final_opportunities = []
            #for opp in top_opportunities:
            #    try:
            #        analysis = self.analyzer.analyze_symbol(opp['symbol'])
            #        if analysis:
            #            opp.update({
            #                'score': analysis['score'],
            #                'rsi': analysis.get('rsi', 50),
            #                'signal': analysis['signal']
            #            })
            #            final_opportunities.append(opp)
            #    except:
            #        continue

            #return final_opportunities

            strict_opportunities = []
            potential_opportunities = []

            for opp in opportunities:
                # Vérification des critères stricts
                meets_criteria = (
                    opp['score'] >= min_score and 
                    30 <= opp.get('rsi', 0) <= 45 and 
                    opp.get('green_candles', 0) >= 3
                )

                if meets_criteria:
                    strict_opportunities.append(opp)
                else:
                    potential_opportunities.append(opp)

            return {
                'strict': strict_opportunities,
                'potential': potential_opportunities
            }


            

        except Exception as e:
            st.error(f"Erreur lors de la recherche : {str(e)}")
            return []
    
    def _show_opportunities(self, opportunities: List[Dict], budget: float):
        for opp in opportunities:
            # Déterminer si c'est un bon moment pour acheter
            buy_conditions = {
                'rsi': 30 <= opp['rsi'] <= 45,
                'score': opp['score'] >= 0.7,
                'volume': opp.get('volume_trend') == 'croissant',
                'candles': opp.get('green_candles', 0) >= 3
            }
            
            should_buy = all(buy_conditions.values())
            
            header_color = "🟢" if should_buy else "🔴"
            with st.expander(f"{header_color} {opp['symbol']} - Score: {opp['score']:.2f}"):
                st.markdown("""---""")
                
                # Section 1: Prix et Indicateurs Principaux
                st.markdown("### 📊 Indicateurs Principaux")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                    "Prix",
                    f"${opp['price']:.8f}",
                    f"{opp['change']:+.2f}%" if opp.get('change') else None
            )
                with col2:
                    # RSI dans les indicateurs principaux
                    rsi = opp.get('rsi', 0)
                    rsi_color = "green" if 30 <= rsi <= 70 else "red"
                    st.markdown(f"RSI: <span style='color: {rsi_color}'>{rsi:.1f}</span>", 
                            unsafe_allow_html=True)
                with col3:
                    # Affichage du volume en millions
                    volume = opp.get('volume', 0)
                    st.metric("Volume 24h", f"${volume/1e6:.1f}M")
                
                # Section 2: Analyse Technique
                st.markdown("""---""")
                st.markdown("### 🔍 Analyse Technique")
                # Configuration des indicateurs avec leurs conditions
                indicators = [
                    {
                        'name': 'Score technique',
                        'value': opp['score'],
                        'format': '.2f',
                        'condition': opp['score'] >= 0.7
                    },
                    {
                        'name': 'RSI',
                        'value': opp.get('rsi', 0),
                        'format': '.1f',
                        'condition': 30 <= opp.get('rsi', 0) <= 70
                    },
                    {
                        'name': 'Bougies vertes',
                        'value': opp.get('green_candles', 0),
                        'format': 'd',
                        'condition': opp.get('green_candles', 0) >= 3
                    },
                    {
                        'name': 'Volume',
                        'value': f"${opp.get('volume', 0)/1e6:.1f}M",
                        'format': 's',
                        'condition': opp.get('volume', 0) >= 50000
                    }
                ]

                # Affichage des indicateurs
                for ind in indicators:
                    color = "green" if ind['condition'] else "red"
                    symbol = "✓" if ind['condition'] else "✗"
                    if ind['format'] == 's':  # Pour les strings formatées (comme le volume)
                        value = ind['value']
                    else:
                        value = f"{ind['value']:{ind['format']}}"
                        
                    st.markdown(
                        f"<span style='color: {color}'>{symbol} {ind['name']}: {value}</span>", 
                        unsafe_allow_html=True
                    )
                
                # Dans la section après les indicateurs
                if opp['score'] >= 0.5:  # Montrer seulement si le score n'est pas trop mauvais
                    st.markdown("### 💰 Position Suggérée")
                    pos_col1, pos_col2 = st.columns(2)
                    with pos_col1:
                        st.metric(
                            "Investissement suggéré", 
                            f"${opp['investment']:.2f}",
                            f"{opp['tokens_possible']:.2f} tokens"
                        )
                    with pos_col2:
                        perte_max = opp['investment'] * 0.015  # Stop loss à -1.5%
                        gain_max = opp['investment'] * 0.05   # Target à +5%
                        st.metric(
                            "Gain potentiel",
                            f"+${gain_max:.2f}",
                            f"Perte max: -${perte_max:.2f}"
                        )

                # Message d'avertissement si nécessaire
                if not all(ind['condition'] for ind in indicators):
                    st.warning("⚠️ Certains indicateurs ne sont pas optimaux")

                # Section 3: Niveaux de Trading
                if should_buy:
                    st.markdown("""---""")
                    st.markdown("### 🎯 Niveaux de Trading Suggérés")
                    
                    stop_loss = opp['price'] * 0.985
                    target_1 = opp['price'] * 1.03
                    target_2 = opp['price'] * 1.05
                    
                    level_col1, level_col2, level_col3 = st.columns(3)
                    with level_col1:
                        st.markdown("**🛡️ Stop Loss**")
                        st.markdown(f"${stop_loss:.8f}")
                    with level_col2:
                        st.markdown("**🎯 Target 1 (+3%)**")
                        st.markdown(f"${target_1:.8f}")
                    with level_col3:
                        st.markdown("**🎯 Target 2 (+5%)**")
                        st.markdown(f"${target_2:.8f}")

                    # Position suggérée
                    st.markdown("""---""")
                    st.markdown("### 💰 Position Suggérée")
                    pos_col1, pos_col2 = st.columns(2)
                    with pos_col1:
                        st.markdown(f"""
                        - Investissement: **${opp['investment']:.2f}** USDT
                        - Nombre de tokens: **{opp['tokens_possible']:.2f}**
                        """)
                    with pos_col2:
                        st.markdown(f"""
                        - Perte max: **${(opp['investment'] * 0.015):.2f}** USDT
                        - Gain potentiel: **${(opp['investment'] * 0.05):.2f}** USDT
                        """)
                    # Dans une section dédiée pour les gains potentiels
                    if opp['price'] > 0:  # Vérification de sécurité
                        investment = opp['investment']
                        gain_3 = investment * 0.03  # Gain à +3%
                        gain_5 = investment * 0.05  # Gain à +5%
                                
                        st.markdown("#### 💰 Gains Potentiels")
                        gain_col1, gain_col2 = st.columns(2)
                        with gain_col1:
                            st.metric("À +3%", f"${gain_3:.2f}", f"{((gain_3/investment)*100):.1f}%")
                        with gain_col2:
                            st.metric("À +5%", f"${gain_5:.2f}", f"{((gain_5/investment)*100):.1f}%")

                    # Bouton de préparation
                    st.button(
                        "📝 Préparer l'ordre",
                        key=f"prep_{opp['symbol']}",
                        on_click=self._prepare_trade,
                        args=(opp, stop_loss, target_1, target_2)
                    )

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