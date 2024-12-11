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
                opportunities = self._get_best_opportunities(
                    max_price=max_price,
                    min_volume=min_volume,
                    min_score=min_score,
                    budget=budget,
                    timeframe=timeframe
                )
                
                # Séparation des résultats
                strict_results = []
                potential_results = []
                
                for opp in opportunities:
                    try:
                        # Vérification des critères avec get() et conversion explicite
                        is_strict = (
                            float(opp.get('score', 0)) >= min_score and
                            30 <= float(opp.get('rsi', 0)) <= 45 and
                            float(opp.get('green_candles', 0)) >= 3
                        )
                        if is_strict:
                            strict_results.append(opp)
                        else:
                            potential_results.append(opp)
                    except (ValueError, TypeError, AttributeError):
                        potential_results.append(opp)

                # Affichage des résultats
                st.session_state['strict_results'] = strict_results
                st.session_state['potential_results'] = potential_results
                
                strict_count = len(strict_results)
                potential_count = len(potential_results)

                if strict_count > 0:
                    st.success(f"✅ {strict_count} opportunité{'s' if strict_count > 1 else ''} correspond{'ent' if strict_count > 1 else ''} aux critères stricts")
                else:
                    st.warning("❌ Aucune opportunité ne correspond aux critères stricts")

                if potential_count > 0:
                    st.info(f"👀 {potential_count} opportunité{'s' if potential_count > 1 else ''} potentielle{'s' if potential_count > 1 else ''} à surveiller")

            st.session_state['show_sort'] = True

        # Affichage des résultats triés
        if st.session_state.get('show_sort', False):
            sort_by = st.selectbox("Trier par", ["Score", "Volume", "RSI"], key="sort_opportunities")
            
            def sort_function(x):
                try:
                    if sort_by == "Score":
                        return float(x.get('score', 0))
                    elif sort_by == "Volume":
                        return float(x.get('volume', 0))
                    else:  # RSI
                        return abs(float(x.get('rsi', 50)) - 40)
                except (ValueError, TypeError):
                    return 0
            
            # Affichage des opportunités strictes
            if st.session_state.get('strict_results'):
                st.markdown("### ✅ Opportunités Idéales")
                sorted_strict = sorted(st.session_state['strict_results'], key=sort_function, reverse=(sort_by != "RSI"))
                # Passage de la liste complète
                self._show_opportunities(sorted_strict, budget)

            # Affichage des opportunités potentielles
            if st.session_state.get('potential_results'):
                st.markdown("### 👀 Opportunités à Surveiller")
                sorted_potential = sorted(st.session_state['potential_results'], key=sort_function, reverse=(sort_by != "RSI"))
                # Passage de la liste complète
                self._show_opportunities(sorted_potential, budget)
        

    def _get_best_opportunities(self, max_price: float, min_volume: float, min_score: float, budget: float, timeframe: str = '1h'):
        try:
            # 1. Une seule requête pour tous les tickers
            all_tickers = self.exchange.exchange.fetch_tickers()
            opportunities = []
            
            # 2. Premier filtrage rapide
            filtered_pairs = []
            for symbol, ticker in all_tickers.items():
                if not symbol.endswith('/USDT'):
                    continue
                    
                try:
                    price = float(ticker['last'])
                    volume = float(ticker.get('quoteVolume', 0))
                    
                    if 0 < price <= max_price:  # On garde seulement le filtre de prix
                        filtered_pairs.append({
                            'symbol': symbol.split('/')[0],
                            'price': price,
                            'volume': volume,
                            'change': float(ticker.get('percentage', 0))
                        })
                except:
                    continue

            # 3. Trier par volume et prendre le top 20
            filtered_pairs.sort(key=lambda x: x['volume'], reverse=True)
            top_pairs = filtered_pairs[:20]

            # 4. Analyser uniquement le top 20
            for pair in top_pairs:
                try:
                    analysis = self.analyzer.analyze_symbol(pair['symbol'])
                    if analysis:
                        # Calcul du pourcentage haussier basé sur le nombre de bougies vertes
                        green_candles = analysis.get('green_candles', 0)
                        bullish_percentage = (green_candles / 5) * 100
                        pair.update({
                            'score': analysis.get('score', 0),
                            'rsi': analysis.get('rsi', 50),
                            'signal': analysis.get('signal', 'NEUTRAL'),
                            'tokens_possible': budget/pair['price'],
                            'investment': min(budget, (budget/pair['price']) * pair['price']),
                            'green_candles': green_candles,
                            'bullish_percentage': bullish_percentage  
                        })
                        opportunities.append(pair)
                except:
                    continue

            return opportunities

        except Exception as e:
            st.error(f"Erreur lors de la recherche : {str(e)}")
            return []
                    

    
    def _show_opportunities(self, opportunities: List[Dict], budget: float):
        for opp in opportunities:
            # Déterminer si c'est un bon moment pour acheter
            buy_conditions = {
            'rsi': 30 <= opp.get('rsi', 0) <= 70,  # Zone saine du RSI
            'score': opp.get('score', 0) >= 0.7,
            'volume': opp.get('volume', 0) >= 50000,  # Volume minimum
            'candles': opp.get('green_candles', 0) >= 3  # Au moins 3 bougies vertes sur 5
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
                
                # Analyse des Bougies
                st.markdown("### 🕯️ Analyse des Bougies")
                candle_col1, candle_col2 = st.columns(2)
                with candle_col1:
                     st.metric(
                        "Bougies vertes (5 dernières)", 
                        f"{opp['green_candles']}/5",
                        f"{opp['bullish_percentage']:.0f}% haussier"
                    )


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