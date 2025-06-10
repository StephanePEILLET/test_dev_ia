#!/usr/bin/env python3
"""
Test simple de l'API de taux de change.
"""

import requests
from decimal import Decimal
from datetime import datetime
from currency import EUR, USD, GBP

def test_api():
    """Test basique de l'API de taux de change."""
    
    print("=== Test API de taux de change ===\n")
    
    try:
        # Test avec l'API open.er-api.com
        url = "https://open.er-api.com/v6/latest/EUR"
        print(f"Appel API: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"Statut API: {data.get('result', 'inconnu')}")
        
        if data.get('result') == 'success' and 'rates' in data:
            rates = data['rates']
            print(f"Nombre de devises: {len(rates)}")
            print("\nQuelques taux depuis EUR:")
            
            for code in ['USD', 'GBP', 'JPY', 'CHF']:
                if code in rates:
                    rate = Decimal(str(rates[code]))
                    print(f"  1 EUR = {rate} {code}")
            
            print(f"\nTimestamp: {data.get('time_last_update_utc', 'N/A')}")
            
        else:
            print("Erreur dans la réponse de l'API")
            
    except requests.RequestException as e:
        print(f"Erreur réseau: {e}")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_api() 