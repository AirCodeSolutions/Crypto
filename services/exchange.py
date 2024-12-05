# services/exchange.py
import time
from typing import Optional, Dict, Any, List
from functools import lru_cache
import ccxt
import pandas as pd
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

class ExchangeService:
    def __init__(self):
        self.exchange = ccxt.kucoin({
            'enableRateLimit': True,
            'rateLimit': 50  # Réduit à 50ms entre les requêtes
        })
        self._last_request_time = 0
        self._min_request_interval = 0.05  # 50ms

    def _rate_limit(self):
        """Gestion simple des limites de taux"""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    @lru_cache(maxsize=100)
    def get_ticker(self, symbol: str):
        """Version optimisée avec cache"""
        self._rate_limit()
        return self.exchange.fetch_ticker(f"{symbol}/USDT")

    @lru_cache(maxsize=50)
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """Version optimisée avec cache"""
        self._rate_limit()
        return self.exchange.fetch_ohlcv(f"{symbol}/USDT", timeframe, limit=limit)

   

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