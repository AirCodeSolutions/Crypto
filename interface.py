# pages.py
import streamlit as st
from datetime import datetime
import pandas as pd
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

class OpportunitiesPage:
    def __init__(self, exchange, ta_analyzer):
        self.exchange = exchange
        self.ta = ta_analyzer

    def render(self):
        st.title("🎯 Opportunités Court Terme")
        
        # Filtres
        self._display_filters()
        
        # Recherche d'opportunités
        if st.button("Rechercher"):
            self._search_opportunities()

    def _display_filters(self):
        col1, col2, col3 = st.columns(3)
        with col1:
            min_var = st.number_input("Variation minimum (%)", value=1.0)
        with col2:
            min_vol = st.number_input("Volume minimum (USDT)", value=100000.0)
        with col3:
            min_score = st.slider("Score minimum", 0.0, 1.0, 0.6)
        return min_var, min_vol, min_score

    def _search_opportunities(self):
        # [Code de recherche d'opportunités]
        pass

class HistoricalAnalysisPage:
    def __init__(self, exchange, ta_analyzer):
        self.exchange = exchange
        self.ta = ta_analyzer

    def render(self):
        st.title("📊 Analyse Historique")
        # [Code de l'analyse historique]
        pass

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
