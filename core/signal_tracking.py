from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class SignalHistory:
    def __init__(self, airtable_service, user_id):
        self.signals = []
        """Initialise l'historique des signaux avec persistance Airtable"""
        self.airtable = airtable_service
        self.user_id = user_id
        self.signal_stats = self._load_user_performance()
        
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

    def get_success_rate(self, signal_type: str) -> float:
        """Calcule le taux de réussite pour un type de signal donné"""
        signals = [s for s in self.signals if s['type'] == signal_type]
        if not signals:
            return 0.0
        
        successful = len([s for s in signals if s['status'] == 'successful'])
        return (successful / len(signals)) * 100
    

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
    
    def _load_user_performance(self):
        """Charge ou crée les statistiques de l'utilisateur"""
        performance = self.airtable.trading_performance.first(formula=f"user_id = '{self.user_id}'")
        
        if not performance:
            # Si pas de données existantes, créer une nouvelle entrée
            #performance_data = {
            #    "user_id": self.user_id,
            #    "total_signals": 0,
            #    "successful_signals": 0,
            #    "failed_signals": 0,
            #    "total_profit": 0,
            #    "last_updated": datetime.now().isoformat()
            #}
        #log erreur
            try:
                    logger.info(f"Tentative de chargement des performances...")
                    logger.info(f"User ID: {self.user_id}")
                    logger.info(f"Table de performance ID: {self.airtable.trading_performance}")
                    
                    # Version simplifiée sans formule pour tester
                    all_records = self.airtable.trading_performance.all()
                    logger.info(f"Records trouvés: {all_records}")

                    return {
                        "total_signals": 0,
                        "successful_signals": 0,
                        "failed_signals": 0,
                        "total_profit": 0,
                        "last_updated": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                    logger.error(f"Erreur dans _load_user_performance: {str(e)}")
                    # Retourner des valeurs par défaut en cas d'erreur
                    return {
                        "total_signals": 0,
                        "successful_signals": 0,
                        "failed_signals": 0,
                        "total_profit": 0,
                        "last_updated": datetime.now().isoformat()
                    }






            performance_data = {
            'user_id': self.user_id,               # en simple quotes
            'total_signals': '0',                  # en string
            'successful_signals': '0',
            'failed_signals': '0',
            'total_profit': '0',
            'last_updated': datetime.now().isoformat()
            }
            
            self.airtable.trading_performance.create(performance_data)
            return performance_data
        
        return performance['fields']