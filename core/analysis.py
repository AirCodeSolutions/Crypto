# core/analysis.py
import pandas as pd
import ta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analyseur de marché pour les cryptomonnaies"""
    
    def __init__(self, exchange_service):
        """
        Initialise l'analyseur avec un service d'exchange
        
        Args:
            exchange_service: Instance de ExchangeService
        """
        self.exchange = exchange_service

    def analyze_symbol(self, symbol: str) -> Dict:
        """
        Réalise une analyse complète d'une crypto
        
        Args:
            symbol: Symbole de la crypto à analyser
            
        Returns:
            Dict: Résultats de l'analyse
        """
        try:
            # Récupération des données
            df = self.exchange.get_ohlcv(symbol)
            ticker = self.exchange.get_ticker(symbol)
            
            # Calcul des indicateurs
            rsi = ta.momentum.RSIIndicator(df['close']).rsi().iloc[-1]
            macd = ta.trend.MACD(df['close']).macd_diff().iloc[-1]
            
            # Analyse des volumes
            volume_sma = df['volume'].rolling(window=20).mean().iloc[-1]
            volume_current = df['volume'].iloc[-1]
            volume_ratio = volume_current / volume_sma
            
            # Construction du signal
            signal = self._generate_signal(rsi, macd, volume_ratio)
            
            return {
                'price': ticker['last'],
                'change_24h': ticker['percentage'],
                'volume_24h': ticker['quoteVolume'],
                'rsi': rsi,
                'macd': macd,
                'volume_ratio': volume_ratio,
                'signal': signal,
                'timestamp': pd.Timestamp.now()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {symbol}: {e}")
            raise

    def _generate_signal(self, rsi: float, macd: float, volume_ratio: float) -> str:
        """Génère un signal de trading basé sur les indicateurs"""
        if rsi < 30 and macd > 0 and volume_ratio > 1.5:
            return "STRONG_BUY"
        elif rsi < 40 and macd > 0:
            return "BUY"
        elif rsi > 70 and macd < 0:
            return "SELL"
        elif rsi > 60 and macd < 0:
            return "WEAK_SELL"
        else:
            return "NEUTRAL"