from pyairtable import Api, Base, Table
from datetime import datetime

AIRTABLE_API_KEY = "patSoNhRnQ8WV6uPi.488183127a11c9808004735f1fb7347fbc11560bd1c473a6772d84e9384c2bcf"  # Remplacez par votre clé API
BASE_ID = "Crypto"  # Remplacez par votre ID de base

class AirtableManager:
    def __init__(self):
        self.api = Api(AIRTABLE_API_KEY)
        self.base = Base(self.api, BASE_ID)
        self.cryptos_suivies = Table(self.api, BASE_ID, "cryptos_suivies")
        self.historique_analyses = Table(self.api, BASE_ID, "historique_analyses")
        self.utilisateurs = Table(self.api, BASE_ID, "utilisateurs")
    
    def ajouter_crypto(self, id_utilisateur: str, symbole: str):
        return self.cryptos_suivies.create({
            "id_utilisateur": id_utilisateur,
            "symbole": symbole,
            "date_ajout": datetime.now().isoformat()
        })
    
    def obtenir_cryptos_suivies(self, id_utilisateur: str):
        records = self.cryptos_suivies.all(formula=f"{{id_utilisateur}} = '{id_utilisateur}'")
        return [record['fields']['symbole'] for record in records]
    
    def sauvegarder_analyse(self, id_utilisateur: str, symbole: str, 
                           prix: float, rsi: float, score: float, signal: str):
        return self.historique_analyses.create({
            "id_utilisateur": id_utilisateur,
            "symbole": symbole,
            "prix": prix,
            "rsi": rsi,
            "score": score,
            "signal": signal,
            "horodatage": datetime.now().isoformat()
        })
