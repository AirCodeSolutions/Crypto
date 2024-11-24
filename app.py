<<<<<<< HEAD
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

# Structure correcte des conditions
if page == "Analyse en Direct":
    # Votre code existant pour Analyse en Direct...
    pass

elif page == "Top Performances":
    st.title("🏆 Top Performances")
    # Modifiez la partie du filtrage après la récupération des performances
    if st.button("Rafraîchir"):
        try:
            performances = []
            with st.spinner("Analyse des performances en cours..."):
                markets = exchange.load_markets()
                for symbol in markets:
                    if symbol.endswith('/USDT'):
                        try:
                            ticker = exchange.fetch_ticker(symbol)
                            if ticker['last'] <= 20:  # Filtrer uniquement les cryptos <= 20 USDT
                                ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=7)
                                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                                
                                # Calculs...
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
                
elif page == "Opportunités Court Terme":
    st.title("🎯 Opportunités Court Terme")
    
    # Paramètres de filtrage
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
                    # Récupération des données sur différentes périodes
                    ticker = exchange.fetch_ticker(symbol)
                    
                    # Filtrer par prix <= 20 USDT
                    if ticker['last'] <= 20 and ticker['quoteVolume'] >= min_vol:
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
                            
                            # RSI court terme
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
            
            # Tri des opportunités
            opportunities.sort(key=lambda x: abs(x['price_change_1h']), reverse=True)
            
            # Affichage des opportunités
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

elif page == "Guide & Explications":
    # Ajoutez ici le code du guide que je vous ai fourni précédemment...
elif page == "Opportunités Court Terme":
    st.title("🎯 Opportunités Court Terme")
    
    # Paramètres de filtrage
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
                    if ticker['quoteVolume'] >= min_vol and ticker['last'] <= 20:  # Ajout du filtre de prix
                        ohlcv_short = exchange.fetch_ohlcv(symbol, '15m', limit=24)
                        ohlcv_7h = exchange.fetch_ohlcv(symbol, '15m', limit=28)
                        ohlcv_24h = exchange.fetch_ohlcv(symbol, '1h', limit=24)
                        
                        # DataFrame pour chaque période
                        df_short = pd.DataFrame(ohlcv_short, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_7h = pd.DataFrame(ohlcv_7h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_24h = pd.DataFrame(ohlcv_24h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        
                        # Calculs...
                        price_change_1h = ((df_short['close'].iloc[-1] - df_short['close'].iloc[-4]) / df_short['close'].iloc[-4]) * 100
                        
                        if abs(price_change_1h) >= min_var:
                            # Votre logique d'opportunités existante...
                            pass
                            
                except Exception as e:
                    print(f"Erreur pour {symbol}: {str(e)}")
                    continue
                
                count += 1
                progress.progress(count / total)
  
# Page Analyse Historique - Enrichissement des analyses
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
                        
                        # Mise à jour timestamp
                        st.caption(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
                        
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse: {str(e)}")
            else:
                st.error(f"La crypto {symbol} n'est pas disponible sur KuCoin")
                
else:  # Analyse Historique
    st.title("📊 Analyse Historique")
    
    symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC, ETH)", "").upper()
    
    if symbol:
        timeframes = {
            "1 jour": "1d",
            "1 semaine": "1w",
            "1 mois": "1M"
        }
        
        selected_timeframe = st.selectbox("Période d'analyse", list(timeframes.keys()))
        
        if st.button("Analyser"):
            valid_symbol = get_valid_symbol(symbol)
            if valid_symbol:
                try:
                    ohlcv = exchange.fetch_ohlcv(valid_symbol, timeframes[selected_timeframe])
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Métriques principales
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        variation = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
                        st.metric("Variation totale", f"{variation:.2f}%")
                    with col2:
                        st.metric("Plus haut", f"{df['high'].max():.8f}")
                    with col3:
                        st.metric("Plus bas", f"{df['low'].min():.8f}")
                    
                    # Graphiques
                    st.subheader("Évolution du prix")
                    st.line_chart(df.set_index('timestamp')['close'])
                    
                    st.subheader("Volume des échanges")
                    st.bar_chart(df.set_index('timestamp')['volume'])
                    
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
            else:
                st.error(f"La crypto {symbol} n'est pas disponible sur KuCoin")
=======
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

# Structure correcte des conditions
if page == "Analyse en Direct":
    # Votre code existant pour Analyse en Direct...
    pass

elif page == "Top Performances":
    st.title("🏆 Top Performances")
    # Modifiez la partie du filtrage après la récupération des performances
    if st.button("Rafraîchir"):
        try:
            performances = []
            with st.spinner("Analyse des performances en cours..."):
                markets = exchange.load_markets()
                for symbol in markets:
                    if symbol.endswith('/USDT'):
                        try:
                            ticker = exchange.fetch_ticker(symbol)
                            if ticker['last'] <= 20:  # Filtrer uniquement les cryptos <= 20 USDT
                                ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=7)
                                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                                
                                # Calculs...
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
                
                # Le reste de votre code pour l'affichage...

elif page == "Opportunités Court Terme":
    st.title("🎯 Opportunités Court Terme")
    
    # Paramètres de filtrage
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
                    # Récupération des données sur différentes périodes
                    ticker = exchange.fetch_ticker(symbol)
                    
                    # Filtrer par prix <= 20 USDT
                    if ticker['last'] <= 20 and ticker['quoteVolume'] >= min_vol:
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
                            
                            # RSI court terme
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
            
            # Tri des opportunités
            opportunities.sort(key=lambda x: abs(x['price_change_1h']), reverse=True)
            
            # Affichage des opportunités
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

elif page == "Guide & Explications":
    # Ajoutez ici le code du guide que je vous ai fourni précédemment...
elif page == "Opportunités Court Terme":
    st.title("🎯 Opportunités Court Terme")
    
    # Paramètres de filtrage
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
                    if ticker['quoteVolume'] >= min_vol and ticker['last'] <= 20:  # Ajout du filtre de prix
                        ohlcv_short = exchange.fetch_ohlcv(symbol, '15m', limit=24)
                        ohlcv_7h = exchange.fetch_ohlcv(symbol, '15m', limit=28)
                        ohlcv_24h = exchange.fetch_ohlcv(symbol, '1h', limit=24)
                        
                        # DataFrame pour chaque période
                        df_short = pd.DataFrame(ohlcv_short, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_7h = pd.DataFrame(ohlcv_7h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_24h = pd.DataFrame(ohlcv_24h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        
                        # Calculs...
                        price_change_1h = ((df_short['close'].iloc[-1] - df_short['close'].iloc[-4]) / df_short['close'].iloc[-4]) * 100
                        
                        if abs(price_change_1h) >= min_var:
                            # Votre logique d'opportunités existante...
                            pass
                            
                except Exception as e:
                    print(f"Erreur pour {symbol}: {str(e)}")
                    continue
                
                count += 1
                progress.progress(count / total)
  
# Page Analyse Historique - Enrichissement des analyses
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
                        
                        # Mise à jour timestamp
                        st.caption(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
                        
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse: {str(e)}")
            else:
                st.error(f"La crypto {symbol} n'est pas disponible sur KuCoin")
                
else:  # Analyse Historique
    st.title("📊 Analyse Historique")
    
    symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC, ETH)", "").upper()
    
    if symbol:
        timeframes = {
            "1 jour": "1d",
            "1 semaine": "1w",
            "1 mois": "1M"
        }
        
        selected_timeframe = st.selectbox("Période d'analyse", list(timeframes.keys()))
        
        if st.button("Analyser"):
            valid_symbol = get_valid_symbol(symbol)
            if valid_symbol:
                try:
                    ohlcv = exchange.fetch_ohlcv(valid_symbol, timeframes[selected_timeframe])
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Métriques principales
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        variation = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
                        st.metric("Variation totale", f"{variation:.2f}%")
                    with col2:
                        st.metric("Plus haut", f"{df['high'].max():.8f}")
                    with col3:
                        st.metric("Plus bas", f"{df['low'].min():.8f}")
                    
                    # Graphiques
                    st.subheader("Évolution du prix")
                    st.line_chart(df.set_index('timestamp')['close'])
                    
                    st.subheader("Volume des échanges")
                    st.bar_chart(df.set_index('timestamp')['volume'])
                    
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
            else:
                st.error(f"La crypto {symbol} n'est pas disponible sur KuCoin")
>>>>>>> 8a9b577289e4f0a666d2fc114b9c7b1ebcf94284
