# models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

@dataclass
class TradingPosition:
    """Représente une position de trading"""
    symbol: str
    amount: float
    entry_price: float
    current_price: float
    stop_loss: float
    target_1: float
    target_2: float
    entry_date: datetime
    pnl: float = 0.0
    status: str = 'open'
    partial_exits: List[Dict] = field(default_factory=list)
    target1_hit: bool = False

@dataclass
class Portfolio:
    """Représente l'état du portfolio"""
    positions: Dict[str, TradingPosition] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    capital: float = 0.0
    current_capital: float = 0.0
    performance: Dict[str, float] = field(default_factory=lambda: {
        'total_trades': 0,
        'winning_trades': 0,
        'total_profit': 0,
        'max_drawdown': 0
    })

@dataclass
class TradingSignal:
    """Représente un signal de trading"""
    action: Optional[str] = None
    strength: float = 0.0
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    reasons: List[str] = field(default_factory=list)

@dataclass
class MarketOpportunity:
    """Représente une opportunité de marché"""
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    rsi: float
    score: float
    stop_loss: float
    target: float
    risk_reward: float
    conditions: Dict[str, str]
    reasons: List[str]
    suggested_position: float = 30.0
    green_candles: int = 0
    consecutive_green: int = 0

# config.py
class Config:
    """Configuration globale de l'application"""
    EXCHANGE_TIMEOUT = 30000
    MIN_VOLUME = 50000
    MAX_PRICE = 20.0
    RISK_PER_TRADE = 0.015  # 1.5%
    DEFAULT_TIMEFRAME = '1h'
    RSI_PERIOD = 14
    EMA_PERIODS = [9, 20, 50]
    VOLUME_THRESHOLD = 1.5
    SCORE_THRESHOLD = 0.7

# settings.py
class Settings:
    """Paramètres de l'application"""
    AIRTABLE_API_KEY = "your_api_key"  # À remplacer par un système sécurisé
    BASE_ID = "your_base_id"           # À remplacer par un système sécurisé
    
    # Tables Airtable
    CRYPTOS_TABLE = "cryptos_suivies"
    ANALYSES_TABLE = "historique_analyses"
    USERS_TABLE = "utilisateurs"
    
    # Paramètres de trading
    DEFAULT_CAPITAL = 1000.0
    MAX_POSITIONS = 3
    MIN_POSITION_SIZE = 30.0
    MAX_POSITION_SIZE = 100.0
    
    # Paramètres techniques
    DEFAULT_STOP_LOSS = 0.015  # 1.5%
    DEFAULT_TARGET_1 = 0.03    # 3%
    DEFAULT_TARGET_2 = 0.05    # 5%

# exceptions.py
class TradingException(Exception):
    """Exception de base pour le trading"""
    pass

class InsufficientFundsException(TradingException):
    """Exception pour fonds insuffisants"""
    pass

class InvalidSymbolException(TradingException):
    """Exception pour symbole invalide"""
    pass

class TechnicalAnalysisException(TradingException):
    """Exception pour erreur d'analyse technique"""
    pass

class ExchangeConnectionException(TradingException):
    """Exception pour erreur de connexion à l'exchange"""
    pass