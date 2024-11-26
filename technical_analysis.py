# indicators.py
import pandas as pd
import numpy as np
import ta

class TechnicalAnalysis:
    @staticmethod
    def calculate_rsi(df, periods=14):
        """Calcule le RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_support_resistance(df, window=20):
        """Calcule les niveaux de support et résistance"""
        rolling_min = df['low'].rolling(window=window).min()
        rolling_max = df['high'].rolling(window=window).max()
        return rolling_min.iloc[-1], rolling_max.iloc[-1]

    @staticmethod
    def detect_divergence(price_data, rsi_data, window=14):
        """Détecte les divergences prix/RSI"""
        price_peaks = pd.Series(price_data).rolling(window, center=True).apply(
            lambda x: 1 if x.iloc[len(x)//2] == max(x) else (
                -1 if x.iloc[len(x)//2] == min(x) else 0
            )
        )
        rsi_peaks = pd.Series(rsi_data).rolling(window, center=True).apply(
            lambda x: 1 if x.iloc[len(x)//2] == max(x) else (
                -1 if x.iloc[len(x)//2] == min(x) else 0
            )
        )
        return price_peaks != rsi_peaks

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def analyze_volume_profile(df):
        """Analyse le profil volumétrique"""
        volume_mean = df['volume'].mean()
        recent_volume = df['volume'].iloc[-5:].mean()
        return recent_volume / volume_mean

    @staticmethod
    def detect_trend_reversal(df):
        """Détecte les potentiels retournements de tendance"""
        signals = []
        
        # Patterns de chandeliers
        df['doji'] = ta.candlestick.doji(df['open'], df['high'], df['low'], df['close'])
        df['hammer'] = ta.candlestick.hammer(df['open'], df['high'], df['low'], df['close'])
        df['shooting_star'] = ta.candlestick.shooting_star(df['open'], df['high'], df['low'], df['close'])
        
        if df['doji'].iloc[-1]: signals.append("Doji")
        if df['hammer'].iloc[-1]: signals.append("Hammer")
        if df['shooting_star'].iloc[-1]: signals.append("Shooting Star")
        
        return signals

class SignalGenerator:
    def __init__(self, df, current_price):
        self.df = df
        self.current_price = current_price
        self.ta = TechnicalAnalysis()

    def generate_trading_signals(self):
        """
        Génère les signaux de trading complets
        """
        signals = {
            'action': None,
            'strength': 0,
            'entry_price': None,
            'stop_loss': None,
            'target_1': None,
            'target_2': None,
            'reasons': []
        }

        # Calcul des indicateurs
        rsi = self.ta.calculate_rsi(self.df).iloc[-1]
        macd = ta.trend.macd_diff(self.df['close'])
        volume_trend = self.ta.analyze_volume_profile(self.df)
        
        # Conditions d'achat
        buy_conditions = (
            30 <= rsi <= 40 and
            macd.iloc[-1] > macd.iloc[-2] and
            volume_trend > 1
        )
        
        # Conditions de vente
        sell_conditions = (
            rsi >= 70 or
            (macd.iloc[-1] < macd.iloc[-2] and self.current_price >= self.df['close'].mean())
        )

        if buy_conditions:
            signals.update({
                'action': 'BUY',
                'strength': min((40 - rsi) / 10 * 0.5 + volume_trend * 0.5, 1),
                'entry_price': self.current_price,
                'stop_loss': self.current_price * 0.99,
                'target_1': self.current_price * 1.02,
                'target_2': self.current_price * 1.03,
                'reasons': [
                    "RSI en zone de survente",
                    "MACD en reprise",
                    "Volume confirmant"
                ]
            })
        elif sell_conditions:
            signals.update({
                'action': 'SELL',
                'strength': min((rsi - 70) / 10 * 0.5 + volume_trend * 0.5, 1),
                'reasons': [
                    "RSI en zone de surachat" if rsi >= 70 else "Objectif atteint",
                    "MACD baissier",
                    "Volume significatif"
                ]
            })

        return signals

    def calculate_opportunity_score(self):
        """
        Calcule un score global pour l'opportunité
        """
        # Prix actuel en tendance haussière par rapport aux EMAs ?
        df = self.df.copy()
        df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
        df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
        
        trend_score = 0
        if df['close'].iloc[-1] > df['ema9'].iloc[-1] > df['ema20'].iloc[-1]:
            trend_score = 0.4
        elif df['close'].iloc[-1] > df['ema20'].iloc[-1]:
            trend_score = 0.2
            
        # RSI dans une zone intéressante ?
        rsi = ta.momentum.rsi(df['close']).iloc[-1]
        rsi_score = 0
        if 30 <= rsi <= 40:  # Zone de survente
            rsi_score = 0.3
        elif 40 < rsi <= 60:  # Zone neutre
            rsi_score = 0.2
            
        # Volume significatif ?
        volume_sma = df['volume'].rolling(window=20).mean().iloc[-1]
        volume_score = 0
        if df['volume'].iloc[-1] > volume_sma * 1.5:
            volume_score = 0.3
        elif df['volume'].iloc[-1] > volume_sma:
            volume_score = 0.2
            
        # Score final
        final_score = trend_score + rsi_score + volume_score
        
        return min(final_score, 1.0)  # Score maximum de 1.0
