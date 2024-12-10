import streamlit as st
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Literal

@dataclass
class PriceAlert:
    """Représente une alerte de prix"""
    symbol: str
    target_price: float
    condition: Literal["above", "below"]
    created_at: datetime = field(default_factory=datetime.now)
    triggered: bool = False
    notification_sent: bool = False

class EnhancedAlertSystem:
    def __init__(self):
        """Initialise le système d'alertes"""
        if 'price_alerts' not in st.session_state:
            st.session_state.price_alerts = []
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []

    def add_price_alert(self, symbol: str, target_price: float, condition: Literal["above", "below"]):
        """Ajoute une nouvelle alerte de prix"""
        alert = PriceAlert(
            symbol=symbol,
            target_price=target_price,
            condition=condition
        )
        st.session_state.price_alerts.append(alert)

    def check_alerts(self, symbol: str, current_price: float):
        """Vérifie les alertes pour un symbole donné"""
        for alert in st.session_state.price_alerts:
            if alert.symbol == symbol and not alert.triggered:
                if self._check_price_condition(current_price, alert.target_price, alert.condition):
                    self._trigger_alert(alert, current_price)

    def _check_price_condition(self, current_price: float, target_price: float, condition: str) -> bool:
        """Vérifie si la condition de prix est remplie"""
        if condition == "above":
            return current_price >= target_price
        return current_price <= target_price

    def _trigger_alert(self, alert: PriceAlert, current_price: float):
        """Déclenche l'alerte et crée une notification"""
        alert.triggered = True
        
        # Création de la notification
        condition_text = "dépassé" if alert.condition == "above" else "descendu sous"
        message = f"🔔 {alert.symbol} a {condition_text} {alert.target_price:.4f} USDT (Prix actuel: {current_price:.4f} USDT)"
        
        self.add_notification(
            message=message,
            notification_type="warning" if alert.condition == "below" else "success",
            details={
                "Symbol": alert.symbol,
                "Prix cible": f"{alert.target_price:.4f}",
                "Prix actuel": f"{current_price:.4f}",
                "Condition": "Au-dessus" if alert.condition == "above" else "En-dessous"
            }
        )

    def render_alert_manager(self):
        """Affiche l'interface de gestion des alertes"""
        st.subheader("⚙️ Gestionnaire d'Alertes")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            symbol = st.text_input("Symbole", key="alert_symbol").upper()
        with col2:
            target_price = st.number_input("Prix cible", min_value=0.0, step=0.0001, key="alert_price")
        with col3:
            condition = st.selectbox(
                "Condition",
                options=["above", "below"],
                format_func=lambda x: "Au-dessus" if x == "above" else "En-dessous",
                key="alert_condition"
            )

        if st.button("Ajouter l'alerte"):
            if symbol and target_price > 0:
                self.add_price_alert(symbol, target_price, condition)
                st.success(f"Alerte ajoutée pour {symbol}")

        # Affichage des alertes actives
        st.subheader("🔔 Alertes actives")
        active_alerts = [alert for alert in st.session_state.price_alerts if not alert.triggered]
        
        for alert in active_alerts:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.write(f"**{alert.symbol}**")
                with col2:
                    st.write(f"Prix cible: {alert.target_price:.4f}")
                with col3:
                    st.write("Au-dessus" if alert.condition == "above" else "En-dessous")
                with col4:
                    if st.button("❌", key=f"delete_{alert.symbol}_{alert.target_price}"):
                        st.session_state.price_alerts.remove(alert)
                        st.rerun()