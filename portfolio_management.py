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
    def _add_position_form(self):
    with st.expander("➕ Ajouter une nouvelle position"):
        # Première ligne : Symbole et Prix d'entrée
        col1, col2 = st.columns(2)
        with col1:
            new_symbol = st.text_input("Symbole (ex: BTC)", "").upper()
            amount = st.number_input("Montant (USDT)", min_value=0.0, value=100.0)
        with col2:
            entry_price = st.number_input("Prix d'entrée", min_value=0.0, value=0.0, format="%.8f")
        
        # Calculateur d'aide
        st.markdown("---")
        st.markdown("### 🎯 Calculateur de niveaux")
        
        col1, col2 = st.columns(2)
        with col1:
            risk_percentage = st.slider(
                "Risque acceptable (%)", 
                min_value=0.5, 
                max_value=5.0, 
                value=1.5,
                step=0.5,
                help="Pourcentage de perte maximale acceptable"
            )
        with col2:
            risk_reward = st.slider(
                "Ratio Risque/Récompense", 
                min_value=1.5, 
                max_value=5.0, 
                value=2.0,
                step=0.5,
                help="Ratio entre profit potentiel et risque"
            )

        if entry_price > 0:
            # Calcul des niveaux suggérés
            stop_loss = entry_price * (1 - risk_percentage/100)
            risk_amount = entry_price - stop_loss
            target_1 = entry_price + (risk_amount * risk_reward)
            target_2 = entry_price + (risk_amount * (risk_reward * 1.5))

            # Affichage des niveaux calculés
            st.markdown("#### Niveaux suggérés:")
            col1, col2, col3 = st.columns(3)
            with col1:
                suggested_sl = st.metric(
                    "Stop Loss suggéré",
                    f"{stop_loss:.8f}",
                    f"{-risk_percentage:.1f}%"
                )
            with col2:
                suggested_t1 = st.metric(
                    "Target 1 suggéré",
                    f"{target_1:.8f}",
                    f"+{risk_percentage * risk_reward:.1f}%"
                )
            with col3:
                suggested_t2 = st.metric(
                    "Target 2 suggéré",
                    f"{target_2:.8f}",
                    f"+{risk_percentage * risk_reward * 1.5:.1f}%"
                )

            # Champs pour les niveaux réels
            st.markdown("---")
            st.markdown("### 📊 Niveaux de la position")
            col1, col2, col3 = st.columns(3)
            with col1:
                stop_loss = st.number_input(
                    "Stop Loss", 
                    min_value=0.0, 
                    value=float(stop_loss), 
                    format="%.8f",
                    help="Niveau de stop loss en USDT"
                )
            with col2:
                target_1 = st.number_input(
                    "Target 1", 
                    min_value=0.0, 
                    value=float(target_1), 
                    format="%.8f",
                    help="Premier objectif de profit"
                )
            with col3:
                target_2 = st.number_input(
                    "Target 2", 
                    min_value=0.0, 
                    value=float(target_2), 
                    format="%.8f",
                    help="Second objectif de profit"
                )

            # Calcul des métriques de la position
            if amount > 0:
                potential_loss = (stop_loss - entry_price) * (amount / entry_price)
                potential_profit_1 = (target_1 - entry_price) * (amount / entry_price)
                potential_profit_2 = (target_2 - entry_price) * (amount / entry_price)

                st.markdown("#### Analyse de la position")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Perte maximale",
                        f"{potential_loss:.2f} USDT",
                        f"{(potential_loss/amount)*100:.1f}% du capital"
                    )
                with col2:
                    st.metric(
                        "Profit potentiel (T2)",
                        f"{potential_profit_2:.2f} USDT",
                        f"{(potential_profit_2/amount)*100:.1f}% du capital"
                    )

            # Bouton d'ajout
            st.markdown("---")
            if st.button("Ajouter la position", type="primary"):
                self._handle_new_position(new_symbol, amount, entry_price, stop_loss, target_1, target_2)

        else:
            st.info("Entrez un prix d'entrée pour voir les niveaux suggérés")
            
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
