# pages.py
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
import ta
from utils import get_valid_symbol, calculate_timeframe_data
from technical_analysis import SignalGenerator

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
            # Utilisation de la fonction importée
            valid_symbol = get_valid_symbol(self.exchange, coin)
            if valid_symbol:
                # Récupération des données
                ticker = self.exchange.fetch_ticker(valid_symbol)
                df = calculate_timeframe_data(self.exchange, valid_symbol, '1h', 100)
                
                if df is not None:
                    st.write(f"### {coin}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Prix",
                            f"${ticker['last']:,.2f}",
                            f"{ticker['percentage']:+.2f}%"
                        )
                    with col2:
                        st.metric(
                            "Volume 24h",
                            f"${ticker['quoteVolume']:,.0f}",
                            None
                        )
                    
                    # Vous pouvez ajouter ici plus d'analyses selon vos besoins
                    
        except Exception as e:
            st.error(f"Erreur pour {coin}: {str(e)}")

class PortfolioPage:
    def __init__(self, portfolio_manager):
        self.portfolio = portfolio_manager

    def render(self):
        st.title("💼 Gestion du Portefeuille")
        
        # Configuration du capital initial
        self._manage_capital()
        
        # Formulaire d'ajout de position
        self._add_position_form()
        
        # Affichage des positions actuelles
        self._display_current_positions()
        
        # Historique et statistiques
        self._display_history_and_stats()

    def _manage_capital(self):
        if st.session_state.portfolio['capital'] == 0:
            st.session_state.portfolio['capital'] = st.number_input(
                "Capital initial (USDT)",
                min_value=0.0,
                value=1000.0,
                step=100.0
            )
            st.session_state.portfolio['current_capital'] = st.session_state.portfolio['capital']

    def _add_position_form(self):
        with st.expander("➕ Ajouter une nouvelle position"):
            col1, col2 = st.columns(2)
            with col1:
                new_symbol = st.text_input("Symbole (ex: BTC)", "").upper()
                amount = st.number_input("Montant (USDT)", min_value=0.0, value=100.0)
                entry_price = st.number_input("Prix d'entrée", min_value=0.0, value=0.0)
            with col2:
                stop_loss = st.number_input("Stop Loss", min_value=0.0, value=0.0)
                target_1 = st.number_input("Target 1", min_value=0.0, value=0.0)
                target_2 = st.number_input("Target 2", min_value=0.0, value=0.0)
            
            if st.button("Ajouter la position"):
                self._handle_new_position(new_symbol, amount, entry_price, stop_loss, target_1, target_2)

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

    def _display_history_and_stats(self):
        st.subheader("📈 Historique et Statistiques")
        
        # Récupération des données
        summary = self.portfolio.get_portfolio_summary()
        history_df = self.portfolio.get_trade_history()
        
        # Affichage des statistiques globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Capital total",
                f"${summary['capital_actuel']:.2f}",
                f"{summary['performance']:.2f}%"
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
            history_df['Durée'] = history_df['duration'].astype(str)
            history_df['P&L'] = history_df['pnl'].map('{:,.2f}%'.format)
            
            # Sélection et renommage des colonnes à afficher
            display_df = history_df[[
                'symbol', 'entry_price', 'exit_price', 'pnl', 'Durée', 'reason'
            ]].rename(columns={
                'symbol': 'Symbole',
                'entry_price': 'Prix entrée',
                'exit_price': 'Prix sortie',
                'pnl': 'P&L',
                'reason': 'Raison'
            })
            
            st.dataframe(display_df)
        else:
            st.info("Aucun historique de trade disponible")
            
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
        st.sidebar.title("Navigation")
        page_name = st.sidebar.selectbox("Choisir une page", list(self.pages.keys()))
        
        # Rendu de la page sélectionnée
        self.pages[page_name].render()
