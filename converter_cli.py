#!/usr/bin/env python3
"""
Interface CLI simple pour le convertisseur de devise avec taux en temps réel.
"""

import sys
import requests
from decimal import Decimal
from datetime import datetime

from currency import EUR, USD, GBP, JPY, CHF, CAD, AUD
from money import Money


class SimpleCurrencyConverter:
    """Convertisseur simple avec API en temps réel."""
    
    def __init__(self):
        self.currencies = {
            'EUR': EUR, 'USD': USD, 'GBP': GBP, 'JPY': JPY,
            'CHF': CHF, 'CAD': CAD, 'AUD': AUD
        }
    
    def get_rate(self, from_code, to_code):
        """Récupère un taux de change depuis l'API."""
        try:
            url = f"https://open.er-api.com/v6/latest/{from_code}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('result') == 'success' and 'rates' in data:
                rates = data['rates']
                if to_code in rates:
                    return Decimal(str(rates[to_code]))
            
            return None
            
        except Exception as e:
            print(f"Erreur API: {e}")
            return None
    
    def convert(self, amount, from_code, to_code):
        """Convertit un montant entre deux devises."""
        if from_code == to_code:
            return amount
        
        rate = self.get_rate(from_code, to_code)
        if rate is None:
            raise ValueError(f"Impossible de récupérer le taux {from_code} -> {to_code}")
        
        return amount * rate


def print_help():
    """Affiche l'aide."""
    print("""
💱 CONVERTISSEUR DE DEVISE EN TEMPS RÉEL

Usage:
  python converter_cli.py convert <montant> <devise_source> <devise_cible>
  python converter_cli.py rates <devise_base>
  python converter_cli.py currencies
  python converter_cli.py interactive

Exemples:
  python converter_cli.py convert 100 EUR USD
  python converter_cli.py rates EUR
  python converter_cli.py interactive

Devises supportées: EUR, USD, GBP, JPY, CHF, CAD, AUD
    """)


def cmd_convert(converter, args):
    """Commande de conversion."""
    if len(args) != 3:
        print("Usage: convert <montant> <devise_source> <devise_cible>")
        return
    
    try:
        amount = Decimal(args[0])
        from_code = args[1].upper()
        to_code = args[2].upper()
        
        if from_code not in converter.currencies:
            print(f"Devise source inconnue: {from_code}")
            return
        
        if to_code not in converter.currencies:
            print(f"Devise cible inconnue: {to_code}")
            return
        
        # Effectuer la conversion
        result = converter.convert(amount, from_code, to_code)
        
        # Créer les objets Money pour l'affichage
        from_currency = converter.currencies[from_code]
        to_currency = converter.currencies[to_code]
        
        original = Money(amount, from_currency)
        converted = Money(result, to_currency)
        
        print(f"\n✅ {original} = {converted.round(2)}")
        
        # Afficher le taux
        rate = converter.get_rate(from_code, to_code)
        if rate:
            print(f"📊 Taux: 1 {from_code} = {rate:.4f} {to_code}")
            print(f"🕐 Mis à jour: {datetime.now().strftime('%H:%M:%S')}")
        
    except ValueError as e:
        print(f"❌ Erreur: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")


def cmd_rates(converter, args):
    """Commande d'affichage des taux."""
    if len(args) != 1:
        print("Usage: rates <devise_base>")
        return
    
    base_code = args[0].upper()
    if base_code not in converter.currencies:
        print(f"Devise inconnue: {base_code}")
        return
    
    try:
        url = f"https://open.er-api.com/v6/latest/{base_code}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('result') == 'success' and 'rates' in data:
            rates = data['rates']
            
            print(f"\n📈 Taux de change depuis {base_code}:")
            print("-" * 40)
            
            for code in sorted(converter.currencies.keys()):
                if code != base_code and code in rates:
                    rate = Decimal(str(rates[code]))
                    currency = converter.currencies[code]
                    symbol = currency.symbol or ""
                    print(f"{code:<4} {currency.name:<20} {rate:.4f} {symbol}")
            
            print(f"\n🕐 Mis à jour: {data.get('time_last_update_utc', 'N/A')}")
        else:
            print("❌ Erreur lors de la récupération des taux")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")


def cmd_currencies(converter):
    """Commande d'affichage des devises."""
    print("\n💰 Devises supportées:")
    print("-" * 30)
    
    for code, currency in sorted(converter.currencies.items()):
        symbol = f" ({currency.symbol})" if currency.symbol else ""
        print(f"{code}: {currency.name}{symbol}")


def cmd_interactive(converter):
    """Mode interactif."""
    print("\n💱 Mode interactif - Convertisseur de devise")
    print("Tapez 'quit' pour quitter, 'help' pour l'aide")
    print("Format: <montant> <devise_source> <devise_cible>\n")
    
    while True:
        try:
            user_input = input("💱 > ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir!")
                break
            
            if user_input.lower() in ['help', 'h']:
                print("\nFormat: <montant> <devise_source> <devise_cible>")
                print("Exemple: 100 EUR USD")
                print("Devises: EUR, USD, GBP, JPY, CHF, CAD, AUD")
                print("Commandes: quit, help")
                continue
            
            parts = user_input.split()
            if len(parts) == 3:
                cmd_convert(converter, parts)
            else:
                print("❌ Format: <montant> <devise_source> <devise_cible>")
                
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")


def main():
    """Fonction principale."""
    converter = SimpleCurrencyConverter()
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if command == 'convert':
        cmd_convert(converter, args)
    elif command == 'rates':
        cmd_rates(converter, args)
    elif command == 'currencies':
        cmd_currencies(converter)
    elif command == 'interactive':
        cmd_interactive(converter)
    elif command in ['help', '--help', '-h']:
        print_help()
    else:
        print(f"Commande inconnue: {command}")
        print_help()


if __name__ == '__main__':
    main() 