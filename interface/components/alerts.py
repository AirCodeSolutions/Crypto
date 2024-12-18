# interface/components/alerts.py
import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Literal
from datetime import datetime
import time

@dataclass
class NotificationMessage:
    """Représente une notification ou une alerte"""
    message: str
    type: Literal["info", "success", "warning", "error"]
    timestamp: datetime = field(default_factory=datetime.now)
    is_read: bool = False
    details: Optional[Dict] = None
    def format_time(self) -> str:
            """Formate le timestamp pour l'affichage"""
            now = datetime.now()
            delta = now - self.timestamp
            
            if delta.days > 0:
                return f"Il y a {delta.days} jours"
            elif delta.seconds > 3600:
                return f"Il y a {delta.seconds // 3600}h"
            elif delta.seconds > 60:
                return f"Il y a {delta.seconds // 60}m"
            else:
                return "À l'instant"



@dataclass
class PriceAlert:
    """Représente une alerte de prix"""
    symbol: str
    target_price: float
    condition: Literal["above", "below"]
    created_at: datetime = field(default_factory=datetime.now)
    triggered: bool = False

class AlertSystem:
    """Système de gestion des alertes et notifications."""
    
    def __init__(self):
        """Initialise le système d'alertes"""
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        if 'price_alerts' not in st.session_state:
            st.session_state.price_alerts = []
    
    def add_notification(
        self,
        message: str,
        notification_type: Literal["info", "success", "warning", "error"],
        details: Optional[Dict] = None
    ):
        """Ajoute une nouvelle notification"""
        notification = NotificationMessage(
            message=message,
            type=notification_type,
            details=details
        )
        st.session_state.notifications.insert(0, notification)

    def add_price_alert(self, symbol: str, target_price: float, condition: Literal["above", "below"]):
        """Ajoute une nouvelle alerte de prix"""
        alert = PriceAlert(
            symbol=symbol,
            target_price=target_price,
            condition=condition
        )
        st.session_state.price_alerts.append(alert)
        
        # Notification de confirmation
        self.add_notification(
            f"Alerte configurée pour {symbol} à ${target_price:.4f}",
            "info",
            {"Prix cible": f"${target_price:.4f}", "Condition": "Au-dessus" if condition == "above" else "En-dessous"}
        )
    
    def check_alerts(self, symbol: str, current_price: float):
        """Vérifie les alertes de prix pour un symbole donné"""
        for alert in st.session_state.price_alerts:
            if alert.symbol == symbol and not alert.triggered:
                if self._check_price_condition(current_price, alert):
                    self._trigger_alert(alert, current_price)

    def _check_price_condition(self, current_price: float, alert: PriceAlert) -> bool:
        """Vérifie si la condition de prix est remplie"""
        if alert.condition == "above":
            return current_price >= alert.target_price
        return current_price <= alert.target_price

    def _trigger_alert(self, alert: PriceAlert, current_price: float):
        """Déclenche l'alerte et crée une notification"""
        alert.triggered = True
        condition_text = "dépassé" if alert.condition == "above" else "descendu sous"
        
        self.add_notification(
            f"🎯 {alert.symbol} a {condition_text} {alert.target_price:.4f} USDT",
            "success" if alert.condition == "above" else "warning",
            {
                "Prix cible": f"${alert.target_price:.4f}",
                "Prix actuel": f"${current_price:.4f}"
            }
        )
    
    def clear_all(self):
        """Efface toutes les notifications et alertes"""
        st.session_state.notifications = []
        st.session_state.price_alerts = []
    
    def mark_all_as_read(self):
        """Marque toutes les notifications comme lues"""
        for notif in st.session_state.notifications:
            notif.is_read = True
    
    def get_unread_count(self) -> int:
        """Retourne le nombre de notifications non lues"""
        return sum(1 for n in st.session_state.notifications if not n.is_read)

    def render(self):
        """Affiche l'interface des notifications et alertes"""
        # En-tête avec compteur
        unread = self.get_unread_count()
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### 🔔 Notifications ({unread} non lues)")
        
        with col2:
            if st.button("Tout marquer comme lu"):
                self.mark_all_as_read()
                
        with col3:
            if st.button("Effacer tout"):
                self.clear_all()
        
        # Affichage des alertes actives
        active_alerts = [alert for alert in st.session_state.price_alerts if not alert.triggered]
        if active_alerts:
            st.markdown("#### ⏰ Alertes actives")
            for alert in active_alerts:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{alert.symbol}**")
                    with col2:
                        condition = "Au-dessus" if alert.condition == "above" else "En-dessous"
                        st.write(f"{condition} de {alert.target_price:.4f}")
                    with col3:
                        if st.button("❌", key=f"delete_{alert.symbol}_{alert.target_price}"):
                            st.session_state.price_alerts.remove(alert)
                            st.rerun()
        
        # Affichage des notifications
        if not st.session_state.notifications:
            st.info("Aucune notification")
            return
        
        for notification in st.session_state.notifications:
            self._render_notification(notification)
    
    def _render_notification(self, notification: NotificationMessage):
        """Affiche une notification individuelle"""
        styles = {
            "info": {"icon": "ℹ️", "color": "blue"},
            "success": {"icon": "✅", "color": "green"},
            "warning": {"icon": "⚠️", "color": "orange"},
            "error": {"icon": "❌", "color": "red"}
        }
        
        style = styles[notification.type]
        
        with st.container():
            st.markdown(
                f"""
                <div style='padding: 10px; border-left: 3px solid {style['color']}; margin: 5px 0;'>
                    {style['icon']} {notification.message}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(notification.format_time())
            
            if notification.details:
                with st.expander("Voir les détails"):
                    for key, value in notification.details.items():
                        st.write(f"**{key}:** {value}")
            
            if not notification.is_read:
                notification.is_read = True

    def check_rsi_alert(self, symbol: str, rsi_value: float):
        """Vérifie les seuils RSI et ajoute une notification si nécessaire."""
        if rsi_value < 30:
            self.add_notification(
                f"RSI de {symbol} est inférieur à 30 (survendu)",
                "warning",
                {"RSI": rsi_value}
            )
            print(f"Notification RSI ajoutée : {symbol} - RSI {rsi_value} (survendu)")
        elif rsi_value > 70:
            self.add_notification(
                f"RSI de {symbol} est supérieur à 70 (suracheté)",
                "warning",
                {"RSI": rsi_value}
            )
            print(f"Notification RSI ajoutée : {symbol} - RSI {rsi_value} (suracheté)")
        else:
            print(f"Aucune notification RSI : {symbol} - RSI {rsi_value}")
    
    def check_ema_crossover(self, symbol: str, short_ema: float, long_ema: float):
    """Vérifie les croisements EMA et ajoute une notification si nécessaire."""
    # Vérifie si une notification similaire existe déjà
    existing_notifications = [
        notif for notif in st.session_state.get('notifications', [])
        if f"Croisement EMA détecté pour {symbol}" in notif['message']
    ]

    if short_ema > long_ema and not any("Croisement haussier" in notif['message'] for notif in existing_notifications):
        self.add_notification(
            f"Croisement haussier EMA détecté pour {symbol}",
            "success",
            {"EMA Court": short_ema, "EMA Long": long_ema}
        )
    elif short_ema < long_ema and not any("Croisement baissier" in notif['message'] for notif in existing_notifications):
        self.add_notification(
            f"Croisement baissier EMA détecté pour {symbol}",
            "warning",
            {"EMA Court": short_ema, "EMA Long": long_ema}
        )

    def notify_pattern(self, symbol: str, pattern_name: str, details: Optional[Dict] = None):
        self.add_notification(
            f"Pattern détecté pour {symbol}: {pattern_name}",
            "info",
            details
        )