# interface/components/dashboard_manager.py
import streamlit as st
from typing import Optional
from datetime import datetime

from .alerts import AlertSystem
from .trade_card import TradeCard, TradeCardData
from .chart_components import TradingChart, ChartConfig
from .filter_section import FilterSection, FilterCriteria

class DashboardManager:
    """
    Gestionnaire central pour coordonner tous les composants de l'interface.
    Cette classe permet une communication fluide entre les différents éléments
    et maintient la cohérence de l'interface utilisateur.
    """
    
    def __init__(self):
        """Initialise tous les composants nécessaires au dashboard"""
        # Initialisation des composants principaux
        self.alert_system = AlertSystem()
        self.chart = TradingChart(ChartConfig())
        self.filter_section = FilterSection()
        
        # Initialisation de l'état si nécessaire
        if 'last_analysis_time' not in st.session_state:
            st.session_state.last_analysis_time = None

    def analyze_trading_opportunity(self, symbol: str, data: dict):
        """
        Analyse une opportunité de trading et met à jour tous les composants pertinents
        
        Args:
            symbol: Symbole de la crypto-monnaie
            data: Données d'analyse (prix, indicateurs, etc.)
        """
        try:
            # Création de la carte de trading
            trade_data = TradeCardData(
                symbol=symbol,
                price=data['price'],
                score=data['score'],
                volume=data['volume'],
                change_24h=data['change_24h'],
                stop_loss=data.get('stop_loss'),
                target_1=data.get('target_1'),
                target_2=data.get('target_2'),
                reasons=data.get('reasons', [])
            )
            
            # Génération des alertes basées sur l'analyse
            self._generate_trading_alerts(symbol, data)
            
            # Création et affichage de la carte
            trade_card = TradeCard(trade_data)
            if trade_card.render():
                # Si le bouton "Préparer l'ordre" est cliqué
                self._handle_trade_preparation(symbol, data)
                
        except Exception as e:
            self.alert_system.add_notification(
                f"Erreur lors de l'analyse de {symbol}: {str(e)}",
                "error"
            )

    def _generate_trading_alerts(self, symbol: str, data: dict):
        """
        Génère des alertes basées sur l'analyse technique
        
        Args:
            symbol: Symbole de la crypto-monnaie
            data: Données d'analyse
        """
        # Alerte sur le RSI
        if data.get('rsi', 0) <= 30:
            self.alert_system.add_notification(
                f"RSI en zone de survente sur {symbol}",
                "warning",
                {
                    "RSI": f"{data['rsi']:.1f}",
                    "Prix": f"${data['price']:.4f}"
                }
            )
        
        # Alerte sur le score technique
        if data.get('score', 0) >= 0.8:
            self.alert_system.add_notification(
                f"Configuration technique favorable sur {symbol}",
                "success",
                {
                    "Score": f"{data['score']:.2f}",
                    "Prix": f"${data['price']:.4f}",
                    "Volume": f"${data['volume']/1e6:.1f}M"
                }
            )

    def _handle_trade_preparation(self, symbol: str, data: dict):
        """
        Gère la préparation d'un nouveau trade
        
        Args:
            symbol: Symbole de la crypto-monnaie
            data: Données du trade
        """
        self.alert_system.add_notification(
            f"Trade préparé pour {symbol}",
            "info",
            {
                "Prix d'entrée": f"${data['price']:.4f}",
                "Stop Loss": f"${data.get('stop_loss', 0):.4f}",
                "Target 1": f"${data.get('target_1', 0):.4f}"
            }
        )
        
        # Stockage des données du trade en cours de préparation
        st.session_state.prepared_trade = {
            'symbol': symbol,
            'data': data,
            'timestamp': datetime.now()
        }

    def render_dashboard(self, df, symbol: str):
        """
        Affiche le dashboard complet avec tous les composants
        
        Args:
            df: DataFrame avec les données OHLCV
            symbol: Symbole de la crypto-monnaie
        """
        # Layout en colonnes pour le dashboard
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Graphique principal
            self.chart.render(df, symbol)
        
        with col2:
            # Système d'alertes
            self.alert_system.render()
        
        # Filtres en bas
        st.markdown("---")
        filters = self.filter_section.render()
        
        return filters

    def update_analysis(self, symbol: str, new_data: dict):
        """
        Met à jour l'analyse et génère de nouvelles alertes si nécessaire
        
        Args:
            symbol: Symbole de la crypto-monnaie
            new_data: Nouvelles données d'analyse
        """
        last_price = st.session_state.get(f'last_price_{symbol}', 0)
        current_price = new_data['price']
        
        # Détection des mouvements de prix significatifs
        if last_price > 0:
            price_change = ((current_price - last_price) / last_price) * 100
            if abs(price_change) >= 5:  # Mouvement de 5% ou plus
                alert_type = "success" if price_change > 0 else "warning"
                self.alert_system.add_notification(
                    f"Mouvement significatif sur {symbol}: {price_change:+.2f}%",
                    alert_type,
                    {
                        "Prix précédent": f"${last_price:.4f}",
                        "Prix actuel": f"${current_price:.4f}",
                        "Variation": f"{price_change:+.2f}%"
                    }
                )
        
        # Mise à jour du dernier prix connu
        st.session_state[f'last_price_{symbol}'] = current_price