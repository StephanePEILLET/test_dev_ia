#!/usr/bin/env python3
"""
Exemple d'utilisation du convertisseur de devise.
"""

from currency import EUR, USD, GBP, JPY, Currency
from money import Money
from currency_converter import CurrencyConverter


def main():
    """Démonstration du convertisseur de devise."""
    
    print("=== Convertisseur de Devise - Démonstration ===\n")
    
    # Initialisation du convertisseur
    converter = CurrencyConverter()
    
    # 1. Création de sommes d'argent
    print("1. Création de sommes d'argent:")
    euro_amount = Money(100, EUR)
    dollar_amount = Money(85.50, USD)
    pound_amount = Money(75.25, GBP)
    
    print(f"   {euro_amount}")
    print(f"   {dollar_amount}")
    print(f"   {pound_amount}")
    print()
    
    # 2. Conversions simples
    print("2. Conversions de devises:")
    
    # EUR vers USD
    eur_to_usd = converter.convert(euro_amount, USD)
    print(f"   {euro_amount} → {eur_to_usd}")
    
    # USD vers EUR
    usd_to_eur = converter.convert(dollar_amount, EUR)
    print(f"   {dollar_amount} → {usd_to_eur}")
    
    # EUR vers GBP
    eur_to_gbp = converter.convert(euro_amount, GBP)
    print(f"   {euro_amount} → {eur_to_gbp}")
    
    # GBP vers JPY
    gbp_to_jpy = converter.convert(pound_amount, JPY)
    print(f"   {pound_amount} → {gbp_to_jpy}")
    print()
    
    # 3. Opérations arithmétiques avec Money
    print("3. Opérations arithmétiques:")
    
    # Addition
    more_euros = Money(50, EUR)
    total_euros = euro_amount + more_euros
    print(f"   {euro_amount} + {more_euros} = {total_euros}")
    
    # Multiplication
    double_euros = euro_amount * 2
    print(f"   {euro_amount} × 2 = {double_euros}")
    
    # Division
    half_euros = euro_amount / 2
    print(f"   {euro_amount} ÷ 2 = {half_euros}")
    print()
    
    # 4. Arrondi
    print("4. Gestion de la précision:")
    precise_amount = Money(123.456789, EUR)
    rounded_amount = precise_amount.round(2)
    print(f"   Montant précis: {precise_amount}")
    print(f"   Arrondi (2 décimales): {rounded_amount}")
    print()
    
    # 5. Devises disponibles
    print("5. Devises disponibles:")
    available_currencies = converter.list_available_currencies()
    for currency in sorted(available_currencies, key=lambda c: c.code):
        print(f"   {currency}")
    print()
    
    # 6. Taux de change pour une devise
    print("6. Taux de change depuis EUR:")
    eur_rates = converter.get_all_rates_for_currency(EUR)
    for target_currency, exchange_rate in eur_rates.items():
        print(f"   {exchange_rate}")
    print()
    
    # 7. Création d'une nouvelle devise et ajout d'un taux
    print("7. Ajout d'une nouvelle devise:")
    btc = Currency("BTC", "Bitcoin", "₿")
    converter.add_exchange_rate(EUR, btc, 0.000023)  # 1 EUR = 0.000023 BTC
    converter.add_exchange_rate(btc, EUR, 43478.26)  # 1 BTC = 43478.26 EUR
    
    # Test de conversion avec Bitcoin
    bitcoin_amount = converter.convert(euro_amount, btc)
    print(f"   {euro_amount} → {bitcoin_amount}")
    
    # Conversion retour
    back_to_eur = converter.convert(bitcoin_amount, EUR)
    print(f"   {bitcoin_amount} → {back_to_eur}")
    print()
    
    # 8. Exemple d'utilisation interactive
    print("8. Exemple d'utilisation avec saisie utilisateur:")
    print("   (Simulation - pas de saisie réelle)")
    
    # Simulation d'une conversion utilisateur
    user_amount = 250
    user_from_currency = USD
    user_to_currency = EUR
    
    user_money = Money(user_amount, user_from_currency)
    converted_money = converter.convert(user_money, user_to_currency)
    
    print(f"   Conversion: {user_money} → {converted_money}")
    
    print("\n=== Fin de la démonstration ===")


if __name__ == "__main__":
    main() 