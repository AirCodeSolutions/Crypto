import tkinter as tk
from tkinter import ttk, scrolledtext
import ccxt
import pandas as pd
import threading
import time
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List

class CryptoAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Analyseur de Crypto-monnaies")
        self.root.geometry("1200x800")  # Fenêtre plus grande
        
        self.exchange = ccxt.binance()
        self.monitoring = False
        self.monitoring_thread = None
        self.tracked_coins = set()
        
        # Liste des principales cryptos à surveiller
        self.major_coins = ['BTC', 'ETH', 'BNB', 'XRP', 'SOL', 'DOT', 'AVAX', 'MATIC']
        
        self.create_gui()
        
    def create_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Onglets
        main_frame = ttk.Frame(notebook, padding="10")
        help_frame = ttk.Frame(notebook, padding="10")
        performance_frame = ttk.Frame(notebook, padding="10")
        short_term_frame = ttk.Frame(notebook, padding="10")
        historical_frame = ttk.Frame(notebook, padding="10")  # Nouvel onglet
        
        notebook.add(main_frame, text="Analyse")
        notebook.add(help_frame, text="Guide & Explications")
        notebook.add(performance_frame, text="Top Performances")
        notebook.add(short_term_frame, text="Opportunités Court Terme")
        notebook.add(historical_frame, text="Analyse Historique")  # Ajout du nouvel onglet
        
        self.setup_main_tab(main_frame)
        self.setup_help_tab(help_frame)
        self.setup_performance_tab(performance_frame)
        self.setup_short_term_tab(short_term_frame)
        self.setup_historical_tab(historical_frame)  # Configuration du nouvel onglet

    def setup_main_tab(self, main_frame):
        # Zone de saisie
        input_frame = ttk.LabelFrame(main_frame, text="Ajouter une crypto", padding="5")
        input_frame.pack(fill='x', pady=5)
        
        self.coin_entry = ttk.Entry(input_frame, width=20)
        self.coin_entry.pack(side='left', padx=5)
        
        ttk.Button(input_frame, text="Ajouter", command=self.add_coin).pack(side='left', padx=5)
        ttk.Button(input_frame, text="Supprimer", command=self.remove_coin).pack(side='left', padx=5)
        
        # Liste des cryptos suivies
        tracked_frame = ttk.LabelFrame(main_frame, text="Cryptos suivies", padding="5")
        tracked_frame.pack(fill='x', pady=5)
        
        self.tracked_listbox = tk.Listbox(tracked_frame, height=3)
        self.tracked_listbox.pack(fill='x')
        
        # Zone d'affichage des analyses
        output_frame = ttk.LabelFrame(main_frame, text="Analyses et Recommandations", padding="5")
        output_frame.pack(fill='both', expand=True, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=20)
        self.output_text.pack(fill='both', expand=True)
        
        # Boutons de contrôle
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Démarrer l'analyse", command=self.start_monitoring)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Arrêter", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side='left', padx=5)

    def setup_help_tab(self, help_frame):
        help_text = scrolledtext.ScrolledText(help_frame, height=30)
        help_text.pack(fill='both', expand=True)
        
        guide = """
    GUIDE DE L'ANALYSEUR DE CRYPTO-MONNAIES

    1. RSI (Relative Strength Index) :
    ---------------------------------
    • Qu'est-ce que c'est ?
      - Un indicateur technique qui mesure la vitesse et l'ampleur des mouvements de prix
      - Varie de 0 à 100

    • Comment l'interpréter ?
      - RSI > 70 : Signal de survente (risque de baisse)
      - RSI < 30 : Signal de surachat (opportunité d'achat potentielle)
      - Entre 30-70 : Zone neutre

    2. Indicateurs Clés de Trading :
    -------------------------------
    • Volume :
      - Définition : Quantité totale d'une crypto échangée sur une période donnée (en USDT)
      - Importance :
        * Un volume élevé = beaucoup de transactions = marché actif
        * Un volume faible = peu de transactions = marché peu liquide
      - Comment l'utiliser :
        * Volume en hausse = confirme la tendance
        * Volume en baisse = possible changement de tendance
        * Volume minimum recommandé : 100,000 USDT pour les débutants

    • Variation :
      - Définition : Pourcentage de changement du prix sur une période donnée
      - Calcul : ((Prix final - Prix initial) / Prix initial) × 100
      - Types de variations :
        * Positive : Le prix a augmenté
        * Négative : Le prix a baissé
      - Exemple :
        * Si une crypto passe de 100€ à 110€ → variation de +10%
        * Si une crypto passe de 100€ à 90€ → variation de -10%

    • Volatilité :
      - Définition : Mesure de l'ampleur des variations de prix
      - Caractéristiques :
        * Forte volatilité = variations importantes et rapides
        * Faible volatilité = variations limitées et plus lentes
      - Implications :
        * Plus de volatilité = plus d'opportunités mais plus de risques
        * Moins de volatilité = plus de stabilité mais moins d'opportunités
      - Conseil : Les débutants devraient commencer avec des cryptos moins volatiles

    3. Horizons Temporels :
    ----------------------
    • Court Terme (quelques heures à quelques jours)
      - Trading actif et fréquent
      - Risque plus élevé
      - Nécessite une surveillance constante
      - Adapté aux traders expérimentés

    • Moyen Terme (quelques semaines à quelques mois)
      - Trading moins intensif
      - Risque modéré
      - Surveillance régulière mais pas constante
      - Bon compromis pour débutants

    • Long Terme (plusieurs mois à plusieurs années)
      - Stratégie "buy and hold"
      - Risque plus faible sur la durée
      - Surveillance périodique
      - Idéal pour l'investissement passif

    4. Conseils de Trading :
    -----------------------
    • Gestion du Risque
      - Ne jamais investir plus que ce que vous pouvez perdre
      - Diversifier vos investissements
      - Utiliser des ordres stop-loss
      - Commencer petit et augmenter progressivement

    • Pour les Débutants
      - Commencer avec les cryptos majeures (BTC, ETH)
      - Privilégier les volumes importants (>100,000 USDT)
      - Éviter les cryptos très volatiles au début
      - Ne pas faire de trading sur effet de levier

    • Bonnes Pratiques
      - Faire vos propres recherches avant d'investir
      - Ne pas trader sous le coup de l'émotion
      - Tenir un journal de trading
      - Définir une stratégie claire et s'y tenir

    5. Utilisation de l'Outil :
    --------------------------
    • Onglet Analyse
      - Suivre vos cryptos favorites
      - Recevoir des alertes et recommandations
      - Voir les analyses en temps réel

    • Onglet Opportunités Court Terme
      - Filtrer par variation minimum
      - Vérifier les volumes
      - Observer les signaux d'achat/vente

    • Onglet Analyse Historique
      - Étudier les performances passées
      - Identifier les meilleurs moments de trading
      - Analyser les patterns récurrents

    6. Comprendre les Signaux :
    --------------------------
    • Signal d'Achat Fort :
      - RSI < 30
      - Volume en hausse
      - Tendance haussière confirmée

    • Signal de Vente Fort :
      - RSI > 70
      - Volume en hausse
      - Tendance baissière confirmée

    • Moments Propices au Trading :
      - Observer les périodes de forte activité
      - Éviter les périodes de faible volume
      - Tenir compte des fuseaux horaires des marchés principaux
    """
        help_text.insert(tk.END, guide)
        help_text.configure(state='disabled')

    def setup_performance_tab(self, performance_frame):
        self.performance_text = scrolledtext.ScrolledText(performance_frame, height=30)
        self.performance_text.pack(fill='both', expand=True)
        
        refresh_button = ttk.Button(performance_frame, text="Rafraîchir", command=self.update_top_performers)
        refresh_button.pack(pady=5)

    def setup_short_term_tab(self, short_term_frame):
        # Zone d'affichage des opportunités court terme
        self.short_term_text = scrolledtext.ScrolledText(short_term_frame, height=30)
        self.short_term_text.pack(fill='both', expand=True)
        
        # Bouton de rafraîchissement
        refresh_button = ttk.Button(short_term_frame, text="Rafraîchir Opportunités", 
                                  command=self.update_short_term_opportunities)
        refresh_button.pack(pady=5)
        
        # Paramètres de filtrage
        filter_frame = ttk.LabelFrame(short_term_frame, text="Filtres", padding="5")
        filter_frame.pack(fill='x', pady=5)
        
        ttk.Label(filter_frame, text="Variation min (%):").pack(side='left', padx=5)
        self.var_threshold = ttk.Entry(filter_frame, width=10)
        self.var_threshold.insert(0, "1")  # Changé de 3 à 1 (variation minimum de 1%)
        self.var_threshold.pack(side='left', padx=5)
    
        ttk.Label(filter_frame, text="Volume min (USDT):").pack(side='left', padx=5)
        self.volume_threshold = ttk.Entry(filter_frame, width=15)
        self.volume_threshold.insert(0, "100000")  # Changé de 1000000 à 100000
        self.volume_threshold.pack(side='left', padx=5)

    def get_short_term_opportunities(self):
        try:
            markets = self.exchange.load_markets()
            opportunities = []
            
            min_variation = float(self.var_threshold.get())
            min_volume = float(self.volume_threshold.get())
            
            for symbol in markets:
                if symbol.endswith('/USDT'):
                    try:
                        ticker = self.exchange.fetch_ticker(symbol)
                        
                        # Récupération des données sur différentes périodes
                        ohlcv_short = self.exchange.fetch_ohlcv(symbol, '15m', limit=24)  # 6h
                        ohlcv_7h = self.exchange.fetch_ohlcv(symbol, '15m', limit=28)    # 7h
                        ohlcv_24h = self.exchange.fetch_ohlcv(symbol, '1h', limit=24)    # 24h
                        
                        if ticker['quoteVolume'] < min_volume:
                            continue
                                
                        # DataFrame pour chaque période
                        df_short = pd.DataFrame(ohlcv_short, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_7h = pd.DataFrame(ohlcv_7h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df_24h = pd.DataFrame(ohlcv_24h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        
                        # Calcul des variations sur différentes périodes
                        price_change_1h = ((df_short['close'].iloc[-1] - df_short['close'].iloc[-4]) / df_short['close'].iloc[-4]) * 100
                        price_change_7h = ((df_7h['close'].iloc[-1] - df_7h['close'].iloc[0]) / df_7h['close'].iloc[0]) * 100
                        price_change_24h = ((df_24h['close'].iloc[-1] - df_24h['close'].iloc[0]) / df_24h['close'].iloc[0]) * 100
                        
                        vol_change = (df_short['volume'].iloc[-1] / df_short['volume'].mean()) * 100
                        
                        # RSI court terme
                        delta = df_short['close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=6).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=6).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        current_rsi = rsi.iloc[-1]
                        
                        # Détection des opportunités
                        if abs(price_change_1h) >= min_variation:
                            signal = "ACHAT" if price_change_1h > 0 else "VENTE"
                            if (signal == "ACHAT" and current_rsi < 70) or (signal == "VENTE" and current_rsi > 30):
                                opportunities.append({
                                    'symbol': symbol.replace('/USDT', ''),
                                    'price_change_1h': price_change_1h,
                                    'price_change_7h': price_change_7h,
                                    'price_change_24h': price_change_24h,
                                    'volume_change': vol_change,
                                    'rsi': current_rsi,
                                    'signal': signal,
                                    'price': ticker['last'],
                                    'volume': ticker['quoteVolume']
                                })
                    except Exception as e:
                        print(f"Erreur pour {symbol}: {str(e)}")
                        continue
            
            # Tri des opportunités par variation 1h
            return sorted(opportunities, key=lambda x: abs(x['price_change_1h']), reverse=True)
        
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def update_top_performers(self):
        self.performance_text.delete(1.0, tk.END)
        self.performance_text.insert(tk.END, "Analyse des meilleures performances...\n\n")
        
        try:
            performances = []
            for coin in self.major_coins:
                try:
                    ticker = self.exchange.fetch_ticker(f"{coin}/USDT")
                    # Vérification que toutes les données sont présentes et valides
                    if ticker and 'last' in ticker and 'percentage' in ticker and 'quoteVolume' in ticker:
                        if ticker['last'] is not None and ticker['percentage'] is not None and ticker['quoteVolume'] is not None:
                            performance = {
                                'symbol': coin,
                                'price': float(ticker['last']),
                                'change_24h': float(ticker['percentage']) if ticker['percentage'] else 0.0,
                                'volume': float(ticker['quoteVolume'])
                            }
                            performances.append(performance)
                except Exception as e:
                    self.performance_text.insert(tk.END, f"Erreur pour {coin}: {str(e)}\n")
                    continue

            if not performances:
                self.performance_text.insert(tk.END, "Aucune donnée de performance disponible\n")
                return

            # Tri sécurisé avec gestion des erreurs
            try:
                performances.sort(key=lambda x: x['change_24h'] if x['change_24h'] is not None else -float('inf'), reverse=True)
            except Exception as e:
                self.performance_text.insert(tk.END, f"Erreur lors du tri des performances: {str(e)}\n")
                return

            self.performance_text.insert(tk.END, "TOP PERFORMANCES (24h)\n")
            self.performance_text.insert(tk.END, "=" * 40 + "\n\n")
            for p in performances:
                try:
                    self.performance_text.insert(tk.END, f"📊 {p['symbol']}/USDT\n")
                    self.performance_text.insert(tk.END, f"Prix: {p['price']:.8f} USDT\n")
                    
                    # Formatage de la variation avec code couleur
                    change = p['change_24h']
                    if change > 0:
                        self.performance_text.insert(tk.END, f"Variation 24h: +{change:.2f}% 📈\n")
                    elif change < 0:
                        self.performance_text.insert(tk.END, f"Variation 24h: {change:.2f}% 📉\n")
                    else:
                        self.performance_text.insert(tk.END, f"Variation 24h: {change:.2f}% ↔️\n")
                    
                    # Formatage du volume avec séparateurs de milliers
                    volume_str = "{:,.0f}".format(p['volume']).replace(',', ' ')
                    self.performance_text.insert(tk.END, f"Volume: {volume_str} USDT\n")
                    
                    # Ajout d'indicateurs supplémentaires
                    if p['volume'] > 10000000:  # Volume > 10M USDT
                        self.performance_text.insert(tk.END, "Volume élevé 🔥\n")
                    if abs(change) > 5:  # Variation > 5%
                        self.performance_text.insert(tk.END, "Forte volatilité ⚡\n")
                        
                    self.performance_text.insert(tk.END, "-" * 40 + "\n\n")
                except Exception as e:
                    self.performance_text.insert(tk.END, f"Erreur d'affichage pour {p['symbol']}: {str(e)}\n")
                    continue
                    
            # Ajout de statistiques globales
            try:
                avg_change = sum(p['change_24h'] for p in performances) / len(performances)
                best_perf = max(performances, key=lambda x: x['change_24h'])
                worst_perf = min(performances, key=lambda x: x['change_24h'])
                
                self.performance_text.insert(tk.END, "\n📊 STATISTIQUES GLOBALES\n")
                self.performance_text.insert(tk.END, "=" * 40 + "\n")
                self.performance_text.insert(tk.END, f"Variation moyenne: {avg_change:.2f}%\n")
                self.performance_text.insert(tk.END, f"Meilleure performance: {best_perf['symbol']} ({best_perf['change_24h']:.2f}%)\n")
                self.performance_text.insert(tk.END, f"Moins bonne performance: {worst_perf['symbol']} ({worst_perf['change_24h']:.2f}%)\n")
            except Exception as e:
                self.performance_text.insert(tk.END, f"\nErreur calcul statistiques: {str(e)}\n")

        except Exception as e:
            self.performance_text.insert(tk.END, f"Erreur générale: {str(e)}\n")
        
        finally:
            # Toujours ajouter l'horodatage
            self.performance_text.insert(tk.END, f"\nDernière mise à jour: {datetime.now().strftime('%H:%M:%S')}\n")
        
    def setup_historical_tab(self, historical_frame):
        self.historical_text = scrolledtext.ScrolledText(historical_frame, height=30)
        self.historical_text.pack(fill='both', expand=True)
        
        # Sélection de la crypto
        selection_frame = ttk.LabelFrame(historical_frame, text="Sélection", padding="5")
        selection_frame.pack(fill='x', pady=5)
        
        self.historical_coin_entry = ttk.Entry(selection_frame, width=20)
        self.historical_coin_entry.pack(side='left', padx=5)
        
        ttk.Button(selection_frame, text="Analyser", 
                   command=self.analyze_historical).pack(side='left', padx=5)

    def analyze_historical(self):
        coin = self.historical_coin_entry.get().upper()
        if not coin:
            self.historical_text.delete(1.0, tk.END)
            self.historical_text.insert(tk.END, "Veuillez entrer un symbole de crypto")
            return
            
        self.historical_text.delete(1.0, tk.END)
        self.historical_text.insert(tk.END, f"Analyse historique de {coin}...\n\n")
        
        try:
            # Récupération des données sur différentes périodes
            timeframes = {
                '1j': ('5m', 288),    # 5 minutes sur 24h
                '1s': ('1h', 168),    # 1 heure sur 1 semaine
                '1m': ('1h', 720),    # 1 heure sur 1 mois
                '3m': ('4h', 540),    # 4 heures sur 3 mois
                '6m': ('4h', 1080),   # 4 heures sur 6 mois
                '1a': ('1d', 365)     # 1 jour sur 1 an
            }
            
            results = {}
            best_hours = {}
            
            for period, (interval, limit) in timeframes.items():
                try:
                    ohlcv = self.exchange.fetch_ohlcv(f"{coin}/USDT", interval, limit=limit)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Calcul des variations
                    df['variation'] = ((df['close'] - df['open']) / df['open']) * 100
                    
                    # Statistiques générales
                    start_price = df['open'].iloc[0]
                    end_price = df['close'].iloc[-1]
                    total_variation = ((end_price - start_price) / start_price) * 100
                    max_price = df['high'].max()
                    min_price = df['low'].min()
                    
                    # Meilleurs moments pour trader
                    df['hour'] = df['timestamp'].dt.hour
                    best_hours[period] = df.groupby('hour')['variation'].mean().sort_values(ascending=False)
                    
                    # Stockage des résultats
                    results[period] = {
                        'variation_totale': total_variation,
                        'plus_haut': max_price,
                        'plus_bas': min_price,
                        'volume_moyen': df['volume'].mean(),
                        'volatilite': df['variation'].std(),
                        'meilleure_var': df['variation'].max(),
                        'pire_var': df['variation'].min()
                    }
                    
                except Exception as e:
                    results[period] = f"Erreur: {str(e)}"
                    
            # Affichage des résultats
            self.historical_text.insert(tk.END, f"💰 ANALYSE HISTORIQUE DE {coin}\n")
            self.historical_text.insert(tk.END, "=" * 50 + "\n\n")
            
            for period, data in results.items():
                if isinstance(data, dict):
                    self.historical_text.insert(tk.END, f"📊 PÉRIODE: {period}\n")
                    self.historical_text.insert(tk.END, f"• Variation totale: {data['variation_totale']:.2f}%\n")
                    self.historical_text.insert(tk.END, f"• Plus haut: {data['plus_haut']:.8f} USDT\n")
                    self.historical_text.insert(tk.END, f"• Plus bas: {data['plus_bas']:.8f} USDT\n")
                    self.historical_text.insert(tk.END, f"• Volume moyen: {data['volume_moyen']:.2f} USDT\n")
                    self.historical_text.insert(tk.END, f"• Volatilité: {data['volatilite']:.2f}%\n")
                    self.historical_text.insert(tk.END, f"• Meilleure variation: +{data['meilleure_var']:.2f}%\n")
                    self.historical_text.insert(tk.END, f"• Pire variation: {data['pire_var']:.2f}%\n\n")
                    
                    # Meilleurs moments pour trader
                    best_times = best_hours[period].head(3)
                    self.historical_text.insert(tk.END, "MEILLEURS HORAIRES DE TRADING:\n")
                    for hour, var in best_times.items():
                        self.historical_text.insert(tk.END, f"• {hour}h00: {var:.2f}% en moyenne\n")
                    
                    self.historical_text.insert(tk.END, "-" * 50 + "\n\n")
                else:
                    self.historical_text.insert(tk.END, f"PÉRIODE {period}: {data}\n\n")
                    
            # Calcul des corrélations entre périodes
            self.historical_text.insert(tk.END, "🔄 PATTERNS RÉCURRENTS\n")
            self.historical_text.insert(tk.END, "=" * 50 + "\n\n")
            
            # Détection des moments de forte activité
            try:
                daily_data = self.exchange.fetch_ohlcv(f"{coin}/USDT", '1h', limit=168)  # 1 semaine
                df_daily = pd.DataFrame(daily_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df_daily['timestamp'] = pd.to_datetime(df_daily['timestamp'], unit='ms')
                df_daily['hour'] = df_daily['timestamp'].dt.hour
                df_daily['day'] = df_daily['timestamp'].dt.day_name()
                
                # Analyse par jour de la semaine
                day_analysis = df_daily.groupby('day')['volume'].mean().sort_values(ascending=False)
                
                self.historical_text.insert(tk.END, "JOURS LES PLUS ACTIFS:\n")
                for day, vol in day_analysis.items():
                    self.historical_text.insert(tk.END, f"• {day}: Volume moyen de {vol:,.0f} USDT\n")
                    
                self.historical_text.insert(tk.END, "\nHEURES LES PLUS ACTIVES:\n")
                hour_analysis = df_daily.groupby('hour')['volume'].mean().sort_values(ascending=False).head(5)
                for hour, vol in hour_analysis.items():
                    self.historical_text.insert(tk.END, f"• {hour}h00: Volume moyen de {vol:,.0f} USDT\n")
                    
            except Exception as e:
                self.historical_text.insert(tk.END, f"Erreur analyse patterns: {str(e)}\n")
                
            self.historical_text.insert(tk.END, "\nDernière mise à jour: " + 
                                      datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                
        except Exception as e:
            self.historical_text.insert(tk.END, f"Erreur lors de l'analyse: {str(e)}")




    def update_short_term_opportunities(self):
        self.short_term_text.delete(1.0, tk.END)
        self.short_term_text.insert(tk.END, "Recherche d'opportunités court terme...\n\n")
        
        opportunities = self.get_short_term_opportunities()
        
        if isinstance(opportunities, str):
            self.short_term_text.insert(tk.END, opportunities)
            return
            
        self.short_term_text.insert(tk.END, "🔍 OPPORTUNITÉS DE TRADING MULTI-PÉRIODES\n")
        self.short_term_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for op in opportunities:
            # Symbole et prix actuel
            self.short_term_text.insert(tk.END, f"💰 {op['symbol']}\n")
            self.short_term_text.insert(tk.END, f"Prix actuel: {op['price']:.8f} USDT\n\n")
            
            # Variations sur différentes périodes
            self.short_term_text.insert(tk.END, "VARIATIONS:\n")
            self.short_term_text.insert(tk.END, f"• 1 heure: {op['price_change_1h']:.2f}%\n")
            self.short_term_text.insert(tk.END, f"• 7 heures: {op['price_change_7h']:.2f}%\n")
            self.short_term_text.insert(tk.END, f"• 24 heures: {op['price_change_24h']:.2f}%\n\n")
            
            # Indicateurs techniques
            self.short_term_text.insert(tk.END, "INDICATEURS:\n")
            self.short_term_text.insert(tk.END, f"• RSI: {op['rsi']:.2f}\n")
            self.short_term_text.insert(tk.END, f"• Volume 24h: {op['volume']:,.0f} USDT\n")
            self.short_term_text.insert(tk.END, f"• Variation volume: {op['volume_change']:.2f}%\n\n")
            
            # Signal et analyse
            self.short_term_text.insert(tk.END, "ANALYSE:\n")
            if op['signal'] == "ACHAT":
                if op['rsi'] < 30:
                    self.short_term_text.insert(tk.END, "📊 Opportunité d'achat forte (RSI survendu)\n")
                else:
                    self.short_term_text.insert(tk.END, "📈 Momentum haussier détecté\n")
            else:
                if op['rsi'] > 70:
                    self.short_term_text.insert(tk.END, "📊 Opportunité de vente forte (RSI suracheté)\n")
                else:
                    self.short_term_text.insert(tk.END, "📉 Momentum baissier détecté\n")
            
            # Tendance générale basée sur les différentes périodes
            changes = [op['price_change_1h'], op['price_change_7h'], op['price_change_24h']]
            if all(x > 0 for x in changes):
                self.short_term_text.insert(tk.END, "🚀 Tendance haussière sur toutes les périodes\n")
            elif all(x < 0 for x in changes):
                self.short_term_text.insert(tk.END, "📉 Tendance baissière sur toutes les périodes\n")
            else:
                self.short_term_text.insert(tk.END, "↔️ Tendance mixte\n")
                        
            self.short_term_text.insert(tk.END, "-" * 50 + "\n\n")
        
        # Mise à jour du timestamp
        self.short_term_text.insert(tk.END, f"\nDernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")

    def add_coin(self):
        coin = self.coin_entry.get().upper()
        if coin and coin not in self.tracked_coins:
            try:
                self.exchange.fetch_ticker(f"{coin}/USDT")
                self.tracked_coins.add(coin)
                self.tracked_listbox.insert(tk.END, coin)
                self.coin_entry.delete(0, tk.END)
                self.log_message(f"Ajout de {coin} à la liste de suivi")
            except:
                self.log_message(f"Erreur: {coin} n'est pas une crypto valide sur Binance")

    def remove_coin(self):
        selection = self.tracked_listbox.curselection()
        if selection:
            coin = self.tracked_listbox.get(selection[0])
            self.tracked_coins.remove(coin)
            self.tracked_listbox.delete(selection[0])
            self.log_message(f"Suppression de {coin} de la liste de suivi")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)

    def analyze_coin(self, symbol: str) -> Dict:
        try:
            ohlcv = self.exchange.fetch_ohlcv(f"{symbol}/USDT", '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            df['SMA20'] = df['close'].rolling(window=20).mean()
            df['SMA50'] = df['close'].rolling(window=50).mean()
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            current_price = df['close'].iloc[-1]
            sma20 = df['SMA20'].iloc[-1]
            sma50 = df['SMA50'].iloc[-1]
            rsi = df['RSI'].iloc[-1]
            
            trend = "NEUTRE"
            if sma20 > sma50:
                trend = "HAUSSIÈRE"
            elif sma20 < sma50:
                trend = "BAISSIÈRE"
                
            recommendation = "CONSERVER"
            timeframe = "MOYEN TERME"
            
            if rsi < 30 and trend == "HAUSSIÈRE":
                recommendation = "ACHETER"
                timeframe = "COURT TERME"
            elif rsi > 70 and trend == "BAISSIÈRE":
                recommendation = "VENDRE"
                timeframe = "COURT TERME"
            elif trend == "HAUSSIÈRE" and current_price > sma50:
                recommendation = "ACHETER"
                timeframe = "MOYEN TERME"
            elif trend == "BAISSIÈRE" and current_price < sma50:
                recommendation = "VENDRE"
                timeframe = "MOYEN TERME"

            return {
                'price': current_price,
                'trend': trend,
                'rsi': rsi,
                'recommendation': recommendation,
                'timeframe': timeframe
            }
        except Exception as e:
            self.log_message(f"Erreur d'analyse pour {symbol}: {str(e)}")
            return None

    def monitor_coins(self):
        while self.monitoring:
            for coin in self.tracked_coins:
                analysis = self.analyze_coin(coin)
                if analysis:
                    self.log_message(f"\n=== Analyse de {coin} ===")
                    self.log_message(f"Prix actuel: {analysis['price']:.8f} USDT")
                    self.log_message(f"Tendance: {analysis['trend']}")
                    self.log_message(f"RSI: {analysis['rsi']:.2f}")
                    self.log_message(f"Recommandation: {analysis['recommendation']}")
                    self.log_message(f"Horizon temporel: {analysis['timeframe']}")
                    self.log_message("-" * 40)
            
            if int(time.time()) % 300 == 0:
                self.update_top_performers()
                self.update_short_term_opportunities()
                
            time.sleep(60)

    def start_monitoring(self):
        if not self.tracked_coins:
            self.log_message("Erreur: Ajoutez au moins une crypto à surveiller")
            return
            
        self.monitoring = True
        self.monitoring_thread = threading.Thread(target=self.monitor_coins)
        self.monitoring_thread.start()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_message("Démarrage de la surveillance...")
        
        self.update_top_performers()

    def stop_monitoring(self):
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("Arrêt de la surveillance")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CryptoAnalyzerGUI()
    app.run()

