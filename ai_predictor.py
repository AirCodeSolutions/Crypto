import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import ta
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, precision_score, recall_score
from utils import calculate_timeframe_data

class AIPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.scaler = MinMaxScaler()
        
    def prepare_features(self, df):
        """Prépare les features pour l'IA"""
        features = pd.DataFrame()
        
        features['rsi'] = ta.momentum.rsi(df['close'])
        features['macd'] = ta.trend.macd_diff(df['close'])
        features['volume_change'] = df['volume'].pct_change()
        features['price_change'] = df['close'].pct_change()
        
        features['ema9_trend'] = (df['close'] - ta.trend.ema_indicator(df['close'], window=9)) / df['close']
        features['ema20_trend'] = (df['close'] - ta.trend.ema_indicator(df['close'], window=20)) / df['close']
        
        features['volatility'] = df['close'].rolling(window=20).std() / df['close'].mean()
        
        return self.scaler.fit_transform(features.dropna())
        
    def predict_movement(self, df):
        try:
            features = self.prepare_features(df)
            if len(features) < 2:
                return {'probability': 0, 'confidence': 0}
                
            y = (df['close'].shift(-1) > df['close']).dropna().astype(int)
            if len(y) > len(features):
                y = y[:len(features)]
            
            self.model.fit(features[:-1], y[:-1])
            probability = self.model.predict_proba(features[-1:])
            
            return {
                'probability': probability[0][1],
                'confidence': max(probability[0])
            }
            
        except Exception as e:
            print(f"Erreur de prédiction: {str(e)}")
            return {'probability': 0, 'confidence': 0}

class AITester:
    def __init__(self, exchange, ai_predictor):
        self.exchange = exchange
        self.ai_predictor = ai_predictor
        
    def backtest_predictions(self, symbol, days=30):
        try:
            df = calculate_timeframe_data(self.exchange, symbol, '1h', days * 24)
            if df is None:
                return None
                
            predictions = []
            actual_movements = []
            dates = []
            
            for i in range(len(df)-24):
                window = df.iloc[i:i+24]
                pred = self.ai_predictor.predict_movement(window)
                
                predictions.append(pred['probability'] > 0.5)
                actual_movements.append(df['close'].iloc[i+24] > df['close'].iloc[i+23])
                dates.append(df.index[i+23])
            
            metrics = {
                'accuracy': accuracy_score(actual_movements, predictions),
                'precision': precision_score(actual_movements, predictions),
                'recall': recall_score(actual_movements, predictions)
            }
            
            return {
                'metrics': metrics,
                'predictions': predictions,
                'actual': actual_movements,
                'dates': dates
            }
            
        except Exception as e:
            print(f"Erreur backtest: {str(e)}")
            return None
            
    def visualize_results(self, results, symbol):
        if not results:
            return None
            
        fig = go.Figure()
        
        correct_pred = [i for i in range(len(results['predictions'])) 
                       if results['predictions'][i] == results['actual'][i]]
        incorrect_pred = [i for i in range(len(results['predictions'])) 
                         if results['predictions'][i] != results['actual'][i]]
        
        fig.add_trace(go.Scatter(
            x=[results['dates'][i] for i in correct_pred],
            y=[1 if results['predictions'][i] else 0 for i in correct_pred],
            mode='markers',
            name='Prédictions correctes',
            marker=dict(color='green', size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=[results['dates'][i] for i in incorrect_pred],
            y=[1 if results['predictions'][i] else 0 for i in incorrect_pred],
            mode='markers',
            name='Prédictions incorrectes',
            marker=dict(color='red', size=8)
        ))
        
        fig.update_layout(
            title=f"Résultats des prédictions pour {symbol}",
            xaxis_title="Date",
            yaxis_title="Prédiction (1=Hausse, 0=Baisse)",
            template="plotly_dark"
        )
        
        return fig
```
