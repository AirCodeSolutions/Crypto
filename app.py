import streamlit as st
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Configuration de la page
st.set_page_config(
    page_title="Analyseur Crypto",
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

# Page Opportunités Court Terme
elif page == "Opportunités Court Terme":
    st.title("🎯 Opportunités Court Terme")
    
    col1, col2 = st.columns(2)
    with col1:
        min_var = st.number_input("Variation minimum (%)", value=1.0)
    with col2:
        min_vol = st.number_input("Volume minimum (USDT)", value=100000.0)
    
    if st.button("Rechercher"):
        try:
            markets = exchange.load_markets()
            opportunities = []
            
            progress = st.progress(0)
            st.write("Analyse en cours... Veuillez patienter.")
            
            usdt_markets = [s for s in markets if '/USDT' in s]
            total = len(usdt_markets)
            count = 0
            
            for symbol in usdt_markets:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    if ticker['last'] <= 20 and ticker['quoteVolume'] >= min_vol:  # Filtre prix <= 20 USDT
                        ohlcv_short = exchange.fetch_ohlcv(symbol, '15m', limit=24)
                        ohlcv_7h = exchange.fetch_ohlcv(symbol, '15m', limit=28)
                        ohlcv_24h = exchange.fetch_ohlcv(symbol, '1h', limit=24)
                        
                        df_short = pd.DataFrame(ohlcv_short, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_7h = pd.DataFrame(ohlcv_7h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_24h = pd.DataFrame(ohlcv_24h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        
                        price_change_1h = ((df_short['close'].iloc[-1] - df_short['close'].iloc[-4]) / df_short['close'].iloc[-4]) * 100
                        price_change_7h = ((df_7h['close'].iloc[-1] - df_7h['close'].iloc[0]) / df_7h['close'].iloc[0]) * 100
                        price_change_24h = ((df_24h['close'].iloc[-1] - df_24h['close'].iloc[0]) / df_24h['close'].iloc[0]) * 100
                        
                        if abs(price_change_1h) >= min_var:
                            vol_change = (df_short['volume'].iloc[-1] / df_short['volume'].mean()) * 100
                            rsi = calculate_rsi(df_short, periods=6).iloc[-1]
                            
                            signal = "🟢 ACHAT" if price_change_1h > 0 else "🔴 VENTE"
                            if (signal.startswith("🟢") and rsi < 70) or (signal.startswith("🔴") and rsi > 30):
                                opportunities.append({
                                    'symbol': symbol.split('/')[0],
                                    'price': ticker['last'],
                                    'price_change_1h': price_change_1h,
                                    'price_change_7h': price_change_7h,
                                    'price_change_24h': price_change_24h,
                                    'volume_change': vol_change,
                                    'rsi': rsi,
                                    'signal': signal,
                                    'volume': ticker['quoteVolume']
                                })
                except Exception as e:
                    print(f"Erreur pour {symbol}: {str(e)}")
                    continue
                
                count += 1
                progress.progress(count / total)
            
            opportunities.sort(key=lambda x: abs(x['price_change_1h']), reverse=True)
            
            for op in opportunities:
                st.markdown(f"## {op['symbol']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix", f"{op['price']:.8f} USDT")
                with col2:
                    direction = "↗️" if op['price_change_1h'] > 0 else "↘️"
                    st.metric("Variation 1h", f"{op['price_change_1h']:.2f}% {direction}")
                with col3:
                    st.metric("Volume 24h", f"{op['volume']:,.0f} USDT")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("RSI", f"{op['rsi']:.2f}")
                with col2:
                    st.metric("Variation 7h", f"{op['price_change_7h']:.2f}%")
                with col3:
                    st.metric("Variation 24h", f"{op['price_change_24h']:.2f}%")
                with col4:
                    st.metric("Variation volume", f"{op['volume_change']:.2f}%")
                
                st.markdown(f"**Signal:** {op['signal']}")
                
                # Analyse supplémentaire
                if op['signal'].startswith("🟢"):
                    if op['rsi'] < 30:
                        st.success("📊 Opportunité d'achat forte (RSI survendu)")
                    else:
                        st.info("📈 Momentum haussier détecté")
                else:
                    if op['rsi'] > 70:
                        st.error("📊 Opportunité de vente forte (RSI suracheté)")
                    else:
                        st.warning("📉 Momentum baissier détecté")
                
                changes = [op['price_change_1h'], op['price_change_7h'], op['price_change_24h']]
                if all(x > 0 for x in changes):
                    st.success("🚀 Tendance haussière sur toutes les périodes")
                elif all(x < 0 for x in changes):
                    st.error("📉 Tendance baissière sur toutes les périodes")
                else:
                    st.info("↔️ Tendance mixte")
                
                st.markdown("---")
            
            st.caption(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
        
# Page Guide & Explications
elif page == "Guide & Explications":
    st.title("📚 Guide de Trading Crypto")
    
    st.markdown("""
    ## 1. RSI (Relative Strength Index)
    
    ### Qu'est-ce que c'est ?
    - Un indicateur technique qui mesure la vitesse et l'ampleur des mouvements de prix
    - Varie de 0 à 100
    
    ### Comment l'interpréter ?
    - RSI > 70 : Signal de survente (risque de baisse)
    - RSI < 30 : Signal de surachat (opportunité d'achat potentielle)
    - Entre 30-70 : Zone neutre
    
    ## 2. Indicateurs Clés de Trading
    
    ### Volume
    - Quantité totale d'une crypto échangée sur une période donnée (en USDT)
    - Un volume élevé = beaucoup de transactions = marché actif
    - Un volume faible = peu de transactions = marché peu liquide
    - Volume en hausse = confirme la tendance
    - Volume en baisse = possible changement de tendance
    - Volume minimum recommandé : 100,000 USDT pour les débutants
    
    ### Variation
    - Pourcentage de changement du prix sur une période donnée
    - Types :
        * Positive : Le prix a augmenté
        * Négative : Le prix a baissé
    
    ### Volatilité
    - Mesure de l'ampleur des variations de prix
    - Forte volatilité = variations importantes et rapides = plus de risques
    - Faible volatilité = variations limitées et plus lentes = plus stable
    
    ## 3. Conseils de Trading
    
    ### Gestion du Risque
    - Ne jamais investir plus que ce que vous pouvez perdre
    - Diversifier vos investissements
    - Utiliser des ordres stop-loss
    - Commencer petit et augmenter progressivement
    
    ### Pour les Débutants
    - Commencer avec les cryptos majeures (BTC, ETH)
    - Privilégier les volumes importants (>100,000 USDT)
    - Éviter les cryptos très volatiles au début
    - Ne pas faire de trading sur effet de levier
    
    ### Bonnes Pratiques
    - Faire vos propres recherches avant d'investir
    - Ne pas trader sous le coup de l'émotion
    - Tenir un journal de trading
    - Définir une stratégie claire et s'y tenir
    """)

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
