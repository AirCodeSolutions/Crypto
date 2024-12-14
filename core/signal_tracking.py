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