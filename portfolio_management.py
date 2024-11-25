# portfolio.py
import streamlit as st
from datetime import datetime
import pandas as pd

class PortfolioManager:
    def __init__(self, exchange):
        self.exchange = exchange
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = {
                'positions': {},  # Positions ouvertes
                'history': [],    # Historique des trades
                'capital': 0,     # Capital initial
                'current_capital': 0,  # Capital actuel
                'performance': {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'total_profit': 0,
                    'max_drawdown': 0
                }
            }

    def add_position(self, symbol, amount, entry_price, stop_loss, target_1, target_2):
        """Ajoute une nouvelle position"""
        try:
            # Vérification du capital disponible
            position_cost = amount * entry_price
            if position_cost > st.session_state.portfolio['current_capital']:
                return False, "Capital insuffisant"

            position = {
                'symbol': symbol,
                'amount': float(amount),
                'entry_price': float(entry_price),
                'current_price': float(entry_price),
                'stop_loss': float(stop_loss),
                'target_1': float(target_1),
                'target_2': float(target_2),
                'entry_date': datetime.now(),
                'pnl': 0,
                'status': 'open',
                'partial_exits': []
            }
            
            st.session_state.portfolio['positions'][symbol] = position
            st.session_state.portfolio['current_capital'] -= position_cost
            return True, "Position ajoutée avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de l'ajout de la position: {str(e)}"

    def update_positions(self):
        """Met à jour toutes les positions ouvertes"""
        for symbol in list(st.session_state.portfolio['positions'].keys()):
            try:
                position = st.session_state.portfolio['positions'][symbol]
                ticker = self.exchange.fetch_ticker(f"{symbol}/USDT")
                current_price = ticker['last']
                
                # Mise à jour du prix et du PnL
                position['current_price'] = current_price
                position['pnl'] = (
                    (current_price - position['entry_price']) / 
                    position['entry_price']
                ) * 100

                # Vérification des stops et targets
                self._check_exit_conditions(symbol, current_price)
                
            except Exception as e:
                st.error(f"Erreur mise à jour {symbol}: {str(e)}")

    def _check_exit_conditions(self, symbol, current_price):
        """Vérifie les conditions de sortie"""
        position = st.session_state.portfolio['positions'][symbol]
        
        # Stop Loss
        if current_price <= position['stop_loss']:
            self.close_position(symbol, current_price, "Stop Loss")
            
        # Target 1 (sortie partielle)
        elif current_price >= position['target_1'] and not position.get('target1_hit'):
            position['target1_hit'] = True
            self.partial_exit(symbol, current_price, 0.5, "Target 1")
            # Ajuster le stop loss au point d'entrée
            position['stop_loss'] = position['entry_price']
            
        # Target 2 (sortie complète)
        elif current_price >= position['target_2']:
            self.close_position(symbol, current_price, "Target 2")

    def partial_exit(self, symbol, exit_price, exit_percentage, reason):
        """Effectue une sortie partielle de position"""
        position = st.session_state.portfolio['positions'][symbol]
        exit_amount = position['amount'] * exit_percentage
        
        partial_exit = {
            'date': datetime.now(),
            'price': exit_price,
            'amount': exit_amount,
            'pnl': ((exit_price - position['entry_price']) / position['entry_price']) * 100,
            'reason': reason
        }
        
        position['partial_exits'].append(partial_exit)
        position['amount'] -= exit_amount

    def close_position(self, symbol, exit_price, reason):
        """Ferme une position complètement"""
        if symbol in st.session_state.portfolio['positions']:
            position = st.session_state.portfolio['positions'][symbol]
            
            # Calcul du P&L final
            pnl = ((exit_price - position['entry_price']) / position['entry_price']) * 100
            
            # Mise à jour du capital
            exit_value = position['amount'] * exit_price
            st.session_state.portfolio['current_capital'] += exit_value
            
            # Création de l'enregistrement historique
            trade_record = {
                'symbol': symbol,
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'amount': position['amount'],
                'pnl': pnl,
                'entry_date': position['entry_date'],
                'exit_date': datetime.now(),
                'duration': str(datetime.now() - position['entry_date']),
                'reason': reason,
                'partial_exits': position['partial_exits']
            }
            
            # Mise à jour des statistiques
            self._update_statistics(pnl)
            
            # Ajout à l'historique et suppression de la position
            st.session_state.portfolio['history'].append(trade_record)
            del st.session_state.portfolio['positions'][symbol]

    def _update_statistics(self, pnl):
        """Met à jour les statistiques du portfolio"""
        stats = st.session_state.portfolio['performance']
        stats['total_trades'] += 1
        if pnl > 0:
            stats['winning_trades'] += 1
        stats['total_profit'] += pnl
        
        # Calcul du drawdown
        if pnl < 0:
            current_drawdown = abs(pnl)
            stats['max_drawdown'] = max(stats['max_drawdown'], current_drawdown)

    def get_portfolio_summary(self):
        """Génère un résumé du portfolio"""
        performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit': 0,
            'max_drawdown': 0
        } if 'performance' not in st.session_state.portfolio else st.session_state.portfolio['performance']
        
        capital_initial = st.session_state.portfolio['capital']
        capital_actuel = st.session_state.portfolio['current_capital']
        
        # Calcul du win rate
        win_rate = (performance['winning_trades'] / performance['total_trades'] * 100) if performance['total_trades'] > 0 else 0
        
        # Calcul de la performance en pourcentage
        perf = ((capital_actuel / capital_initial - 1) * 100) if capital_initial > 0 else 0
        
        return {
            'capital_initial': capital_initial,
            'capital_actuel': capital_actuel,
            'profit_total': performance['total_profit'],
            'nombre_trades': performance['total_trades'],
            'win_rate': win_rate,
            'max_drawdown': performance['max_drawdown'],
            'positions_ouvertes': len(st.session_state.portfolio['positions']),
            'performance': perf
        }
    def get_trade_history(self):
        """Retourne l'historique des trades sous forme de DataFrame"""
        if not st.session_state.portfolio['history']:
            return pd.DataFrame()
            
        return pd.DataFrame(st.session_state.portfolio['history'])

    def get_open_positions(self):
        """Retourne les positions ouvertes sous forme de DataFrame"""
        if not st.session_state.portfolio['positions']:
            return pd.DataFrame()
            
        positions = []
        for symbol, pos in st.session_state.portfolio['positions'].items():
            positions.append({
                'symbol': symbol,
                'amount': pos['amount'],
                'entry_price': pos['entry_price'],
                'current_price': pos['current_price'],
                'pnl': pos['pnl'],
                'stop_loss': pos['stop_loss'],
                'target_1': pos['target_1'],
                'target_2': pos['target_2']
            })
        
        return pd.DataFrame(positions)
