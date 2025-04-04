import requests
import time
import json

class BOMService:
    """Ein einfacher Service zum Abrufen von BOM-Daten"""
    
    def __init__(self, url="http://160.85.252.87"):
        self.url = url
        
    def get_data(self):
        """
        Ruft BOM-Daten ab mit Wiederholungsversuchen
        """
        max_retries = 5
        attempt = 0
        
        while attempt < max_retries:
            try:
                response = requests.get(self.url)
                if response.status_code == 200:
                    return self._process_data(response.json())
                
            except Exception as e:
                print(f"Anfrage fehlgeschlagen: {e}")
            
            # Exponentieller Backoff
            wait_time = 2 ** attempt
            print(f"Warte {wait_time} Sekunden vor dem nächsten Versuch...")
            time.sleep(wait_time)
            attempt += 1
            
        print("Maximale Anzahl von Versuchen erreicht.")
        return {}
    
    def _process_data(self, data):
        """Bereinigt die BOM-Daten"""
        result = {}
        
        for key, value in data.items():
            # Umlaute reparieren
            fixed_key = key.replace('Ã¼', 'ü').replace('Ã¤', 'ä').replace('Ã¶', 'ö').replace('\u00c3\u00bc', 'ü').replace('\u00c3\u00a4', 'ä')
            
            # Ungültige Einträge ignorieren
            if value is not None and value != "":
                result[fixed_key] = value
                
        return result
    
    def format_bom_table(self, data):
        """Formatiert BOM-Daten als Tabelle"""
        if not data:
            return "Keine gültigen Daten gefunden."
        
        # Sortierte Materialliste erstellen
        items = sorted(data.items())
        
        numerical_costs = []
        for material, cost in items:
            if isinstance(cost, (int, float)):
                numerical_costs.append(float(cost))
                
        total = sum(numerical_costs)
        
        # Tabelle erstellen
        result = "MAT1 | COST1\n"
        result += "-----+---------\n"
        
        for material, cost in items:
            result += f"{material} | {cost}\n"
            
        result += "-----+---------\n"
        result += f"SUM  | {total}"
        
        return result