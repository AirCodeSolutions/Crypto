# services/exchange.py
import ccxt
from typing import Dict, Optional

class ExchangeService:
    def __init__(self):
        self.exchange = ccxt.kucoin({
            'adjustForTimeDifference': True,
            'timeout': 30000
        })
        
    def get_ticker(self, symbol: str) -> Dict:
        return self.exchange.fetch_ticker(f"{symbol}/USDT")
        
    def get_ohlcv(self, symbol: str, timeframe: str = '1h') -> list:
        return self.exchange.fetch_ohlcv(f"{symbol}/USDT", timeframe)