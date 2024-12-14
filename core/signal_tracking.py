import pandas as pd
from datetime import datetime

class SignalHistory:
    def __init__(self):
        self.signals = []
        self.signal_stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'pending': 0
        }
        
    def add_signal(self, symbol, signal_type, entry_price, target_price, stop_loss):
        signal = {
            'symbol': symbol,
            'type': signal_type,  # BUY ou SELL
            'entry_price': entry_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'timestamp': datetime.now(),
            'status': 'pending',
            'result': None
        }
        self.signals.append(signal)
        self.signal_stats['total'] += 1
        self.signal_stats['pending'] += 1


    @property
    def average_profit(self) -> float:
        """Calcule le profit moyen des signaux terminés"""
        completed_signals = [s for s in self.signals if s['status'] != 'pending']
        if not completed_signals:
            return 0.0
        
        total_profit = sum(s.get('result', 0) for s in completed_signals)
        return total_profit / len(completed_signals)

    def get_success_rate(self, signal_type: str) -> float:
        """Calcule le taux de réussite pour un type de signal donné"""
        signals = [s for s in self.signals if s['type'] == signal_type]
        if not signals:
            return 0.0
        
        successful = len([s for s in signals if s['status'] == 'successful'])
        return (successful / len(signals)) * 100

    def update_signal_status(self, symbol: str, current_price: float):
        """Met à jour le statut des signaux en fonction du prix actuel"""
        for signal in self.signals:
            if signal['symbol'] == symbol and signal['status'] == 'pending':
                if signal['type'] == 'BUY':
                    if current_price <= signal['stop_loss']:
                        self._mark_signal_failed(signal, current_price)
                    elif current_price >= signal['target_price']:
                        self._mark_signal_successful(signal, current_price)
                else:  # SELL signal
                    if current_price >= signal['stop_loss']:
                        self._mark_signal_failed(signal, current_price)
                    elif current_price <= signal['target_price']:
                        self._mark_signal_successful(signal, current_price)

    def _mark_signal_successful(self, signal: dict, exit_price: float):
        """Marque un signal comme réussi et calcule le résultat"""
        signal['status'] = 'successful'
        signal['exit_price'] = exit_price
        signal['result'] = self._calculate_profit(signal)
        self.signal_stats['successful'] += 1
        self.signal_stats['pending'] -= 1

    def _mark_signal_failed(self, signal: dict, exit_price: float):
        """Marque un signal comme échoué et calcule la perte"""
        signal['status'] = 'failed'
        signal['exit_price'] = exit_price
        signal['result'] = self._calculate_profit(signal)
        self.signal_stats['failed'] += 1
        self.signal_stats['pending'] -= 1

    def _calculate_profit(self, signal: dict) -> float:
        """Calcule le profit/perte en pourcentage pour un signal"""
        if signal['type'] == 'BUY':
            return ((signal['exit_price'] - signal['entry_price']) / signal['entry_price']) * 100
        else:  # SELL signal
            return ((signal['entry_price'] - signal['exit_price']) / signal['entry_price']) * 100