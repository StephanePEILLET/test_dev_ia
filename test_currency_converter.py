#!/usr/bin/env python3
"""
Tests unitaires pour le convertisseur de devise.
"""

import unittest
from decimal import Decimal
from datetime import datetime

from currency import Currency, EUR, USD, GBP, JPY
from money import Money
from currency_converter import CurrencyConverter, ExchangeRate


class TestCurrency(unittest.TestCase):
    """Tests pour la classe Currency."""
    
    def test_currency_creation(self):
        """Test de création d'une devise."""
        currency = Currency("EUR", "Euro", "€")
        self.assertEqual(currency.code, "EUR")
        self.assertEqual(currency.name, "Euro")
        self.assertEqual(currency.symbol, "€")
    
    def test_currency_code_validation(self):
        """Test de validation du code de devise."""
        # Code trop court
        with self.assertRaises(ValueError):
            Currency("EU", "Euro")
        
        # Code trop long
        with self.assertRaises(ValueError):
            Currency("EURO", "Euro")
        
        # Code vide
        with self.assertRaises(ValueError):
            Currency("", "Euro")
    
    def test_currency_name_validation(self):
        """Test de validation du nom de devise."""
        with self.assertRaises(ValueError):
            Currency("EUR", "")
    
    def test_currency_code_normalization(self):
        """Test de normalisation du code en majuscules."""
        currency = Currency("eur", "Euro")
        self.assertEqual(currency.code, "EUR")
    
    def test_currency_equality(self):
        """Test d'égalité entre devises."""
        eur1 = Currency("EUR", "Euro", "€")
        eur2 = Currency("EUR", "Euro", "€")
        usd = Currency("USD", "US Dollar", "$")
        
        self.assertEqual(eur1, eur2)
        self.assertNotEqual(eur1, usd)
    
    def test_currency_string_representation(self):
        """Test de représentation textuelle."""
        eur_with_symbol = Currency("EUR", "Euro", "€")
        eur_without_symbol = Currency("EUR", "Euro")
        
        self.assertEqual(str(eur_with_symbol), "Euro (EUR) - €")
        self.assertEqual(str(eur_without_symbol), "Euro (EUR)")
    
    def test_predefined_currencies(self):
        """Test des devises prédéfinies."""
        self.assertEqual(EUR.code, "EUR")
        self.assertEqual(USD.code, "USD")
        self.assertEqual(GBP.code, "GBP")
        self.assertEqual(JPY.code, "JPY")


class TestMoney(unittest.TestCase):
    """Tests pour la classe Money."""
    
    def setUp(self):
        """Configuration des tests."""
        self.eur = Currency("EUR", "Euro", "€")
        self.usd = Currency("USD", "US Dollar", "$")
    
    def test_money_creation(self):
        """Test de création d'un objet Money."""
        money = Money(100, self.eur)
        self.assertEqual(money.amount, Decimal('100'))
        self.assertEqual(money.currency, self.eur)
    
    def test_money_creation_with_different_types(self):
        """Test de création avec différents types numériques."""
        # Int
        money_int = Money(100, self.eur)
        self.assertEqual(money_int.amount, Decimal('100'))
        
        # Float
        money_float = Money(100.50, self.eur)
        self.assertEqual(money_float.amount, Decimal('100.50'))
        
        # String
        money_str = Money("100.75", self.eur)
        self.assertEqual(money_str.amount, Decimal('100.75'))
        
        # Decimal
        money_decimal = Money(Decimal('100.25'), self.eur)
        self.assertEqual(money_decimal.amount, Decimal('100.25'))
    
    def test_money_invalid_currency(self):
        """Test avec une devise invalide."""
        with self.assertRaises(TypeError):
            Money(100, "EUR")  # String au lieu de Currency
    
    def test_money_equality(self):
        """Test d'égalité entre objets Money."""
        money1 = Money(100, self.eur)
        money2 = Money(100, self.eur)
        money3 = Money(100, self.usd)
        money4 = Money(200, self.eur)
        
        self.assertEqual(money1, money2)
        self.assertNotEqual(money1, money3)  # Devise différente
        self.assertNotEqual(money1, money4)  # Montant différent
    
    def test_money_comparison(self):
        """Test de comparaisons entre objets Money."""
        money1 = Money(100, self.eur)
        money2 = Money(150, self.eur)
        money3 = Money(100, self.usd)
        
        # Comparaisons valides (même devise)
        self.assertTrue(money1 < money2)
        self.assertTrue(money2 > money1)
        self.assertTrue(money1 <= money2)
        self.assertTrue(money2 >= money1)
        
        # Comparaisons invalides (devises différentes)
        with self.assertRaises(ValueError):
            money1 < money3
    
    def test_money_addition(self):
        """Test d'addition entre objets Money."""
        money1 = Money(100, self.eur)
        money2 = Money(50, self.eur)
        money3 = Money(100, self.usd)
        
        # Addition valide
        result = money1 + money2
        self.assertEqual(result.amount, Decimal('150'))
        self.assertEqual(result.currency, self.eur)
        
        # Addition invalide (devises différentes)
        with self.assertRaises(ValueError):
            money1 + money3
    
    def test_money_subtraction(self):
        """Test de soustraction entre objets Money."""
        money1 = Money(100, self.eur)
        money2 = Money(30, self.eur)
        
        result = money1 - money2
        self.assertEqual(result.amount, Decimal('70'))
        self.assertEqual(result.currency, self.eur)
    
    def test_money_multiplication(self):
        """Test de multiplication d'un objet Money."""
        money = Money(100, self.eur)
        
        # Multiplication par int
        result_int = money * 2
        self.assertEqual(result_int.amount, Decimal('200'))
        
        # Multiplication par float
        result_float = money * 1.5
        self.assertEqual(result_float.amount, Decimal('150'))
        
        # Multiplication par Decimal
        result_decimal = money * Decimal('0.5')
        self.assertEqual(result_decimal.amount, Decimal('50'))
        
        # Type invalide
        with self.assertRaises(TypeError):
            money * "invalid"
    
    def test_money_division(self):
        """Test de division d'un objet Money."""
        money = Money(100, self.eur)
        
        # Division par int
        result_int = money / 2
        self.assertEqual(result_int.amount, Decimal('50'))
        
        # Division par float
        result_float = money / 4.0
        self.assertEqual(result_float.amount, Decimal('25'))
        
        # Division par zéro
        with self.assertRaises(ZeroDivisionError):
            money / 0
        
        # Type invalide
        with self.assertRaises(TypeError):
            money / "invalid"
    
    def test_money_rounding(self):
        """Test d'arrondi d'un objet Money."""
        money = Money(123.456789, self.eur)
        
        # Arrondi par défaut (2 décimales)
        rounded_default = money.round()
        self.assertEqual(rounded_default.amount, Decimal('123.46'))
        
        # Arrondi à 0 décimales
        rounded_zero = money.round(0)
        self.assertEqual(rounded_zero.amount, Decimal('123'))
        
        # Arrondi à 4 décimales
        rounded_four = money.round(4)
        self.assertEqual(rounded_four.amount, Decimal('123.4568'))
    
    def test_money_string_representation(self):
        """Test de représentation textuelle."""
        money_with_symbol = Money(100, self.eur)
        money_without_symbol = Money(100, Currency("XYZ", "Test Currency"))
        
        self.assertEqual(str(money_with_symbol), "100.00 €")
        self.assertEqual(str(money_without_symbol), "100.00 XYZ")


class TestExchangeRate(unittest.TestCase):
    """Tests pour la classe ExchangeRate."""
    
    def setUp(self):
        """Configuration des tests."""
        self.eur = EUR
        self.usd = USD
    
    def test_exchange_rate_creation(self):
        """Test de création d'un taux de change."""
        rate = ExchangeRate(self.eur, self.usd, Decimal('1.0850'))
        
        self.assertEqual(rate.from_currency, self.eur)
        self.assertEqual(rate.to_currency, self.usd)
        self.assertEqual(rate.rate, Decimal('1.0850'))
        self.assertIsInstance(rate.timestamp, datetime)
    
    def test_exchange_rate_with_timestamp(self):
        """Test de création avec timestamp personnalisé."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        rate = ExchangeRate(self.eur, self.usd, Decimal('1.0850'), custom_time)
        
        self.assertEqual(rate.timestamp, custom_time)
    
    def test_exchange_rate_string_representation(self):
        """Test de représentation textuelle."""
        rate = ExchangeRate(self.eur, self.usd, Decimal('1.0850'))
        expected = "EUR → USD: 1.0850"
        self.assertEqual(str(rate), expected)


class TestCurrencyConverter(unittest.TestCase):
    """Tests pour la classe CurrencyConverter."""
    
    def setUp(self):
        """Configuration des tests."""
        self.converter = CurrencyConverter()
    
    def test_converter_initialization(self):
        """Test d'initialisation du convertisseur."""
        # Vérifier que des taux par défaut sont chargés
        available_currencies = self.converter.list_available_currencies()
        self.assertTrue(len(available_currencies) > 0)
        
        # Vérifier quelques devises principales
        currency_codes = {c.code for c in available_currencies}
        self.assertIn("EUR", currency_codes)
        self.assertIn("USD", currency_codes)
        self.assertIn("GBP", currency_codes)
    
    def test_add_exchange_rate(self):
        """Test d'ajout de taux de change."""
        btc = Currency("BTC", "Bitcoin", "₿")
        self.converter.add_exchange_rate(EUR, btc, Decimal('0.000023'))
        
        rate = self.converter.get_exchange_rate(EUR, btc)
        self.assertIsNotNone(rate)
        self.assertEqual(rate.rate, Decimal('0.000023'))
    
    def test_get_exchange_rate(self):
        """Test de récupération de taux de change."""
        # Taux existant
        rate = self.converter.get_exchange_rate(EUR, USD)
        self.assertIsNotNone(rate)
        
        # Taux inexistant
        btc = Currency("BTC", "Bitcoin")
        rate_nonexistent = self.converter.get_exchange_rate(EUR, btc)
        self.assertIsNone(rate_nonexistent)
    
    def test_convert_same_currency(self):
        """Test de conversion vers la même devise."""
        money = Money(100, EUR)
        converted = self.converter.convert(money, EUR)
        
        self.assertEqual(converted.amount, Decimal('100'))
        self.assertEqual(converted.currency, EUR)
    
    def test_convert_different_currencies(self):
        """Test de conversion entre devises différentes."""
        money = Money(100, EUR)
        converted = self.converter.convert(money, USD)
        
        self.assertEqual(converted.currency, USD)
        self.assertGreater(converted.amount, 0)
    
    def test_convert_via_pivot(self):
        """Test de conversion via devise pivot."""
        # Ajouter une devise qui n'a de taux que vers EUR
        sek = Currency("SEK", "Swedish Krona")
        self.converter.add_exchange_rate(EUR, sek, Decimal('11.20'))
        self.converter.add_exchange_rate(sek, EUR, Decimal('0.0892'))
        
        # Convertir EUR vers SEK puis SEK vers USD (via EUR)
        money_eur = Money(100, EUR)
        money_sek = self.converter.convert(money_eur, sek)
        money_usd = self.converter.convert(money_sek, USD)
        
        self.assertEqual(money_sek.currency, sek)
        self.assertEqual(money_usd.currency, USD)
    
    def test_convert_unavailable_rate(self):
        """Test de conversion avec taux non disponible."""
        btc = Currency("BTC", "Bitcoin")
        money = Money(100, btc)
        
        with self.assertRaises(ValueError):
            self.converter.convert(money, USD)
    
    def test_list_available_currencies(self):
        """Test de liste des devises disponibles."""
        currencies = self.converter.list_available_currencies()
        
        self.assertIsInstance(currencies, set)
        self.assertTrue(len(currencies) > 0)
        
        # Vérifier que EUR et USD sont présents
        currency_codes = {c.code for c in currencies}
        self.assertIn("EUR", currency_codes)
        self.assertIn("USD", currency_codes)
    
    def test_get_all_rates_for_currency(self):
        """Test de récupération de tous les taux pour une devise."""
        eur_rates = self.converter.get_all_rates_for_currency(EUR)
        
        self.assertIsInstance(eur_rates, dict)
        self.assertTrue(len(eur_rates) > 0)
        
        # Vérifier qu'USD est dans les taux depuis EUR
        target_currencies = [c.code for c in eur_rates.keys()]
        self.assertIn("USD", target_currencies)
    
    def test_precision_handling(self):
        """Test de gestion de la précision dans les conversions."""
        money = Money("123.456789", EUR)
        converted = self.converter.convert(money, USD)
        
        # Le résultat devrait maintenir la précision
        self.assertIsInstance(converted.amount, Decimal)
        
        # Test d'arrondi
        rounded = converted.round(2)
        # Vérifier que l'arrondi fonctionne
        str_amount = str(rounded.amount)
        decimal_places = len(str_amount.split('.')[-1]) if '.' in str_amount else 0
        self.assertLessEqual(decimal_places, 2)


class TestIntegration(unittest.TestCase):
    """Tests d'intégration du système complet."""
    
    def setUp(self):
        """Configuration des tests."""
        self.converter = CurrencyConverter()
    
    def test_full_conversion_workflow(self):
        """Test complet du workflow de conversion."""
        # 1. Créer une somme d'argent
        original_amount = Money(1000, EUR)
        
        # 2. Convertir vers USD
        usd_amount = self.converter.convert(original_amount, USD)
        
        # 3. Convertir retour vers EUR
        back_to_eur = self.converter.convert(usd_amount, EUR)
        
        # 4. Vérifier que la conversion aller-retour est cohérente
        # (avec une petite tolérance pour les erreurs d'arrondi)
        difference = abs(original_amount.amount - back_to_eur.amount)
        self.assertLess(difference, Decimal('0.01'))
    
    def test_multiple_currency_operations(self):
        """Test d'opérations avec multiples devises."""
        # Créer des montants dans différentes devises
        eur_amount = Money(100, EUR)
        usd_amount = Money(100, USD)
        
        # Convertir tout vers GBP
        eur_to_gbp = self.converter.convert(eur_amount, GBP)
        usd_to_gbp = self.converter.convert(usd_amount, GBP)
        
        # Additionner les montants en GBP
        total_gbp = eur_to_gbp + usd_to_gbp
        
        # Vérifier le résultat
        self.assertEqual(total_gbp.currency, GBP)
        self.assertGreater(total_gbp.amount, 0)
    
    def test_edge_cases(self):
        """Test de cas limites."""
        # Montant zéro
        zero_money = Money(0, EUR)
        converted_zero = self.converter.convert(zero_money, USD)
        self.assertEqual(converted_zero.amount, Decimal('0'))
        
        # Très petit montant
        tiny_money = Money("0.01", EUR)
        converted_tiny = self.converter.convert(tiny_money, USD)
        self.assertGreater(converted_tiny.amount, 0)
        
        # Très grand montant
        large_money = Money("1000000", EUR)
        converted_large = self.converter.convert(large_money, USD)
        self.assertGreater(converted_large.amount, 0)


if __name__ == '__main__':
    # Configuration pour des sorties plus détaillées
    unittest.main(verbosity=2) 