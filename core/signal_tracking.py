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
            'result': None,
            'exit_price': None,
            'exit_timestamp': None,
            'profit_loss': None
        }
        self.signals.append(signal)
        self.signal_stats['total'] += 1
        self.signal_stats['pending'] += 1
    
    def update_signal(self, symbol, current_price):
        """Met à jour le statut d'un signal basé sur le prix actuel"""
        for signal in self.signals:
            if signal['symbol'] == symbol and signal['status'] == 'pending':
                # Vérification du stop loss
                if current_price <= signal['stop_loss']:
                    self._close_signal(signal, current_price, 'failed')
                    continue
                
                # Vérification de la cible
                if current_price >= signal['target_price']:
                    self._close_signal(signal, current_price, 'successful')
    
    def _close_signal(self, signal, exit_price, result):
        """Ferme un signal avec le résultat donné"""
        signal['status'] = 'closed'
        signal['result'] = result
        signal['exit_price'] = exit_price
        signal['exit_timestamp'] = datetime.now()
        signal['profit_loss'] = (
            (exit_price - signal['entry_price']) / signal['entry_price'] * 100
            if signal['type'] == 'BUY'
            else (signal['entry_price'] - exit_price) / signal['entry_price'] * 100
        )
        
        # Mise à jour des statistiques
        self.signal_stats['pending'] -= 1
        if result == 'successful':
            self.signal_stats['successful'] += 1
        else:
            self.signal_stats['failed'] += 1
    
    @property
    def success_rate(self) -> float:
        """Calcule le taux de réussite des signaux terminés"""
        closed_signals = self.signal_stats['successful'] + self.signal_stats['failed']
        if closed_signals == 0:
            return 0.0
        return (self.signal_stats['successful'] / closed_signals) * 100
    
    @property
    def average_profit(self) -> float:
        """Calcule le profit/perte moyen des signaux terminés"""
        closed_signals = [s for s in self.signals if s['status'] == 'closed']
        if not closed_signals:
            return 0.0
        total_pnl = sum(s['profit_loss'] for s in closed_signals if s['profit_loss'] is not None)
        return total_pnl / len(closed_signals)
    
    def get_signal_history(self) -> list:
        """Renvoie l'historique complet des signaux"""
        return self.signals
    
    def get_active_signals(self) -> list:
        """Renvoie les signaux actifs/en attente"""
        return [s for s in self.signals if s['status'] == 'pending']