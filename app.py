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
    ["Analyse en Direct", "Top Performances", "Opportunités Court Terme", "Analyse Historique"]
)

# Function pour calculer le RSI
def calculate_rsi(df, periods=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Page principale
if page == "Analyse en Direct":
    st.title("📈 Analyse en Direct")
    
    # Input pour ajouter une crypto
    symbol = st.text_input("Entrez le symbole de la crypto (ex: BTC, ETH)", "").upper()
    
    if symbol:
        valid_symbol = get_valid_symbol(symbol)
        if valid_symbol:
            try:
                # Récupération des données
                ticker = exchange.fetch_ticker(valid_symbol)
                ohlcv = exchange.fetch_ohlcv(valid_symbol, '1h', limit=100)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # Calcul des indicateurs
                df['SMA20'] = df['close'].rolling(window=20).mean()
                df['SMA50'] = df['close'].rolling(window=50).mean()
                df['RSI'] = calculate_rsi(df)
                
                # Affichage des métriques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix actuel", f"{ticker['last']:.8f} USDT")
                with col2:
                    st.metric("RSI", f"{df['RSI'].iloc[-1]:.2f}")
                with col3:
                    variation_24h = ticker['percentage']
                    st.metric("Variation 24h", f"{variation_24h:.2f}%")
                
                # Graphique des prix
                st.subheader("Évolution du prix")
                st.line_chart(df.set_index('timestamp')['close'])
                
                # Volume
                st.subheader("Volume des échanges")
                st.bar_chart(df.set_index('timestamp')['volume'])
                
            except Exception as e:
                st.error(f"Erreur lors de l'analyse: {str(e)}")
        else:
            st.error(f"La crypto {symbol} n'est pas disponible sur KuCoin")

# Page Top Performances
elif page == "Top Performances":
    st.title("🏆 Top Performances")
    
    major_coins = ['BTC', 'ETH', 'KCS', 'XRP', 'SOL', 'DOT', 'AVAX', 'MATIC']
    
    if st.button("Rafraîchir"):
        try:
            performances = []
            for coin in major_coins:
                valid_symbol = get_valid_symbol(coin)
                if valid_symbol:
                    try:
                        ticker = exchange.fetch_ticker(valid_symbol)
                        performances.append({
                            'symbol': coin,
                            'price': ticker['last'],
                            'change_24h': ticker['percentage'],
                            'volume': ticker['quoteVolume']
                        })
                    except:
                        continue
            
            if performances:
                performances.sort(key=lambda x: x['change_24h'], reverse=True)
                
                for p in performances:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(p['symbol'], f"{p['price']:.8f} USDT")
                    with col2:
                        st.metric("Variation 24h", f"{p['change_24h']:.2f}%")
                    with col3:
                        st.metric("Volume", f"{p['volume']:,.0f} USDT")
                    st.markdown("---")
            
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

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
                    ohlcv_short = exchange.fetch_ohlcv(symbol, '15m', limit=24)  # 6h
                    ohlcv_7h = exchange.fetch_ohlcv(symbol, '15m', limit=28)    # 7h
                    ohlcv_24h = exchange.fetch_ohlcv(symbol, '1h', limit=24)    # 24h
                    
                    if ticker['quoteVolume'] >= min_vol:
                        # DataFrame pour chaque période
                        df_short = pd.DataFrame(ohlcv_short, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_7h = pd.DataFrame(ohlcv_7h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_24h = pd.DataFrame(ohlcv_24h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        
                        # Calcul des variations sur différentes périodes
                        price_change_1h = ((df_short['close'].iloc[-1] - df_short['close'].iloc[-4]) / df_short['close'].iloc[-4]) * 100
                        price_change_7h = ((df_7h['close'].iloc[-1] - df_7h['close'].iloc[0]) / df_7h['close'].iloc[0]) * 100
                        price_change_24h = ((df_24h['close'].iloc[-1] - df_24h['close'].iloc[0]) / df_24h['close'].iloc[0]) * 100
                        
                        vol_change = (df_short['volume'].iloc[-1] / df_short['volume'].mean()) * 100
                        
                        # RSI court terme
                        delta = df_short['close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=6).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=6).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        current_rsi = rsi.iloc[-1]
                        
                        if abs(price_change_1h) >= min_var:
                            signal = "🟢 ACHAT" if price_change_1h > 0 else "🔴 VENTE"
                            if (signal.startswith("🟢") and current_rsi < 70) or (signal.startswith("🔴") and current_rsi > 30):
                                opportunities.append({
                                    'symbol': symbol.split('/')[0],
                                    'price': ticker['last'],
                                    'price_change_1h': price_change_1h,
                                    'price_change_7h': price_change_7h,
                                    'price_change_24h': price_change_24h,
                                    'volume_change': vol_change,
                                    'rsi': current_rsi,
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
                
                # Prix et variations
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Prix", f"{op['price']:.8f} USDT")
                with col2:
                    direction = "↗️" if op['price_change_1h'] > 0 else "↘️"
                    st.metric("Variation 1h", f"{op['price_change_1h']:.2f}% {direction}")
                with col3:
                    st.metric("Volume 24h", f"{op['volume']:,.0f} USDT")
                
                # Indicateurs détaillés
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("RSI", f"{op['rsi']:.2f}")
                with col2:
                    st.metric("Variation 7h", f"{op['price_change_7h']:.2f}%")
                with col3:
                    st.metric("Variation 24h", f"{op['price_change_24h']:.2f}%")
                with col4:
                    st.metric("Variation volume", f"{op['volume_change']:.2f}%")
                
                # Analyse et recommandation
                st.markdown(f"**Signal:** {op['signal']}")
                
                # Analyse supplémentaire
                if op['signal'].startswith("🟢"):  # Signal d'achat
                    if op['rsi'] < 30:
                        st.success("📊 Opportunité d'achat forte (RSI survendu)")
                    else:
                        st.info("📈 Momentum haussier détecté")
                else:  # Signal de vente
                    if op['rsi'] > 70:
                        st.error("📊 Opportunité de vente forte (RSI suracheté)")
                    else:
                        st.warning("📉 Momentum baissier détecté")
                
                # Tendance générale
                changes = [op['price_change_1h'], op['price_change_7h'], op['price_change_24h']]
                if all(x > 0 for x in changes):
                    st.success("🚀 Tendance haussière sur toutes les périodes")
                elif all(x < 0 for x in changes):
                    st.error("📉 Tendance baissière sur toutes les périodes")
                else:
                    st.info("↔️ Tendance mixte")
                
                st.markdown("---")
            
            # Timestamp de mise à jour
            st.write(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

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
