# core/analysis.py
import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Optional
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