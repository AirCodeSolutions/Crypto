# services/exchange.py
import time
from typing import Optional, Dict, Any, List
import ccxt
import pandas as pd
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

class ExchangeService:
    def __init__(self):
        self.exchange = ccxt.kucoin({
            'adjustForTimeDifference': True,
            'timeout': 30000,
            'enableRateLimit': True,  # Activer la limitation de taux
            'rateLimit': 100  # Délai en millisecondes entre les requêtes
        })
        self._cache = {}  # Cache pour les données
        self._cache_duration = 10  # Durée du cache en secondes

    # ... reste du code inchangé ...

    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """Récupère les données du cache si elles sont valides"""
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self._cache_duration:
                return data
        return None

    def _cache_data(self, key: str, data: Dict):
        """Met en cache les données avec un timestamp"""
        self._cache[key] = (time.time(), data)

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Récupère le ticker avec gestion du cache et des erreurs"""
        cache_key = f"ticker_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            # Ajout d'un délai pour respecter les limites
            time.sleep(0.1)  # 100ms entre les requêtes
            ticker = self.exchange.fetch_ticker(f"{symbol}/USDT")
            self._cache_data(cache_key, ticker)
            return ticker
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du ticker pour {symbol}: {e}")
            # Retourner des données par défaut en cas d'erreur
            return {
                'last': 0,
                'percentage': 0,
                'quoteVolume': 0
            }

    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> Optional[pd.DataFrame]:
        """Récupère les données OHLCV avec gestion du cache"""
        cache_key = f"ohlcv_{symbol}_{timeframe}_{limit}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            time.sleep(0.1)  # Respecter les limites de taux
            ohlcv = self.exchange.fetch_ohlcv(f"{symbol}/USDT", timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            self._cache_data(cache_key, df)
            return df
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données OHLCV pour {symbol}: {e}")
            return None

    def get_available_symbols(self) -> List[str]:
        """Récupère la liste des symboles avec gestion du cache"""
        cache_key = "available_symbols"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            markets = self.exchange.load_markets()
            symbols = [
                symbol.split('/')[0] for symbol in markets.keys()
                if symbol.endswith('/USDT')
            ]
            self._cache_data(cache_key, symbols)
            return symbols
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des symboles: {e}")
            return []