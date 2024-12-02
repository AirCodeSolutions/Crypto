# app.py
import streamlit as st
import pandas as pd
from services.exchange import ExchangeService
from core.analysis import MarketAnalyzer

def main():
    st.set_page_config(page_title="Test Données Réelles", layout="wide")
    st.title("Test des Données Réelles KuCoin")

    # Initialisation des services
    exchange = ExchangeService()
    analyzer = MarketAnalyzer(exchange)

    # Sélection de crypto simple pour le test
    try:
        # Test de la récupération des symboles disponibles
        available_symbols = exchange.get_available_symbols()
        st.success(f"✅ Connexion à l'exchange réussie - {len(available_symbols)} symboles disponibles")
        
        selected_crypto = st.selectbox(
            "Sélectionnez une crypto à analyser",
            ["BTC", "ETH", "SOL", "BNB", "XRP"]
        )

        if st.button("Analyser"):
            with st.spinner("Récupération des données..."):
                # Test de la récupération du ticker
                ticker = exchange.get_ticker(selected_crypto)
                st.write("📊 Données du Ticker:")
                st.json({
                    "prix": ticker['last'],
                    "volume_24h": ticker['quoteVolume'],
                    "variation_24h": f"{ticker['percentage']}%"
                })

                # Test de la récupération des données OHLCV
                df = exchange.get_ohlcv(selected_crypto)
                st.write("📈 Dernières données OHLCV:")
                st.dataframe(df.tail())

                # Test de l'analyse complète
                analysis = analyzer.analyze_symbol(selected_crypto)
                st.write("🔍 Résultat de l'analyse:")
                st.json({
                    "RSI": f"{analysis['rsi']:.2f}",
                    "Signal": analysis['signal'],
                    "Volume Ratio": f"{analysis['volume_ratio']:.2f}",
                    "MACD": f"{analysis['macd']:.2f}"
                })

    except Exception as e:
        st.error(f"❌ Erreur lors du test: {str(e)}")
        st.info("💡 Vérifiez que vous êtes bien connecté à Internet et que l'API KuCoin est accessible")

if __name__ == "__main__":
    main()