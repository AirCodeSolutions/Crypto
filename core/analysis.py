# exceptions.py
class TechnicalAnalysisException(Exception):
    """Exception de base pour les erreurs d'analyse technique"""
    pass

class InvalidDataException(TechnicalAnalysisException):
    """Exception pour les données invalides ou manquantes"""
    pass

class CalculationException(TechnicalAnalysisException):
    """Exception pour les erreurs de calcul d'indicateurs"""
    pass

# analysis.py
import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

class Config:
    """Configuration pour l'analyse technique"""
    RSI_PERIOD = 14
    EMA_PERIODS = [9, 20, 50]
    VOLUME_THRESHOLD = 1.5
    SCORE_THRESHOLD = 0.7

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

class TechnicalAnalysis:
    """Classe pour l'analyse technique des cryptomonnaies"""
    
    class TechnicalAnalysisException(Exception):
        """Exception de base pour les erreurs d'analyse technique"""
        pass

    class InvalidDataException(TechnicalAnalysisException):
        """Exception pour les données invalides ou manquantes"""
        pass

    class CalculationException(TechnicalAnalysisException):
        """Exception pour les erreurs de calcul d'indicateurs"""
        pass
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, periods: int = Config.RSI_PERIOD) -> pd.Series:
        """Calcule le RSI"""
        try:
            if df is None or df.empty:
                raise TechnicalAnalysis.InvalidDataException("DataFrame vide ou invalide")
                
            if 'close' not in df.columns:
                raise TechnicalAnalysis.InvalidDataException("Colonne 'close' manquante dans les données")
                
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
            
            if (loss == 0).all():
                raise TechnicalAnalysis.CalculationException("Division par zéro lors du calcul du RSI")
                
            rs = gain / loss
            return 100 - (100 / (1 + rs))
            
        except Exception as e:
            if isinstance(e, TechnicalAnalysis.TechnicalAnalysisException):
                raise
            raise TechnicalAnalysis.TechnicalAnalysisException(f"Erreur calcul RSI: {str(e)}")

    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
        """Calcule les niveaux de support et résistance"""
        try:
            if df is None or df.empty:
                raise TechnicalAnalysis.InvalidDataException("DataFrame vide ou invalide")
                
            if 'low' not in df.columns or 'high' not in df.columns:
                raise TechnicalAnalysis.InvalidDataException("Colonnes 'low' ou 'high' manquantes")
                
            rolling_min = df['low'].rolling(window=window).min()
            rolling_max = df['high'].rolling(window=window).max()
            
            if rolling_min.iloc[-1] is None or rolling_max.iloc[-1] is None:
                raise TechnicalAnalysis.CalculationException("Impossible de calculer les niveaux")
                
            return rolling_min.iloc[-1], rolling_max.iloc[-1]
            
        except Exception as e:
            if isinstance(e, TechnicalAnalysis.TechnicalAnalysisException):
                raise
            raise TechnicalAnalysis.TechnicalAnalysisException(f"Erreur calcul support/résistance: {str(e)}")

    @staticmethod
    def calculate_momentum_score(df: pd.DataFrame) -> float:
        """Calcule un score de momentum global"""
        try:
            if df is None or df.empty:
                raise TechnicalAnalysis.InvalidDataException("DataFrame vide ou invalide")

            required_columns = ['close', 'high', 'low']
            if not all(col in df.columns for col in required_columns):
                raise TechnicalAnalysis.InvalidDataException("Colonnes requises manquantes")

            df['macd'] = ta.trend.macd_diff(df['close'])
            df['rsi'] = ta.momentum.rsi(df['close'])
            df['stoch'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
            df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'])
            
            if df['macd'].isna().all() or df['rsi'].isna().all():
                raise TechnicalAnalysis.CalculationException("Échec du calcul des indicateurs techniques")
            
            score = 0.0
            if df['macd'].iloc[-1] > 0: score += 0.25
            if 40 < df['rsi'].iloc[-1] < 60: score += 0.25
            if df['stoch'].iloc[-1] > df['stoch'].iloc[-2]: score += 0.25
            if df['adx'].iloc[-1] > 25: score += 0.25
            
            return score
            
        except Exception as e:
            if isinstance(e, TechnicalAnalysis.TechnicalAnalysisException):
                raise
            raise TechnicalAnalysis.TechnicalAnalysisException(f"Erreur calcul momentum: {str(e)}")

    @staticmethod
    def get_market_sentiment(df: pd.DataFrame) -> float:
        """Analyse le sentiment du marché"""
        try:
            if df is None or df.empty:
                raise TechnicalAnalysis.InvalidDataException("DataFrame vide ou invalide")

            if 'close' not in df.columns:
                raise TechnicalAnalysis.InvalidDataException("Colonne 'close' manquante")

            sentiment_score = 0.0
            
            df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
            df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
            df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
            
            if df['ema9'].isna().all() or df['ema20'].isna().all():
                raise TechnicalAnalysis.CalculationException("Échec du calcul des EMAs")
            
            if df['ema9'].iloc[-1] > df['ema20'].iloc[-1]: sentiment_score += 0.33
            if df['ema20'].iloc[-1] > df['ema50'].iloc[-1]: sentiment_score += 0.33
            if df['close'].iloc[-1] > df['ema20'].iloc[-1]: sentiment_score += 0.34
            
            return sentiment_score
            
        except Exception as e:
            if isinstance(e, TechnicalAnalysis.TechnicalAnalysisException):
                raise
            raise TechnicalAnalysis.TechnicalAnalysisException(f"Erreur analyse sentiment: {str(e)}")

    @staticmethod
    def analyze_volume_profile(df: pd.DataFrame) -> float:
        """Analyse le profil volumétrique"""
        try:
            if df is None or df.empty:
                raise TechnicalAnalysis.InvalidDataException("DataFrame vide ou invalide")

            if 'volume' not in df.columns:
                raise TechnicalAnalysis.InvalidDataException("Colonne 'volume' manquante")

            volume_mean = df['volume'].mean()
            if volume_mean == 0:
                raise TechnicalAnalysis.CalculationException("Volume moyen nul")

            recent_volume = df['volume'].iloc[-5:].mean()
            return recent_volume / volume_mean
            
        except Exception as e:
            if isinstance(e, TechnicalAnalysis.TechnicalAnalysisException):
                raise
            raise TechnicalAnalysis.TechnicalAnalysisException(f"Erreur analyse volume: {str(e)}")

# Utilisation
if __name__ == "__main__":
    # Exemple d'utilisation
    analyzer = TechnicalAnalysis()
    try:
        # Création d'un DataFrame de test
        df = pd.DataFrame({
            'close': [100, 101, 102, 101, 103],
            'high': [102, 103, 104, 103, 105],
            'low': [99, 100, 101, 100, 102],
            'volume': [1000, 1100, 1200, 900, 1300]
        })
        
        rsi = analyzer.calculate_rsi(df)
        print(f"RSI: {rsi.iloc[-1]:.2f}")
        
        support, resistance = analyzer.calculate_support_resistance(df)
        print(f"Support: {support:.2f}, Resistance: {resistance:.2f}")
        
        momentum = analyzer.calculate_momentum_score(df)
        print(f"Momentum Score: {momentum:.2f}")
        
    except TechnicalAnalysis.TechnicalAnalysisException as e:
        print(f"Erreur d'analyse technique: {e}")