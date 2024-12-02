# app.py
import streamlit as st
from interface.components.widgets import TimeSelector

def main():
    """Une fonction de test simple pour vérifier le TimeSelector"""
    st.title("Test du Sélecteur de Temps")
    
    # Test du composant TimeSelector
    selected_timeframe = TimeSelector.render("test_selector")
    
    # Affichage du résultat pour vérification
    st.write(f"Vous avez sélectionné : {selected_timeframe}")

if __name__ == "__main__":
    main()