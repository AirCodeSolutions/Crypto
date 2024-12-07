# interface/pages/top_performance.py
import streamlit as st
import time
from typing import List, Dict
from ..components.guide_helper import GuideHelper

class TopPerformancePage:
    """Page d'analyse des meilleures performances"""
    
    def __init__(self, exchange_service, analyzer_service):
        """Initialise la page avec les services nécessaires"""
        self.exchange = exchange_service
        self.analyzer = analyzer_service
        
    def render(self):
        """Affiche la page de top performance"""
        st.title("🏆 Top Performances (Prix ≤ 20 USDT)")
        
        # Affichage du guide
        GuideHelper.show_indicator_help()
        GuideHelper.show_pattern_guide()
        GuideHelper.show_quick_guide()
        
        # Configuration des filtres - Simplifiée
        col1, col2 = st.columns(2)
        with col1:
            min_volume = st.number_input(
                "Volume minimum (USDT)",
                value=50000.00
            )
        with col2:
            min_score = st.slider(
                "Score minimum pour achat",
                min_value=0.0,
                max_value=1.0,
                value=0.60
            )
            
        # Bouton de recherche
        if st.button("🔄 Actualiser les données"):
            self._display_top_performers("24h", min_volume)  # timeframe fixé à 24h
                
    def _analyze_candles(self, df) -> Dict:
        """Analyse des patterns de bougies"""
        last_candles = df.tail(5)
        
        return {
            'bullish_patterns': self._detect_bullish_patterns(last_candles),
            'bearish_patterns': self._detect_bearish_patterns(last_candles),
            'trend': self._analyze_trend(last_candles)
        }        
    def _display_top_performers(self, timeframe: str, min_volume: float):
        """Affiche les meilleures performances"""
        with st.spinner("Analyse en cours..."):
            try:
                performers = self._get_top_performers(timeframe, min_volume)
                self._render_results(performers)
            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {str(e)}")
                
    def _get_top_performers(self, timeframe: str, min_volume: float) -> List[Dict]:
        """Version optimisée des top performers"""
        try:
            # Étape 1: Récupération rapide des marchés les plus actifs
            markets = self.exchange.get_available_symbols()
            top_markets = []
            
            with st.spinner("Analyse des marchés..."):
                progress_bar = st.progress(0)
                
                # Traitement par lots pour optimisation
                batch_size = 10
                for i in range(0, min(len(markets), 50), batch_size):
                    batch = markets[i:i+batch_size]
                    for symbol in batch:
                        try:
                            ticker = self.exchange.get_ticker(symbol)
                            # Ajout du filtre de prix <= 20 USDT
                            if ticker['last'] <= 20 and ticker['quoteVolume'] >= min_volume:
                                # Analyse rapide
                                df = self.exchange.get_ohlcv(symbol, timeframe)
                                analysis = self.analyzer.analyze_symbol(symbol)
                                candle_analysis = self._analyze_candles(df)
                                
                                if analysis['score'] >= 0.6:  # Filtre préliminaire
                                    top_markets.append({
                                        'symbol': symbol,
                                        'price': ticker['last'],
                                        'volume': ticker['quoteVolume'],
                                        'change': ticker['percentage'],
                                        'score': analysis['score'],
                                        'candles': candle_analysis,
                                        'signal': analysis['signal']
                                    })
                        except Exception as e:
                            continue
                            
                    progress_bar.progress(min((i + batch_size) / 50, 1.0))
                
                # Tri final avec séparation signaux d'achat et watch list
                return sorted(top_markets, key=lambda x: (x['score'], abs(x['change'])), reverse=True)
                
        except Exception as e:
            raise Exception(f"Erreur lors de l'analyse : {str(e)}")
        
    def _render_results(self, performers: List[Dict]):
        """Affiche les résultats"""
        if not performers:
            st.info("Aucun résultat trouvé")
            return

        # Section Signaux d'achat
        st.markdown("🎯 **Signaux d'achat détectés**")
        buy_signals = [p for p in performers if p['score'] >= 0.70]
        for signal in buy_signals:
            with st.expander(f"💫 {signal['symbol']} - Score: {signal['score']:.2f}"):
                st.metric("Prix", f"${signal['price']:.4f}", f"{signal['change']:+.2f}%")
                st.metric("Volume 24h", f"${signal['volume']/1e6:.1f}M")

        # Section Watch List
        st.markdown("👀 **Watch List**")
        watch_list = [p for p in performers if p['score'] < 0.70]
        
        # Affichage en grille de 3 colonnes
        for i in range(0, len(watch_list), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(watch_list):
                    crypto = watch_list[i + j]
                    with cols[j]:
                        st.write(f"**{crypto['symbol']}**")
                        st.write(f"${crypto['price']:.4f}")
                        st.write(f"{crypto['change']:+.2f}%")

    def _render_signal_details(self, signal: Dict):
        """Affiche les détails d'un signal d'achat"""
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Prix", f"${signal['price']:.4f}", f"{signal['change']:+.2f}%")
            st.metric("Volume 24h", f"${signal['volume']/1e6:.1f}M")
        with col2:
            st.metric("Score", f"{signal['score']:.2f}")
            if 'candles' in signal:
                st.write("Tendance:", signal['candles']['trend'])

    def _detect_bullish_patterns(self, candles) -> List[str]:
        """Détecte les patterns haussiers"""
        patterns = []
        
        # Obtention des données nécessaires
        closes = candles['close'].values
        opens = candles['open'].values
        highs = candles['high'].values
        lows = candles['low'].values
        
        # Détection Marteau
        for i in range(len(candles)):
            body = abs(closes[i] - opens[i])
            lower_shadow = min(opens[i], closes[i]) - lows[i]
            upper_shadow = highs[i] - max(opens[i], closes[i])
            
            # Marteau
            if lower_shadow > 2 * body and upper_shadow < body:
                patterns.append("Marteau")
                
            # Marteau Inversé
            if lower_shadow < body and upper_shadow > 2 * body:
                patterns.append("Marteau Inversé")
        
        # Trois bougies vertes consécutives
        if len(closes) >= 3:
            if all(closes[i] > opens[i] for i in range(-3, 0)):
                patterns.append("Triple Bougie Verte")
        
        return list(set(patterns))  # Évite les doublons

    def _detect_bearish_patterns(self, candles) -> List[str]:
        """Détecte les patterns baissiers"""
        patterns = []
        
        closes = candles['close'].values
        opens = candles['open'].values
        highs = candles['high'].values
        lows = candles['low'].values
        
        # Étoile filante
        for i in range(len(candles)):
            body = abs(closes[i] - opens[i])
            lower_shadow = min(opens[i], closes[i]) - lows[i]
            upper_shadow = highs[i] - max(opens[i], closes[i])
            
            if upper_shadow > 2 * body and lower_shadow < body:
                patterns.append("Étoile Filante")
        
        # Trois bougies rouges consécutives
        if len(closes) >= 3:
            if all(closes[i] < opens[i] for i in range(-3, 0)):
                patterns.append("Triple Bougie Rouge")
        
        return list(set(patterns))

    def _analyze_trend(self, candles) -> str:
        """Analyse la tendance des bougies"""
        closes = candles['close'].values
        opens = candles['open'].values
        
        # Calcul tendance
        up_candles = sum(close > open for close, open in zip(closes, opens))
        down_candles = len(closes) - up_candles
        
        # Tendance des prix
        price_trend = closes[-1] - closes[0]
        
        if up_candles >= 3 and price_trend > 0:
            return "Tendance Haussière"
        elif down_candles >= 3 and price_trend < 0:
            return "Tendance Baissière"
        else:
            return "Tendance Neutre"