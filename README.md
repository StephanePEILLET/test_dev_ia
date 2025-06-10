# Convertisseur de Devise

Un convertisseur de devise orienté objet en Python avec une architecture claire et des concepts métiers bien définis.

## Fonctionnalités

- **Classes métier robustes** : Currency, Money, CurrencyConverter
- **Gestion précise des montants** : Utilisation de Decimal pour éviter les erreurs de précision
- **Opérations arithmétiques** : Addition, soustraction, multiplication, division sur les objets Money
- **Conversions flexibles** : Support des conversions directes et via devise pivot
- **Validation stricte** : Contrôles de type et de cohérence
- **Tests complets** : Suite de tests unitaires exhaustive

## Architecture

### Classes principales

1. **Currency** : Représente une devise avec code ISO, nom et symbole
2. **Money** : Représente une somme d'argent dans une devise spécifique
3. **CurrencyConverter** : Gère les conversions entre devises
4. **ExchangeRate** : Représente un taux de change entre deux devises

## Installation

Aucune dépendance externe requise. Le projet utilise uniquement la bibliothèque standard Python.

```bash
# Cloner ou télécharger les fichiers
# Python 3.8+ requis
```

## Utilisation rapide

```python
from currency import EUR, USD, GBP
from money import Money
from currency_converter import CurrencyConverter

# Créer des montants
euros = Money(100, EUR)
dollars = Money(85.50, USD)

# Initialiser le convertisseur
converter = CurrencyConverter()

# Convertir entre devises
usd_amount = converter.convert(euros, USD)
print(f"{euros} = {usd_amount}")

# Opérations arithmétiques
total = euros + Money(50, EUR)
double = euros * 2
print(f"Total: {total}, Double: {double}")
```

## Exemple complet

Lancez le fichier d'exemple pour voir toutes les fonctionnalités :

```bash
python example.py
```

## Tests

Exécutez la suite de tests complète :

```bash
python test_currency_converter.py
```

### Couverture des tests

- ✅ Tests de création et validation des devises
- ✅ Tests d'opérations arithmétiques sur Money
- ✅ Tests de conversions simples et complexes
- ✅ Tests de gestion d'erreurs
- ✅ Tests d'intégration du workflow complet
- ✅ Tests de cas limites

## Devises supportées par défaut

- **EUR** - Euro (€)
- **USD** - US Dollar ($)
- **GBP** - British Pound (£)
- **JPY** - Japanese Yen (¥)
- **CHF** - Swiss Franc
- **CAD** - Canadian Dollar (C$)
- **AUD** - Australian Dollar (A$)

Vous pouvez facilement ajouter de nouvelles devises et taux de change.

## Exemples d'utilisation

### Création de devises personnalisées

```python
# Créer une nouvelle devise
btc = Currency("BTC", "Bitcoin", "₿")

# Ajouter un taux de change
converter.add_exchange_rate(EUR, btc, Decimal('0.000023'))
```

### Opérations avec Money

```python
# Création
price = Money(19.99, EUR)

# Comparaisons
expensive = Money(50, EUR)
print(price < expensive)  # True

# Arithmétique
tax = price * 0.20
total = price + tax

# Arrondi
rounded = total.round(2)
```

### Conversions avancées

```python
# Conversion via devise pivot automatique
sek = Currency("SEK", "Swedish Krona")
converter.add_exchange_rate(EUR, sek, Decimal('11.20'))

# Cette conversion utilisera EUR comme pivot
yen_amount = Money(1000, JPY)
sek_amount = converter.convert(yen_amount, sek)
```

## Contribution

1. Les contributions sont les bienvenues
2. Assurez-vous que tous les tests passent
3. Respectez le style de code existant
4. Ajoutez des tests pour les nouvelles fonctionnalités

## Licence

Ce projet est fourni à des fins éducatives et de démonstration. 