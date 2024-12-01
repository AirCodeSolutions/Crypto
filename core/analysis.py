import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """Configuration pour l'analyse technique"""
    rsi_period: int = 14
    ema_periods: List[int] = field(default_factory=lambda: [9, 20, 50])
    volume_threshold: float = 1.5
    score_threshold: float = 0.7
    support_window: int = 20
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

@dataclass
class TradingSignal:
    """Structure d'un signal de trading"""
    action: Optional[str] = None
    strength: float = 0.0
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    reasons: List[str] = field(default_factory=list)

class TechnicalAnalyzer:
    """
    Analyseur technique pour les cryptomonnaies
    Fournit des analyses avancées et des signaux de trading
    """

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        Initialise l'analyseur technique
        
        Args:
            config: Configuration personnalisée (optionnelle)
        """
        self.config = config or AnalysisConfig()
        self._validate_config()
        logger.info("Analyseur technique initialisé")

    def _validate_config(self):
        """Valide la configuration de l'analyseur"""
        if not self.config.ema_periods:
            raise ValueError("Les périodes EMA ne peuvent pas être vides")
        if self.config.rsi_period <= 0:
            raise ValueError("La période RSI doit être positive")

    def analyze_crypto(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Réalise une analyse complète d'une crypto
        
        Args:
            df: DataFrame avec les données OHLCV
            current_price: Prix actuel
            
        Returns:
            Dict: Résultats de l'analyse
        """
        try:
            if df.empty:
                raise ValueError("DataFrame vide")

            # Calcul des indicateurs
            rsi = self.calculate_rsi(df)
            support, resistance = self.calculate_support_resistance(df)
            momentum_score = self.calculate_momentum_score(df)
            market_sentiment = self.get_market_sentiment(df)
            volume_profile = self.analyze_volume_profile(df)

            # Génération du signal
            signal = self.generate_trading_signal(
                df, current_price, rsi.iloc[-1],
                support, resistance, momentum_score
            )

            return {
                'rsi': rsi.iloc[-1],
                'support': support,
                'resistance': resistance,
                'momentum_score': momentum_score,
                'market_sentiment': market_sentiment,
                'volume_profile': volume_profile,
                'signal': signal
            }

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {e}")
            raise

    def calculate_rsi(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcule le RSI (Relative Strength Index)
        
        Args:
            df: DataFrame avec les données OHLCV
            
        Returns:
            pd.Series: Valeurs du RSI
        """
        try:
            close_delta = df['close'].diff()

            # Calcul des gains et pertes
            gain = (close_delta.where(close_delta > 0, 0)).rolling(
                window=self.config.rsi_period
            ).mean()
            loss = (-close_delta.where(close_delta < 0, 0)).rolling(
                window=self.config.rsi_period
            ).mean()

            rs = gain / loss
            return 100 - (100 / (1 + rs))

        except Exception as e:
            logger.error(f"Erreur calcul RSI: {e}")
            raise

    def calculate_support_resistance(df, window=20):
        """Calcule les niveaux de support et résistance"""
        rolling_min = df['low'].rolling(window=window).min()
        rolling_max = df['high'].rolling(window=window).max()
        return rolling_min.iloc[-1], rolling_max.iloc[-1]
    
    def calculate_momentum_score(df):
        """Calcule un score de momentum global"""
        # Calcul des indicateurs
        df['macd'] = ta.trend.macd_diff(df['close'])
        df['rsi'] = ta.momentum.rsi(df['close'])
        df['stoch'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
        df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'])
        
        score = 0
        # Scoring des différents indicateurs
        if df['macd'].iloc[-1] > 0: score += 1
        if 40 < df['rsi'].iloc[-1] < 60: score += 1
        if df['stoch'].iloc[-1] > df['stoch'].iloc[-2]: score += 1
        if df['adx'].iloc[-1] > 25: score += 1
        
        return score / 4
    
    def get_market_sentiment(df):
        """Analyse le sentiment du marché"""
        sentiment_score = 0
        
        # Analyse des EMA
        df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
        df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
        
        if df['ema9'].iloc[-1] > df['ema20'].iloc[-1]: sentiment_score += 1
        if df['ema20'].iloc[-1] > df['ema50'].iloc[-1]: sentiment_score += 1
        if df['close'].iloc[-1] > df['ema20'].iloc[-1]: sentiment_score += 1
        
        return sentiment_score / 3
    
    def analyze_volume_profile(df):
            """Analyse le profil volumétrique"""
            volume_mean = df['volume'].mean()
            recent_volume = df['volume'].iloc[-5:].mean()
            return recent_volume / volume_mean

    def generate_trading_signal(
        self, df: pd.DataFrame, current_price: float,
        rsi: float, support: float, resistance: float,
        momentum_score: float
    ) -> TradingSignal:
        """
        Génère un signal de trading basé sur l'analyse
        
        Args:
            df: DataFrame des données
            current_price: Prix actuel
            rsi: Valeur RSI actuelle
            support: Niveau de support
            resistance: Niveau de résistance
            momentum_score: Score de momentum
            
        Returns:
            TradingSignal: Signal de trading généré
        """
        try:
            signal = TradingSignal()

            # Conditions d'achat
            buy_conditions = (
                30 <= rsi <= 45 and
                current_price > support * 1.01 and
                current_price < resistance * 0.95 and
                momentum_score >= self.config.score_threshold
            )

            # Construction du signal
            if buy_conditions:
                signal.action = 'BUY'
                signal.strength = momentum_score
                signal.entry_price = current_price
                signal.stop_loss = support * 0.99
                signal.target_1 = current_price * 1.02
                signal.target_2 = current_price * 1.03
                signal.reasons = self._generate_signal_reasons(
                    rsi, momentum_score, current_price, support, resistance
                )

            return signal

        except Exception as e:
            logger.error(f"Erreur génération signal: {e}")
            raise