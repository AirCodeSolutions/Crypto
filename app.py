import streamlit as st
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import ta

# Configuration de la page
st.set_page_config(
    page_title="Analyseur Crypto Avancé",
    page_icon="📊",
    layout="wide"
)

# Initialisation de l'exchange
@st.cache_resource
def get_exchange():
    return ccxt.kucoin({
        'adjustForTimeDifference': True,
        'timeout': 30000,
    })

exchange = get_exchange()

# Fonction pour vérifier et formater le symbol
def get_valid_symbol(symbol):
    try:
        markets = exchange.load_markets()
        # Essayer d'abord avec USDT
        if f"{symbol}/USDT" in markets:
            return f"{symbol}/USDT"
        # Sinon essayer avec USDT:USDT
        elif f"{symbol}/USDT:USDT" in markets:
            return f"{symbol}/USDT:USDT"
        return None
    except Exception as e:
        st.error(f"Erreur lors de la vérification du symbol: {str(e)}")
        return None

# Sidebar pour la navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Analyse en Direct", "Top Performances", "Opportunités Court Terme", "Analyse Historique", "Guide & Explications"]
)

# Function pour calculer le RSI
def calculate_rsi(df, periods=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
def calculate_support_resistance(df, window=20):
    """Calcule les niveaux de support et résistance"""
    rolling_min = df['low'].rolling(window=window).min()
    rolling_max = df['high'].rolling(window=window).max()
    return rolling_min.iloc[-1], rolling_max.iloc[-1]

def detect_divergence(price_data, rsi_data, window=14):
    """Détecte les divergences prix/RSI"""
    price_peaks = pd.Series(price_data).rolling(window, center=True).apply(
        lambda x: 1 if x.iloc[len(x)//2] == max(x) else (
            -1 if x.iloc[len(x)//2] == min(x) else 0
        )
    )
    rsi_peaks = pd.Series(rsi_data).rolling(window, center=True).apply(
        lambda x: 1 if x.iloc[len(x)//2] == max(x) else (
            -1 if x.iloc[len(x)//2] == min(x) else 0
        )
    )
    return price_peaks != rsi_peaks


# Page principale - Analyse en Direct
if page == "Analyse en Direct":
    st.title("📈 Analyse en Direct")
    
    # Input pour ajouter une crypto
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC, ETH)", "").upper()

    # Liste des cryptos suivies
    if "tracked_coins" not in st.session_state:
        st.session_state.tracked_coins = set()

    # Boutons Ajouter/Supprimer
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ajouter à la liste de suivi"):
            if symbol and symbol not in st.session_state.tracked_coins:
                valid_symbol = get_valid_symbol(symbol)
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

    # Affichage des cryptos suivies
    if st.session_state.tracked_coins:
        st.subheader("Cryptos suivies")
        for coin in st.session_state.tracked_coins:
            valid_symbol = get_valid_symbol(coin)
            if valid_symbol:
                try:
                    # Analyse complète pour chaque crypto
                    ticker = exchange.fetch_ticker(valid_symbol)
                    ohlcv = exchange.fetch_ohlcv(valid_symbol, '1h', limit=100)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    
                    # Calcul des indicateurs
                    df['SMA20'] = df['close'].rolling(window=20).mean()
                    df['SMA50'] = df['close'].rolling(window=50).mean()
                    df['RSI'] = calculate_rsi(df)
                    
                    current_price = ticker['last']
                    sma20 = df['SMA20'].iloc[-1]
                    sma50 = df['SMA50'].iloc[-1]
                    rsi = df['RSI'].iloc[-1]
                    
                    # Détermination de la tendance et des recommandations
                    trend = "NEUTRE"
                    if sma20 > sma50:
                        trend = "HAUSSIÈRE"
                    elif sma20 < sma50:
                        trend = "BAISSIÈRE"
                        
                    recommendation = "CONSERVER"
                    timeframe = "MOYEN TERME"
                    
                    if rsi < 30 and trend == "HAUSSIÈRE":
                        recommendation = "ACHETER"
                        timeframe = "COURT TERME"
                    elif rsi > 70 and trend == "BAISSIÈRE":
                        recommendation = "VENDRE"
                        timeframe = "COURT TERME"
                    
                    # Affichage détaillé
                    st.markdown(f"### {coin}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Prix", f"{current_price:.8f} USDT")
                    with col2:
                        st.metric("RSI", f"{rsi:.2f}")
                    with col3:
                        st.metric("Tendance", trend)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Recommandation", recommendation)
                    with col2:
                        st.metric("Horizon", timeframe)
                    
                    # Graphiques
                    st.line_chart(df.set_index('timestamp')[['close', 'SMA20', 'SMA50']])
                    st.bar_chart(df.set_index('timestamp')['volume'])
                    
                    st.markdown("---")
                    
                except Exception as e:
                    st.error(f"Erreur pour {coin}: {str(e)}")
                
# Page Top Performances
elif page == "Top Performances":
    st.title("🏆 Top Performances")
    
    if st.button("Rafraîchir"):
        try:
            performances = []
            
            with st.spinner("Analyse des performances en cours..."):
                markets = exchange.load_markets()
                for symbol in markets:
                    if symbol.endswith('/USDT'):
                        try:
                            ticker = exchange.fetch_ticker(symbol)
                            if ticker['last'] <= 20:  # Filtre prix <= 20 USDT
                                ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=7)
                                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                                
                                volume_change = ((df['volume'].iloc[-1] / df['volume'].mean()) - 1) * 100
                                week_change = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
                                volatility = df['close'].pct_change().std() * 100
                                
                                performances.append({
                                    'symbol': symbol.replace('/USDT', ''),
                                    'price': ticker['last'],
                                    'change_24h': ticker['percentage'],
                                    'change_7d': week_change,
                                    'volume': ticker['quoteVolume'],
                                    'volume_change': volume_change,
                                    'volatility': volatility,
                                    'high_24h': ticker['high'],
                                    'low_24h': ticker['low']
                                })
                        except:
                            continue
                
                if performances:
                    # Tri par performance 24h
                    performances.sort(key=lambda x: x['change_24h'], reverse=True)
                    
                    # Statistiques globales
                    avg_change = sum(p['change_24h'] for p in performances) / len(performances)
                    avg_volume = sum(p['volume'] for p in performances) / len(performances)
                    
                    st.subheader("📊 Statistiques globales du marché")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Variation moyenne 24h", f"{avg_change:.2f}%")
                    with col2:
                        st.metric("Volume moyen", f"{avg_volume:,.0f} USDT")
                    
                    st.markdown("---")
                    
                    # Affichage détaillé pour chaque crypto
                    for p in performances:
                        st.subheader(f"📊 {p['symbol']}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Prix", f"{p['price']:.8f} USDT")
                        with col2:
                            st.metric("Variation 24h", f"{p['change_24h']:.2f}%", 
                                    delta=f"{p['change_7d']:.2f}% (7j)")
                        with col3:
                            volume_str = "{:,.0f}".format(p['volume']).replace(',', ' ')
                            st.metric("Volume", f"{volume_str} USDT",
                                    delta=f"{p['volume_change']:.2f}%")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            amplitude = ((p['high_24h'] - p['low_24h']) / p['low_24h']) * 100
                            st.metric("Amplitude 24h", f"{amplitude:.2f}%")
                        with col2:
                            st.metric("Volatilité", f"{p['volatility']:.2f}%")
                        
                        if p['change_24h'] > 5:
                            st.success("🚀 Fort momentum haussier")
                        elif p['change_24h'] < -5:
                            st.error("📉 Fort momentum baissier")
                        
                        if p['volume'] > avg_volume * 2:
                            st.info("💹 Volume exceptionnellement élevé")
                        
                        st.markdown("---")
                    
                    st.caption(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
                    
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

# la page "Opportunités Court Terme"
elif page == "Opportunités Court Terme":
    st.title("🎯 Opportunités Court Terme")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_var = st.number_input("Variation minimum (%)", value=1.0)
    with col2:
        min_vol = st.number_input("Volume minimum (USDT)", value=100000.0)
    with col3:
        min_score = st.slider("Score minimum", 0.0, 1.0, 0.6)
    
    if st.button("Rechercher"):
        try:
            markets = exchange.load_markets()
            opportunities = []
            
            progress = st.progress(0)
            st.write("Analyse avancée en cours... Veuillez patienter.")
            
            usdt_markets = [s for s in markets if '/USDT' in s]
            total = len(usdt_markets)
            count = 0
            
            for symbol in usdt_markets:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    if ticker['last'] <= 20 and ticker['quoteVolume'] >= min_vol:
                        # Récupération des données sur plusieurs timeframes
                        ohlcv_15m = exchange.fetch_ohlcv(symbol, '15m', limit=96)
                        ohlcv_1h = exchange.fetch_ohlcv(symbol, '1h', limit=24)
                        
                        df_15m = pd.DataFrame(ohlcv_15m, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_1h = pd.DataFrame(ohlcv_1h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        
                        # Calculs avancés
                        support, resistance = calculate_support_resistance(df_15m)
                        momentum_score = calculate_momentum_score(df_15m)
                        market_sentiment = get_market_sentiment(symbol, exchange)
                        volume_trend = analyze_volume_profile(df_15m)
                        reversal_signals = detect_trend_reversal(df_15m)
                        
                        # Score global
                        total_score = (momentum_score + market_sentiment + (volume_trend/2)) / 3
                        
                        if total_score >= min_score:
                            opportunities.append({
                                'symbol': symbol.split('/')[0],
                                'price': ticker['last'],
                                'score': total_score,
                                'support': support,
                                'resistance': resistance,
                                'signals': reversal_signals,
                                'volume_trend': volume_trend,
                                'sentiment': market_sentiment,
                                'rsi': calculate_rsi(df_15m).iloc[-1]
                            })
                            
                except Exception as e:
                    continue
                
                count += 1
                progress.progress(count / total)
            
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            for op in opportunities:
                st.markdown(f"## {op['symbol']} - Score: {op['score']:.2f}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix", f"{op['price']:.8f} USDT")
                with col2:
                    st.metric("Support", f"{op['support']:.8f}")
                with col3:
                    st.metric("Résistance", f"{op['resistance']:.8f}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("RSI", f"{op['rsi']:.2f}")
                with col2:
                    st.metric("Sentiment", f"{op['sentiment']:.2f}")
                with col3:
                    st.metric("Volume Trend", f"{op['volume_trend']:.2f}x")
                
                if op['signals']:
                    st.info("🔄 Signaux de retournement détectés: " + ", ".join(op['signals']))
                
                # Analyse des risques
                risk_reward = (op['resistance'] - op['price']) / (op['price'] - op['support'])
                if risk_reward > 2:
                    st.success(f"✅ Bon ratio risque/récompense: {risk_reward:.2f}")
                else:
                    st.warning(f"⚠️ Ratio risque/récompense faible: {risk_reward:.2f}")
                
                st.markdown("---")
            
            st.caption(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
        
# Page Guide & Explications
elif page == "Guide & Explications":
    st.title("📚 Guide de Trading Crypto Avancé")
    
    st.markdown("""
    ## 1. Indicateurs Techniques Avancés
    
    ### RSI (Relative Strength Index)
    - Indicateur de momentum oscillant entre 0 et 100
    - RSI > 70 : Suracheté (signal de vente potentiel)
    - RSI < 30 : Survendu (signal d'achat potentiel)
    
    ### Divergences
    - **Divergence classique bearish** : Prix fait un plus haut mais RSI fait un plus bas
    - **Divergence classique bullish** : Prix fait un plus bas mais RSI fait un plus haut
    - Signal puissant de retournement potentiel de tendance
    
    ### Support et Résistance
    - **Support** : Niveau de prix où les acheteurs reprennent historiquement le contrôle
    - **Résistance** : Niveau de prix où les vendeurs reprennent historiquement le contrôle
    - Plus le niveau est testé, plus il est significatif
    
    ## 2. Analyse Multi-Timeframes
    
    ### Importance des timeframes
    - **15 minutes** : Pour les entrées précises
    - **1 heure** : Pour confirmer la tendance
    - **4 heures** : Pour le contexte global
    - La concordance entre timeframes renforce le signal
    
    ## 3. Profil Volumétrique
    
    ### Volume Spread Analysis (VSA)
    - **Volume croissant + prix montant** = Tendance forte
    - **Volume décroissant + prix montant** = Attention possible retournement
    - **Volume explosif** = Possible épuisement de la tendance
    
    ### Patterns de Volume
    - **Accumulation** : Volume élevé sans mouvement de prix significatif
    - **Distribution** : Volume élevé en haut de tendance
    - **Climax** : Volume extraordinairement élevé (possible retournement)
    
    ## 4. Score de Trading
    
    ### Composantes du score
    - **Momentum** : Force de la tendance (MACD, RSI, Stochastique)
    - **Sentiment** : Analyse multi-timeframes des EMA
    - **Volume** : Qualité du volume récent
    - Score > 0.7 = Signal fort
    
    ## 5. Ratio Risque/Récompense
    
    ### Calcul et Utilisation
    - **Calcul** : (Objectif - Prix d'entrée) / (Prix d'entrée - Stop Loss)
    - **Minimum recommandé** : 2:1
    - **Optimal** : 3:1 ou plus
    
    ## 6. Patterns de Retournement
    
    ### Chandeliers Japonais
    - **Doji** : Indécision du marché
    - **Hammer** : Possible retournement haussier
    - **Shooting Star** : Possible retournement baissier
    - **Engulfing** : Pattern de retournement puissant
    
    ## 7. Gestion du Risque Avancée
    
    ### Position Sizing
    - Ne jamais risquer plus de 1-2% du capital par trade
    - Adapter la taille selon le score de l'opportunité
    - Plus le score est élevé, plus la position peut être importante
    
    ### Stops Dynamiques
    - Placer le stop initial sous le dernier support
    - Déplacer le stop en fonction des nouveaux supports
    - Utiliser les EMA comme stops trailing
    
    ## 8. Psychologie du Trading
    
    ### Discipline
    - Suivre strictement sa stratégie
    - Ne pas être influencé par les émotions
    - Tenir un journal de trading détaillé
    
    ### Patience
    - Attendre les setups de haute qualité (score > 0.7)
    - Ne pas forcer les trades
    - La préservation du capital est prioritaire
    """)

    st.info("💡 Pro Tip: Utilisez ce guide comme une checklist avant chaque trade!")

# Page Analyse Historique
else:  # Analyse Historique
    st.title("📊 Analyse Historique")
    
    symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC, ETH)", "").upper()
    
    if symbol:
        timeframes = {
            "1 jour": "1d",
            "1 semaine": "1w",
            "1 mois": "1M",
            "3 mois": "3M",
            "6 mois": "6M"
        }
        
        selected_timeframe = st.selectbox("Période d'analyse", list(timeframes.keys()))
        
        if st.button("Analyser"):
            valid_symbol = get_valid_symbol(symbol)
            if valid_symbol:
                try:
                    with st.spinner("Analyse en cours..."):
                        # Récupération des données
                        ohlcv = exchange.fetch_ohlcv(valid_symbol, timeframes[selected_timeframe])
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        
                        # Calculs avancés
                        df['returns'] = df['close'].pct_change()
                        df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(365) * 100
                        df['MA20'] = df['close'].rolling(window=20).mean()
                        df['MA50'] = df['close'].rolling(window=50).mean()
                        df['RSI'] = calculate_rsi(df)
                        
                        # Statistiques principales
                        start_price = df['open'].iloc[0]
                        end_price = df['close'].iloc[-1]
                        total_return = ((end_price - start_price) / start_price) * 100
                        
                        st.subheader("📈 Métriques clés")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Rendement total", f"{total_return:.2f}%")
                        with col2:
                            st.metric("Plus haut", f"{df['high'].max():.8f}")
                        with col3:
                            st.metric("Plus bas", f"{df['low'].min():.8f}")
                        
                        # Statistiques détaillées
                        st.subheader("📊 Statistiques détaillées")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Volatilité moyenne", f"{df['volatility'].mean():.2f}%")
                        with col2:
                            st.metric("Volume moyen", f"{df['volume'].mean():,.0f}")
                        with col3:
                            st.metric("RSI actuel", f"{df['RSI'].iloc[-1]:.2f}")
                        with col4:
                            drawdown = ((df['close'].cummax() - df['close']) / df['close'].cummax() * 100)
                            st.metric("Drawdown max", f"{drawdown.max():.2f}%")
                        
                        # Graphiques
                        st.subheader("Évolution du prix et moyennes mobiles")
                        fig_price = pd.DataFrame({
                            'Prix': df['close'],
                            'MA20': df['MA20'],
                            'MA50': df['MA50']
                        }, index=df['timestamp'])
                        st.line_chart(fig_price)
                        
                        # Volume et volatilité
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Volume des échanges")
                            st.bar_chart(df.set_index('timestamp')['volume'])
                        with col2:
                            st.subheader("Volatilité")
                            st.line_chart(df.set_index('timestamp')['volatility'])
                        
                        # Analyse des moments propices
                        st.subheader("🕒 Analyse temporelle")
                        df['hour'] = df['timestamp'].dt.hour
                        df['day'] = df['timestamp'].dt.day_name()
                        
                        # Meilleurs moments pour trader
                        vol_by_hour = df.groupby('hour')['volume'].mean()
                        best_hours = vol_by_hour.nlargest(5)
                        
                        st.write("Heures les plus actives:")
                        for hour, vol in best_hours.items():
                            st.write(f"• {hour}h00: {vol:,.0f} USDT en moyenne")
                        
                        # Patterns et tendances
                        st.subheader("🔄 Patterns et tendances")
                        trend_strength = abs(total_return) / df['volatility'].mean()
                        
                        if trend_strength > 2:
                            if total_return > 0:
                                st.success("🚀 Tendance haussière forte")
                            else:
                                st.error("📉 Tendance baissière forte")
                        else:
                            st.info("↔️ Pas de tendance claire - Market ranging")
                        
                        st.caption(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
                        
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse: {str(e)}")
            else:
                st.error(f"La crypto {symbol} n'est pas disponible sur KuCoin")
