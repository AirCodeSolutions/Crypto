# pages.py
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
import ta
from utils import (
    get_valid_symbol, 
    calculate_timeframe_data, 
    format_number,
    get_exchange  # Ajout de cet import
)
from technical_analysis import SignalGenerator, TechnicalAnalysis  # Ajout de TechnicalAnalysis
from portfolio_management import PortfolioManager  # Ajout de cet import


class LiveAnalysisPage:
    def __init__(self, exchange, ta_analyzer, portfolio_manager):
        self.exchange = exchange
        self.ta = ta_analyzer
        self.portfolio = portfolio_manager
        
    def render(self):
        st.title("📈 Analyse en Direct")
        
        # Input pour ajouter une crypto
        col1, col2 = st.columns([3, 1])
        with col1:
            symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC, ETH)", "").upper()

        # Gestion des cryptos suivies
        self._manage_tracked_coins(symbol)
        
        # Affichage des analyses
        if st.session_state.tracked_coins:
            self._display_tracked_coins()

    def _manage_tracked_coins(self, symbol):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ajouter à la liste de suivi"):
                if symbol and symbol not in st.session_state.tracked_coins:
                    valid_symbol = get_valid_symbol(self.exchange, symbol)
                    if valid_symbol:
                        st.session_state.tracked_coins.add(symbol)
                        st.success(f"{symbol} ajouté à la liste de suivi")
                    else:
                        st.error(f"{symbol} n'est pas une crypto valide")

        with col2:
            if st.button("Supprimer de la liste"):
                if symbol in st.session_state.tracked_coins:
                    st.session_state.tracked_coins.remove(symbol)
                    st.info(f"{symbol} retiré de la liste de suivi")
    

    def _display_tracked_coins(self):
        st.subheader("Cryptos suivies")
        for coin in st.session_state.tracked_coins:
            self._analyze_and_display_coin(coin)

    def _analyze_and_display_coin(self, coin):
        try:
            valid_symbol = get_valid_symbol(self.exchange, coin)
            if valid_symbol:
                ticker = self.exchange.fetch_ticker(valid_symbol)
                df = calculate_timeframe_data(self.exchange, valid_symbol, '1h', 100)
                
                if df is not None:
                    # ... code existant ...

                    # Bouton pour ajouter au portfolio si signal d'achat
                    if signals['action'] == 'BUY':
                        if st.button("📝 Préparer un ordre", key=f"prepare_{coin}"):
                            # Calcul des niveaux suggérés
                            risk_percentage = 1.5  # 1.5% de stop loss par défaut
                            stop_loss = ticker['last'] * (1 - risk_percentage/100)
                            risk_amount = ticker['last'] - stop_loss
                            target_1 = ticker['last'] + (risk_amount * 2)  # R/R 1:2
                            target_2 = ticker['last'] + (risk_amount * 3)  # R/R 1:3

                            # Stockage des informations dans la session
                            st.session_state['prepared_trade'] = {
                                'symbol': coin,
                                'price': ticker['last'],
                                'stop_loss': stop_loss,
                                'target_1': target_1,
                                'target_2': target_2,
                                'support': support,
                                'resistance': resistance,
                                'score': score
                            }
                            
                            st.success(f"✅ Trade préparé pour {coin}! Allez dans Portfolio pour finaliser l'ordre.")
                        
class PortfolioPage:
    def __init__(self, portfolio_manager):
        self.portfolio = portfolio_manager

    def render(self):
        st.title("💼 Gestion du Portefeuille")


        with st.expander("⚙️ Paramètres du Portfolio"):
            col1, col2 = st.columns(2)
            with col1:
                # Configuration du capital initial avec une clé unique
                initial_capital = st.session_state.portfolio['capital']
                new_capital = st.number_input(
                    "Capital (USDT)",
                    min_value=0.0,
                    value=float(initial_capital) if initial_capital > 0 else 1000.0,
                    step=100.0,
                    key="capital_input_settings"  # Ajout d'une clé unique
                )
                
                # Si le capital a été modifié
                if new_capital != initial_capital:
                    # Vérifier s'il y a des positions ouvertes
                    if st.session_state.portfolio['positions']:
                        st.warning("⚠️ Impossible de modifier le capital avec des positions ouvertes")
                    else:
                        # Mise à jour du capital
                        st.session_state.portfolio['capital'] = new_capital
                        st.session_state.portfolio['current_capital'] = new_capital
                        
                        # Réinitialisation des performances
                        st.session_state.portfolio['performance'] = {
                            'total_trades': 0,
                            'winning_trades': 0,
                            'total_profit': 0,
                            'max_drawdown': 0
                        }
                        
                        st.success(f"💰 Capital mis à jour à {new_capital} USDT")
                        st.rerun()
                        
            with col2:
                # Bouton de réinitialisation
                if st.button("🗑️ Réinitialiser Portfolio", type="secondary"):
                    if st.session_state.portfolio['positions']:
                        # Demande de confirmation si des positions sont ouvertes
                        if st.warning("⚠️ Attention: Cette action supprimera toutes vos positions et votre historique. Êtes-vous sûr?"):
                            if st.button("✅ Confirmer la réinitialisation"):
                                self._reset_portfolio()
                    else:
                        # Réinitialisation directe s'il n'y a pas de positions ouvertes
                        self._reset_portfolio()

                        
                
        # Formulaire d'ajout de position
        self._add_position_form()
        
        # Affichage des positions actuelles
        self._display_current_positions()
        
        # Historique et statistiques
        self._display_history_and_stats()
        # Vérifier les trades préparés
        self._check_prepared_trade()
    
            
    def _reset_portfolio(self):
        """Réinitialise le portfolio à son état initial"""
        st.session_state.portfolio = {
            'positions': {},
            'history': [],
            'capital': 0,
            'current_capital': 0,
            'performance': {
                'total_trades': 0,
                'winning_trades': 0,
                'total_profit': 0,
                'max_drawdown': 0
            }
        }
        st.success("✨ Portfolio réinitialisé avec succès!")
        st.rerun()
        
    def _add_position_form(self):
        with st.expander("➕ Ajouter une nouvelle position"):
            # Première ligne : Symbole et Prix d'entrée
            col1, col2 = st.columns(2)
            with col1:
                new_symbol = st.text_input("Symbole (ex: BTC)", "").upper()
                amount = st.number_input("Montant (USDT)", min_value=0.0, value=100.0)
            with col2:
                entry_price = st.number_input("Prix d'entrée", min_value=0.0, value=0.0, format="%.8f")
            
            # Calculateur d'aide
            st.markdown("---")
            st.markdown("### 🎯 Calculateur de niveaux")
            
            col1, col2 = st.columns(2)
            with col1:
                risk_percentage = st.slider(
                    "Risque acceptable (%)", 
                    min_value=0.5, 
                    max_value=5.0, 
                    value=1.5,
                    step=0.5,
                    help="Pourcentage de perte maximale acceptable"
                )
            with col2:
                risk_reward = st.slider(
                    "Ratio Risque/Récompense", 
                    min_value=1.5, 
                    max_value=5.0, 
                    value=2.0,
                    step=0.5,
                    help="Ratio entre profit potentiel et risque"
                )

            if entry_price > 0:
                # Calcul des niveaux suggérés
                stop_loss = entry_price * (1 - risk_percentage/100)
                risk_amount = entry_price - stop_loss
                target_1 = entry_price + (risk_amount * risk_reward)
                target_2 = entry_price + (risk_amount * (risk_reward * 1.5))

                # Affichage des niveaux calculés
                st.markdown("#### Niveaux suggérés:")
                col1, col2, col3 = st.columns(3)
                with col1:
                    suggested_sl = st.metric(
                        "Stop Loss suggéré",
                        f"{stop_loss:.8f}",
                        f"{-risk_percentage:.1f}%"
                    )
                with col2:
                    suggested_t1 = st.metric(
                        "Target 1 suggéré",
                        f"{target_1:.8f}",
                        f"+{risk_percentage * risk_reward:.1f}%"
                    )
                with col3:
                    suggested_t2 = st.metric(
                        "Target 2 suggéré",
                        f"{target_2:.8f}",
                        f"+{risk_percentage * risk_reward * 1.5:.1f}%"
                    )

                # Champs pour les niveaux réels
                st.markdown("---")
                st.markdown("### 📊 Niveaux de la position")
                col1, col2, col3 = st.columns(3)
                with col1:
                    stop_loss = st.number_input(
                        "Stop Loss", 
                        min_value=0.0, 
                        value=float(stop_loss), 
                        format="%.8f",
                        help="Niveau de stop loss en USDT"
                    )
                with col2:
                    target_1 = st.number_input(
                        "Target 1", 
                        min_value=0.0, 
                        value=float(target_1), 
                        format="%.8f",
                        help="Premier objectif de profit"
                    )
                with col3:
                    target_2 = st.number_input(
                        "Target 2", 
                        min_value=0.0, 
                        value=float(target_2), 
                        format="%.8f",
                        help="Second objectif de profit"
                    )

                # Calcul des métriques de la position
                if amount > 0:
                    potential_loss = (stop_loss - entry_price) * (amount / entry_price)
                    potential_profit_1 = (target_1 - entry_price) * (amount / entry_price)
                    potential_profit_2 = (target_2 - entry_price) * (amount / entry_price)

                    st.markdown("#### Analyse de la position")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Perte maximale",
                            f"{potential_loss:.2f} USDT",
                            f"{(potential_loss/amount)*100:.1f}% du capital"
                        )
                    with col2:
                        st.metric(
                            "Profit potentiel (T2)",
                            f"{potential_profit_2:.2f} USDT",
                            f"{(potential_profit_2/amount)*100:.1f}% du capital"
                        )

                # Bouton d'ajout
                st.markdown("---")
                if st.button("Ajouter la position", type="primary"):
                    self._handle_new_position(new_symbol, amount, entry_price, stop_loss, target_1, target_2)

            else:
                st.info("Entrez un prix d'entrée pour voir les niveaux suggérés")
                
    def _handle_new_position(self, symbol, amount, entry_price, stop_loss, target_1, target_2):
        try:
            # Validation des entrées
            if not all([symbol, amount > 0, entry_price > 0, stop_loss > 0, target_1 > 0, target_2 > 0]):
                st.error("Tous les champs doivent être remplis avec des valeurs valides")
                return

            if stop_loss >= entry_price:
                st.error("Le stop loss doit être inférieur au prix d'entrée")
                return

            if target_1 <= entry_price or target_2 <= target_1:
                st.error("Les targets doivent être supérieurs au prix d'entrée et Target 2 > Target 1")
                return

            # Ajout de la position
            success, message = self.portfolio.add_position(symbol, amount, entry_price, stop_loss, target_1, target_2)
            
            if success:
                st.success(message)
            else:
                st.error(message)
                
        except Exception as e:
            st.error(f"Erreur lors de l'ajout de la position : {str(e)}")

    def _display_current_positions(self):
        st.subheader("📊 Positions Ouvertes")
        
        # Récupération des positions
        positions_df = self.portfolio.get_open_positions()
        
        if positions_df.empty:
            st.info("Aucune position ouverte")
            return
            
        # Mise à jour des positions
        self.portfolio.update_positions()
        
        # Affichage des positions
        for _, position in positions_df.iterrows():
            with st.expander(f"{position['symbol']} - {position['pnl']:.2f}%"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Prix actuel",
                        f"${position['current_price']:.4f}",
                        f"{position['pnl']:.2f}%"
                    )
                    
                with col2:
                    st.metric("Montant", f"{position['amount']:.4f}")
                    
                with col3:
                    st.metric("Valeur", f"${position['amount'] * position['current_price']:.2f}")
                
                # Niveaux importants
                st.markdown("### Niveaux")
                levels_col1, levels_col2, levels_col3 = st.columns(3)
                
                with levels_col1:
                    st.write("Stop Loss:", f"${position['stop_loss']:.4f}")
                    
                with levels_col2:
                    st.write("Target 1:", f"${position['target_1']:.4f}")
                    
                with levels_col3:
                    st.write("Target 2:", f"${position['target_2']:.4f}")
                
                # Bouton de fermeture
                if st.button("Fermer la position", key=f"close_{position['symbol']}"):
                    self.portfolio.close_position(
                        position['symbol'],
                        position['current_price'],
                        "Fermeture manuelle"
                    )
                    st.success(f"Position {position['symbol']} fermée")
                    st.rerun()

    def _add_risk_management_section(self):
        with st.expander("⚠️ Gestion des Risques"):
            st.markdown("""
            ### Règles de gestion des risques
            
            1. **Position Size** 🎯
            - Maximum 1-2% du capital par trade
            - Stop loss toujours défini
            - Ratio risque/récompense minimum de 1:2
            
            2. **Diversification** 📊
            - Maximum 20% du capital en crypto
            - Pas plus de 4-5 positions simultanées
            - Varier les types de cryptos
            
            3. **Périodes de Trading** ⏰
            - Éviter les annonces importantes
            - Préférer les périodes de forte liquidité
            - Pas de FOMO sur les pics de volatilité
            """)
            
            # Calculs de gestion des risques
            capital = st.session_state.portfolio['current_capital']
            col1, col2 = st.columns(2)
            
            with col1:
                risk_percentage = st.slider(
                    "% de risque par trade",
                    min_value=0.5,
                    max_value=2.0,
                    value=1.0,
                    step=0.1,
                    help="Pourcentage du capital à risquer par trade"
                )
                
                max_risk_amount = capital * (risk_percentage/100)
                st.metric(
                    "Risque maximum par trade",
                    f"${max_risk_amount:.2f}",
                    help="Perte maximale acceptable par position"
                )
                
            with col2:
                max_positions = st.slider(
                    "Nombre maximum de positions",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="Nombre maximum de positions simultanées"
                )
                
                position_size = capital / max_positions
                st.metric(
                    "Taille suggérée par position",
                    f"${position_size:.2f}",
                    help="Montant suggéré pour chaque position"
                )
    
    def _display_history_and_stats(self):
        st.subheader("📈 Historique et Statistiques")
        
        # Récupération des données
        summary = self.portfolio.get_portfolio_summary()
        history_df = self.portfolio.get_trade_history()
        
        # Calcul de la performance si elle n'existe pas dans le summary
        if 'performance' not in summary:
            if summary['capital_initial'] > 0:
                performance = ((summary['capital_actuel'] / summary['capital_initial']) - 1) * 100
            else:
                performance = 0.0
        else:
            performance = summary['performance']
        
        # Affichage des statistiques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Capital total",
                f"${summary['capital_actuel']:.2f}",
                f"{performance:.2f}%"
            )
            
        with col2:
            if summary['nombre_trades'] > 0:
                win_rate = f"{summary['win_rate']:.1f}%"
            else:
                win_rate = "N/A"
            st.metric("Win Rate", win_rate)
            
        with col3:
            st.metric("Nombre de trades", summary['nombre_trades'])
            
        with col4:
            st.metric("Drawdown Max", f"{summary['max_drawdown']:.2f}%")
    
        # Historique des trades
        if not history_df.empty:
            st.subheader("Historique des trades")
            
            # Formatage des colonnes pour l'affichage
            if 'duration' in history_df.columns:
                history_df['Durée'] = history_df['duration'].astype(str)
            else:
                history_df['Durée'] = 'N/A'

            if 'pnl' in history_df.columns:
                history_df['P&L'] = history_df['pnl'].map('{:,.2f}%'.format)
            else:
                history_df['P&L'] = 'N/A'
            
            # Sélection et renommage des colonnes à afficher
            display_columns = [col for col in ['symbol', 'entry_price', 'exit_price', 'pnl', 'Durée', 'reason'] 
                             if col in history_df.columns]
            
            column_names = {
                'symbol': 'Symbole',
                'entry_price': 'Prix entrée',
                'exit_price': 'Prix sortie',
                'pnl': 'P&L',
                'reason': 'Raison'
            }
            
            display_df = history_df[display_columns].rename(columns=column_names)
            
            st.dataframe(display_df)
        else:
            st.info("Aucun historique de trade disponible")

    def _check_prepared_trade(self):
        if 'prepared_trade' in st.session_state:
            trade = st.session_state['prepared_trade']
            
            st.info("💫 Trade préparé disponible!")
            with st.expander("📝 Détails du trade préparé"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Symbole", trade['symbol'])
                    st.metric("Prix actuel", f"${trade['price']:.8f}")
                    st.metric("Score technique", f"{trade['score']:.2f}")
                with col2:
                    st.metric("Support", f"${trade['support']:.8f}")
                    st.metric("Résistance", f"${trade['resistance']:.8f}")
                
                # Calcul de la taille suggérée de position
                capital = st.session_state.portfolio['current_capital']
                suggested_risk = capital * 0.01  # 1% du capital
                position_size = (suggested_risk / (trade['price'] - trade['stop_loss'])) * trade['price']
                
                st.markdown("### 📊 Position suggérée")
                col1, col2 = st.columns(2)
                with col1:
                    amount = st.number_input(
                        "Montant (USDT)",
                        min_value=0.0,
                        value=min(position_size, capital * 0.1),  # Max 10% du capital
                        step=10.0
                    )
                with col2:
                    risk_percent = (amount * (trade['price'] - trade['stop_loss'])) / capital * 100
                    st.metric("Risque", f"{risk_percent:.2f}%")
                
                if st.button("✅ Créer la position"):
                    self._handle_new_position(
                        trade['symbol'],
                        amount,
                        trade['price'],
                        trade['stop_loss'],
                        trade['target_1'],
                        trade['target_2']
                    )
                    del st.session_state['prepared_trade']
                    st.rerun()
                
        
class OpportunitiesPage:
    def __init__(self, exchange, ta_analyzer):
        self.exchange = exchange
        self.ta = ta_analyzer

    def render(self):
        st.title("🎯 Opportunités Court Terme")
        
        # Filtres de recherche
        col1, col2, col3 = st.columns(3)
        with col1:
            min_var = st.number_input("Variation minimum (%)", value=1.0)
        with col2:
            min_vol = st.number_input("Volume minimum (USDT)", value=100000.0)
        with col3:
            min_score = st.slider("Score minimum", 0.0, 1.0, 0.6)

        # Options supplémentaires
        col1, col2 = st.columns(2)
        with col1:
            timeframe = st.selectbox(
                "Timeframe",
                ["5m", "15m", "1h", "4h"],
                index=2
            )
        with col2:
            max_price = st.number_input("Prix maximum (USDT)", value=20.0)

        if st.button("🔍 Rechercher des opportunités"):
            self._search_opportunities(min_var, min_vol, min_score, timeframe, max_price)

    def _search_opportunities(self, min_var, min_vol, min_score, timeframe, max_price):
        try:
            markets = self.exchange.load_markets()
            usdt_pairs = [symbol for symbol in markets.keys() if symbol.endswith('USDT')]
            
            opportunities = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, symbol in enumerate(usdt_pairs):
                try:
                    status_text.text(f"Analyse de {symbol}...")
                    ticker = self.exchange.fetch_ticker(symbol)
                    
                    # Filtres primaires
                    if (ticker['quoteVolume'] >= min_vol and 
                        abs(ticker['percentage']) >= min_var and 
                        ticker['last'] <= max_price):
                        
                        # Analyse technique
                        df = calculate_timeframe_data(self.exchange, symbol, timeframe, 100)
                        if df is not None:
                            signal_gen = SignalGenerator(df, ticker['last'])
                            score = signal_gen.calculate_opportunity_score()
                            signals = signal_gen.generate_trading_signals()
                            
                            if score >= min_score:
                                opportunities.append({
                                    'symbol': symbol.replace('/USDT', ''),
                                    'price': ticker['last'],
                                    'change': ticker['percentage'],
                                    'volume': ticker['quoteVolume'],
                                    'score': score,
                                    'signal': signals['action'],
                                    'reasons': signals['reasons']
                                })
                    
                    progress_bar.progress((i + 1) / len(usdt_pairs))
                    
                except Exception as e:
                    continue
            
            progress_bar.empty()
            status_text.empty()
            
            if opportunities:
                opportunities.sort(key=lambda x: x['score'], reverse=True)
                
                for opp in opportunities:
                    with st.expander(f"{opp['symbol']} - Score: {opp['score']:.2f}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Prix", f"${opp['price']:.4f}", f"{opp['change']:+.2f}%")
                        with col2:
                            st.metric("Volume 24h", f"${opp['volume']/1e6:.1f}M", None)
                        
                        if opp['signal']:
                            signal_color = "🟢" if opp['signal'] == 'BUY' else "🔴"
                            st.write(f"{signal_color} Signal: {opp['signal']}")
                            for reason in opp['reasons']:
                                st.write(f"• {reason}")
            else:
                st.info("Aucune opportunité trouvée avec les critères actuels")
                
        except Exception as e:
            st.error(f"Erreur lors de la recherche : {str(e)}")
# Dans interface.py, modifiez la classe HistoricalAnalysisPage

class HistoricalAnalysisPage:
    def __init__(self, exchange, ta_analyzer):
        self.exchange = exchange
        self.ta = ta_analyzer

    def render(self):
        st.title("📊 Analyse Historique")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            symbol = st.text_input("Entrez le symbole (ex: BTC, ETH)", "").upper()
        with col2:
            timeframe = st.selectbox(
                "Timeframe",
                ["1h", "4h", "1d"],
                index=0
            )
        with col3:
            lookback = st.slider(
                "Jours d'historique",
                min_value=7,
                max_value=90,
                value=30
            )

        if symbol:
            valid_symbol = get_valid_symbol(self.exchange, symbol)
            if valid_symbol:
                if st.button("📊 Analyser"):
                    with st.spinner(f"Analyse de {symbol} en cours..."):
                        self._perform_historical_analysis(valid_symbol, timeframe, lookback)
            else:
                st.error(f"Symbole {symbol} non trouvé")

    def _perform_historical_analysis(self, symbol, timeframe, lookback):
        try:
            # Récupération des données
            df = calculate_timeframe_data(self.exchange, symbol, timeframe, lookback * 24)
            
            if df is not None and not df.empty:
                # Calcul des indicateurs
                df['rsi'] = self.ta.calculate_rsi(df)
                df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
                df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
                df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
                df['macd'] = ta.trend.macd_diff(df['close'])
                
                # Prix actuel et variation
                current_price = df['close'].iloc[-1]
                price_change = ((current_price / df['close'].iloc[0] - 1) * 100)
                
                # Affichage des métriques principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix actuel", f"${current_price:.4f}", 
                             f"{price_change:+.2f}%")
                with col2:
                    st.metric("Plus haut", f"${df['high'].max():.4f}")
                with col3:
                    st.metric("Plus bas", f"${df['low'].min():.4f}")
                
                # Graphique des prix
                st.subheader("Graphique des prix")
                fig = go.Figure()
                
                # Chandelier
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name="Prix"
                ))
                
                # EMAs
                fig.add_trace(go.Scatter(x=df.index, y=df['ema9'], 
                                       name="EMA 9", line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=df.index, y=df['ema20'], 
                                       name="EMA 20", line=dict(color='orange')))
                fig.add_trace(go.Scatter(x=df.index, y=df['ema50'], 
                                       name="EMA 50", line=dict(color='red')))
                
                fig.update_layout(
                    title=f"Analyse de {symbol}",
                    yaxis_title="Prix (USDT)",
                    xaxis_title="Date",
                    height=600,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # RSI
                st.subheader("RSI")
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df['rsi'], name="RSI"))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(
                    height=200,
                    template="plotly_dark",
                    yaxis_title="RSI"
                )
                st.plotly_chart(fig_rsi, use_container_width=True)
                
                # MACD
                st.subheader("MACD")
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=df.index, y=df['macd'], name="MACD"))
                fig_macd.add_hline(y=0, line_dash="dash", line_color="gray")
                fig_macd.update_layout(
                    height=200,
                    template="plotly_dark",
                    yaxis_title="MACD"
                )
                st.plotly_chart(fig_macd, use_container_width=True)
                
                # Niveaux clés
                support, resistance = self.ta.calculate_support_resistance(df)
                st.subheader("Niveaux clés")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Support", f"${support:.4f}")
                with col2:
                    st.metric("Résistance", f"${resistance:.4f}")
                
                # Analyse du signal actuel
                signal_gen = SignalGenerator(df, current_price)
                signals = signal_gen.generate_trading_signals()
                
                # Affichage du signal
                st.subheader("Signal actuel")
                if signals['action']:
                    signal_color = "🟢" if signals['action'] == 'BUY' else "🔴"
                    st.write(f"{signal_color} {signals['action']}")
                    for reason in signals['reasons']:
                        st.write(f"• {reason}")
                else:
                    st.info("Pas de signal clair pour le moment")
                
            else:
                st.error("Aucune donnée disponible pour cette période")
                
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {str(e)}")
            st.exception(e)  # Affiche les détails de l'erreur en mode développement

            
class TopPerformancePage:
    def __init__(self, exchange, ta_analyzer):
        self.exchange = exchange
        self.ta = ta_analyzer

    def render(self):
        st.title("🏆 Top Performances (Prix ≤ 20 USDT)")
        
        # Filtres de base
        col1, col2 = st.columns(2)
        with col1:
            min_volume = st.number_input(
                "Volume minimum (USDT)",
                min_value=10000.0,
                value=100000.0,
                step=10000.0
            )
        with col2:
            min_score = st.slider(
                "Score minimum pour achat",
                0.0, 1.0, 0.6,
                help="Score technique minimum pour considérer un achat"
            )

        if st.button("🔄 Actualiser les données"):
            with st.spinner("Analyse en cours..."):
                self._analyze_and_display_opportunities(min_volume, min_score)

    def _analyze_and_display_opportunities(self, min_volume, min_score):
        try:
            # Récupération des marchés USDT
            markets = self.exchange.load_markets()
            usdt_pairs = [symbol for symbol in markets.keys() if symbol.endswith('USDT')]
            
            opportunities = []
            progress_bar = st.progress(0)
            
            for i, symbol in enumerate(usdt_pairs):
                try:
                    ticker = self.exchange.fetch_ticker(symbol)
                    price = ticker['last']
                    
                    # Filtre sur le prix et le volume
                    if price <= 20 and ticker['quoteVolume'] >= min_volume:
                        # Récupération des données pour l'analyse
                        df = calculate_timeframe_data(self.exchange, symbol, '1h', 100)
                        if df is not None:
                            # Analyse technique
                            rsi = self.ta.calculate_rsi(df).iloc[-1]
                            market_sentiment = self.ta.get_market_sentiment(df)
                            volume_profile = self.ta.analyze_volume_profile(df)
                            
                            # Génération des signaux
                            signal_gen = SignalGenerator(df, price)
                            score = signal_gen.calculate_opportunity_score()
                            signals = signal_gen.generate_trading_signals()

                            opportunities.append({
                                'symbol': symbol.replace('/USDT', ''),
                                'price': price,
                                'change_24h': ticker['percentage'],
                                'volume': ticker['quoteVolume'],
                                'rsi': rsi,
                                'sentiment': market_sentiment,
                                'volume_trend': volume_profile,
                                'score': score,
                                'signal': signals['action'],
                                'reasons': signals['reasons'] if signals['action'] == 'BUY' else []
                            })
                
                    # Mise à jour de la progression
                    progress_bar.progress((i + 1) / len(usdt_pairs))
                    
                except Exception as e:
                    continue
            
            progress_bar.empty()
            
            # Affichage des résultats
            if opportunities:
                # Tri par score technique
                opportunities.sort(key=lambda x: (x['score'], x['change_24h']), reverse=True)
                
                # Séparation en deux catégories
                buy_signals = []
                watch_list = []
                
                for opp in opportunities:
                    if opp['score'] >= min_score and opp['signal'] == 'BUY':
                        buy_signals.append(opp)
                    else:
                        watch_list.append(opp)
                
                # Affichage des signaux d'achat
                if buy_signals:
                    st.success("### 🎯 Signaux d'achat détectés")
                    for opp in buy_signals:
                        with st.expander(f"💰 {opp['symbol']} - Score: {opp['score']:.2f}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Prix", f"${opp['price']:.4f}", f"{opp['change_24h']:+.2f}%")
                            with col2:
                                st.metric("RSI", f"{opp['rsi']:.1f}", None)
                            with col3:
                                st.metric("Volume 24h", f"${opp['volume']/1e6:.1f}M", None)
                            
                            st.markdown("#### Raisons d'achat:")
                            for reason in opp['reasons']:
                                st.write(f"✅ {reason}")
                
                # Affichage de la watchlist
                st.markdown("### 👀 Watch List")
                cols = st.columns(3)
                for i, opp in enumerate(watch_list):
                    with cols[i % 3]:
                        st.metric(
                            opp['symbol'],
                            f"${opp['price']:.4f}",
                            f"{opp['change_24h']:+.2f}%",
                            help=f"Score: {opp['score']:.2f}\nRSI: {opp['rsi']:.1f}"
                        )
            else:
                st.warning("Aucune opportunité trouvée avec les critères actuels")
                
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {str(e)}")


class GuidePage:
    def render(self):
        st.title("📚 Guide de Trading Crypto Avancé")
        # [Code du guide]
        pass

# Main App
class CryptoAnalyzerApp:
    def __init__(self):
        self.exchange = get_exchange()
        self.ta = TechnicalAnalysis()
        self.portfolio = PortfolioManager(self.exchange)
        
        self.pages = {
            "Analyse en Direct": LiveAnalysisPage(self.exchange, self.ta, self.portfolio),
            "Portefeuille": PortfolioPage(self.portfolio),
            "Top Performances": TopPerformancePage(self.exchange, self.ta),
            "Opportunités Court Terme": OpportunitiesPage(self.exchange, self.ta),
            "Analyse Historique": HistoricalAnalysisPage(self.exchange, self.ta),
            "Guide & Explications": GuidePage()
        }

    def run(self):
        from utils import format_number  # Ajout ici aussi pour être sûr
        
        st.sidebar.title("Navigation")
        page_name = st.sidebar.selectbox("Choisir une page", list(self.pages.keys()))
        
        # Informations générales dans le sidebar
        if st.session_state.portfolio['capital'] > 0:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 💰 Portfolio")
            st.sidebar.metric(
                "Capital actuel",
                f"{format_number(st.session_state.portfolio['current_capital'])} USDT",
                f"{((st.session_state.portfolio['current_capital'] / st.session_state.portfolio['capital']) - 1) * 100:.2f}%"
            )
            
        # Rendu de la page sélectionnée
        try:
            self.pages[page_name].render()
        except Exception as e:
            st.error(f"Erreur lors du chargement de la page: {str(e)}")
            
