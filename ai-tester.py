import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, precision_score, recall_score
import plotly.graph_objects as go

class AITester:
    def __init__(self, exchange, ai_predictor):
        self.exchange = exchange
        self.ai_predictor = ai_predictor
        
    def backtest_predictions(self, symbol, days=30):
        """Test les prédictions sur l'historique"""
        try:
            # Récupération des données historiques
            df = calculate_timeframe_data(self.exchange, symbol, '1h', days * 24)
            if df is None:
                return None
                
            # Préparation des prédictions
            predictions = []
            actual_movements = []
            dates = []
            
            # Test sur chaque point
            for i in range(len(df)-24):  # -24 pour garder une fenêtre de prédiction
                window = df.iloc[i:i+24]
                pred = self.ai_predictor.predict_movement(window)
                
                predictions.append(pred['probability'] > 0.5)
                actual_movements.append(df['close'].iloc[i+24] > df['close'].iloc[i+23])
                dates.append(df.index[i+23])
            
            # Calcul des métriques
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
        """Visualise les résultats du backtest"""
        if not results:
            return None
            
        fig = go.Figure()
        
        # Ajout des prédictions correctes et incorrectes
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
