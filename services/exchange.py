# services/exchange.py
import ccxt
import pandas as pd
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ExchangeService:
    """Service de communication avec l'exchange KuCoin"""
    
    def __init__(self):
        """Initialise la connexion à l'exchange"""
        try:
            self.exchange = ccxt.kucoin({
                'adjustForTimeDifference': True,
                'timeout': 30000,
                'enableRateLimit': True  # Important pour respecter les limites de l'API
            })
            logger.info("Connexion à KuCoin établie")
        except Exception as e:
            logger.error(f"Erreur de connexion à KuCoin: {e}")
            raise

    def get_ticker(self, symbol: str) -> Dict:
        """
        Récupère les données actuelles d'une crypto
        
        Args:
            symbol: Symbole de la crypto (ex: BTC)
            
        Returns:
            Dict: Données actuelles de la crypto
        """
        try:
            return self.exchange.fetch_ticker(f"{symbol}/USDT")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du ticker pour {symbol}: {e}")
            raise

    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """
        Récupère les données historiques d'une crypto
        
        Args:
            symbol: Symbole de la crypto
            timeframe: Intervalle de temps ('1m', '5m', '1h', '1d', etc.)
            limit: Nombre de périodes à récupérer
            
        Returns:
            pd.DataFrame: Données historiques formatées
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(f"{symbol}/USDT", timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données OHLCV pour {symbol}: {e}")
            raise

    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """
        Récupère le carnet d'ordres d'une crypto
        
        Args:
            symbol: Symbole de la crypto
            limit: Nombre de niveaux à récupérer
            
        Returns:
            Dict: Carnet d'ordres avec bids et asks
        """
        try:
            return self.exchange.fetch_order_book(f"{symbol}/USDT", limit)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du carnet d'ordres pour {symbol}: {e}")
            raise

    def get_available_symbols(self) -> List[str]:
        """
        Récupère la liste des cryptos disponibles
        
        Returns:
            List[str]: Liste des symboles disponibles
        """
        try:
            markets = self.exchange.load_markets()
            return [
                symbol.split('/')[0] for symbol in markets.keys()
                if symbol.endswith('/USDT')
            ]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des symboles disponibles: {e}")
            raise