# core/analysis.py
import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """
    Classe regroupant les indicateurs techniques avancés.
    Cette classe sert de boîte à outils pour l'analyse technique.
    """
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20, std: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calcule les bandes de Bollinger.
        Les bandes de Bollinger nous aident à identifier les zones de survente/surachat
        et la volatilité du marché.
        """
        try:
            indicator_bb = ta.volatility.BollingerBands(
                close=df['close'], 
                window=window, 
                window_dev=std
            )
            
            return {
                'bb_upper': indicator_bb.bollinger_hband(),  # Bande supérieure
                'bb_middle': indicator_bb.bollinger_mavg(),  # Moyenne mobile
                'bb_lower': indicator_bb.bollinger_lband(),  # Bande inférieure
                'bb_width': indicator_bb.bollinger_wband()   # Largeur des bandes (volatilité)
            }
        except Exception as e:
            logger.error(f"Erreur calcul Bollinger Bands: {e}")
            return None

    @staticmethod
    def calculate_macd(df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calcule le MACD (Moving Average Convergence Divergence).
        Le MACD est excellent pour identifier les changements de tendance
        et la force du momentum.
        """
        try:
            macd = ta.trend.MACD(df['close'])
            return {
                'macd_line': macd.macd(),           # Ligne MACD
                'signal_line': macd.macd_signal(),  # Ligne de signal
                'histogram': macd.macd_diff()       # Histogramme (différence)
            }
        except Exception as e:
            logger.error(f"Erreur calcul MACD: {e}")
            return None

    @staticmethod
    def calculate_rsi_divergence(df: pd.DataFrame, window: int = 14) -> Dict[str, bool]:
        """
        Détecte les divergences RSI/Prix.
        Les divergences sont des signaux puissants de retournement potentiel.
        """
        try:
            rsi = ta.momentum.RSIIndicator(df['close'], window).rsi()
            
            # On regarde les 5 dernières périodes
            price_trend = df['close'].tail(5).is_monotonic_increasing
            rsi_trend = rsi.tail(5).is_monotonic_increasing
            
            return {
                'bullish_divergence': not price_trend and rsi_trend,  # Prix ↓ mais RSI ↑
                'bearish_divergence': price_trend and not rsi_trend   # Prix ↑ mais RSI ↓
            }
        except Exception as e:
            logger.error(f"Erreur calcul divergence RSI: {e}")
            return None

    @staticmethod
    def detect_patterns(df: pd.DataFrame) -> List[str]:
        """
        Détecte les patterns de chandeliers japonais.
        Ces patterns nous donnent des indications sur les retournements potentiels.
        """
        patterns = []
        try:
            # Doji (indécision)
            if ta.candlestick.doji(df['open'], df['high'], df['low'], df['close']).iloc[-1]:
                patterns.append("Doji")
            
            # Marteau (potentiel retournement haussier)
            if ta.candlestick.hammer(df['open'], df['high'], df['low'], df['close']).iloc[-1]:
                patterns.append("Hammer")
                
            # Étoile filante (potentiel retournement baissier)
            if ta.candlestick.shooting_star(df['open'], df['high'], df['low'], df['close']).iloc[-1]:
                patterns.append("Shooting Star")
                
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur détection patterns: {e}")
            return []


class TradingSignalAnalyzer:
    """
    Système d'analyse avancé qui combine tous nos indicateurs techniques
    pour générer des signaux de trading plus précis.
    """
    
    def __init__(self, technical_indicators: TechnicalIndicators):
        self.indicators = technical_indicators
        self.score_weights = {
            'trend': 0.3,      # Poids de l'analyse de tendance
            'momentum': 0.25,  # Poids des indicateurs de momentum
            'volatility': 0.2, # Poids de la volatilité
            'patterns': 0.25   # Poids des patterns techniques
        }

    def analyze_market_conditions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse complète des conditions de marché combinant tous les indicateurs.
        Cette méthode nous donne une vue d'ensemble de l'état du marché.
        """
        try:
            # Récupération de tous les indicateurs
            bb_data = self.indicators.calculate_bollinger_bands(df)
            macd_data = self.indicators.calculate_macd(df)
            rsi_div = self.indicators.calculate_rsi_divergence(df)
            patterns = self.indicators.detect_patterns(df)
            
            # Calcul du score de tendance
            trend_score = self._calculate_trend_score(df, bb_data, macd_data)
            
            # Calcul du score de momentum
            momentum_score = self._calculate_momentum_score(df, macd_data, rsi_div)
            
            # Calcul du score de volatilité
            volatility_score = self._calculate_volatility_score(bb_data)
            
            # Score des patterns
            pattern_score = self._evaluate_patterns(patterns)
            
            # Score final pondéré
            final_score = (
                trend_score * self.score_weights['trend'] +
                momentum_score * self.score_weights['momentum'] +
                volatility_score * self.score_weights['volatility'] +
                pattern_score * self.score_weights['patterns']
            )
            
            return {
                'score': final_score,
                'analysis': {
                    'trend': self._get_trend_analysis(trend_score),
                    'momentum': self._get_momentum_analysis(momentum_score),
                    'volatility': self._get_volatility_analysis(volatility_score),
                    'patterns': patterns
                },
                'signal': self._generate_signal(final_score, trend_score, momentum_score)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse marché: {e}")
            return None

    def _calculate_trend_score(self, df: pd.DataFrame, bb_data: Dict, macd_data: Dict) -> float:
        """
        Évalue la force de la tendance actuelle.
        Un score élevé indique une tendance forte et claire.
        """
        try:
            # Position du prix par rapport aux Bandes de Bollinger
            price = df['close'].iloc[-1]
            bb_position = (price - bb_data['bb_lower'].iloc[-1]) / (
                bb_data['bb_upper'].iloc[-1] - bb_data['bb_lower'].iloc[-1]
            )
            
            # Force du MACD
            macd_strength = macd_data['histogram'].iloc[-1] / df['close'].mean()
            
            # Combinaison des scores
            trend_score = (bb_position * 0.6 + abs(macd_strength) * 0.4)
            return min(max(trend_score, 0), 1)  # Normalisation entre 0 et 1
            
        except Exception as e:
            logger.error(f"Erreur calcul score tendance: {e}")
            return 0.5

    def _generate_signal(self, final_score: float, trend_score: float, momentum_score: float) -> str:
        """
        Génère un signal de trading basé sur l'analyse globale.
        Les signaux sont plus nuancés et prennent en compte plusieurs facteurs.
        """
        if final_score >= 0.8 and trend_score > 0.7 and momentum_score > 0.7:
            return "STRONG_BUY"
        elif final_score >= 0.6 and trend_score > 0.5:
            return "BUY"
        elif final_score <= 0.2 and trend_score < 0.3:
            return "STRONG_SELL"
        elif final_score <= 0.4 and trend_score < 0.5:
            return "SELL"
        return "NEUTRAL"

class MarketAnalyzer:
    """
    Classe principale qui coordonne l'analyse de marché.
    Elle utilise TechnicalIndicators et TradingSignalAnalyzer pour fournir
    une analyse complète des opportunités de trading.
    """
    
    def __init__(self, exchange_service):
        """
        Initialise l'analyseur de marché avec les services nécessaires.
        
        Args:
            exchange_service: Service permettant d'accéder aux données de l'exchange
        """
        self.exchange = exchange_service
        self.technical_indicators = TechnicalIndicators()
        self.signal_analyzer = TradingSignalAnalyzer(self.technical_indicators)

    def analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Réalise une analyse complète d'une crypto-monnaie.
        
        Args:
            symbol: Symbole de la crypto à analyser
            
        Returns:
            Dict contenant tous les résultats d'analyse
        """
        try:
            # Récupération des données récentes
            ticker = self.exchange.get_ticker(symbol)
            df = self.exchange.get_ohlcv(symbol)
            
            if df is None or df.empty:
                raise ValueError(f"Données non disponibles pour {symbol}")

            # Analyse technique complète
            market_analysis = self.signal_analyzer.analyze_market_conditions(df)
            
            # Construction du résultat final
            return {
                'price': ticker['last'],
                'change_24h': ticker['percentage'],
                'volume_24h': ticker['quoteVolume'],
                'rsi': self.technical_indicators.calculate_rsi_divergence(df)['rsi'].iloc[-1],
                'signal': market_analysis['signal'],
                'score': market_analysis['score'],
                'analysis': market_analysis['analysis'],
                'macd': self.technical_indicators.calculate_macd(df)['histogram'].iloc[-1],
                'timestamp': pd.Timestamp.now()
            }

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {symbol}: {e}")
            raise

    def get_market_sentiment(self, df: pd.DataFrame) -> float:
        """
        Calcule le sentiment général du marché basé sur plusieurs indicateurs.
        
        Args:
            df: DataFrame contenant les données OHLCV
            
        Returns:
            float: Score de sentiment entre 0 et 1
        """
        try:
            market_conditions = self.signal_analyzer.analyze_market_conditions(df)
            return market_conditions['score']
        except Exception as e:
            logger.error(f"Erreur calcul sentiment: {e}")
            return 0.5  # Valeur neutre par défaut