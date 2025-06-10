from decimal import Decimal, ROUND_HALF_UP
from typing import Union
from currency import Currency


class Money:
    """
    Représente une somme d'argent dans une devise spécifique.
    Utilise Decimal pour éviter les erreurs de précision des flottants.
    """
    
    def __init__(self, amount: Union[int, float, str, Decimal], currency: Currency):
        """
        Initialise une somme d'argent.
        
        Args:
            amount: Montant (int, float, str ou Decimal)
            currency: Devise associée
        """
        if not isinstance(currency, Currency):
            raise TypeError("currency doit être une instance de Currency")
        
        self._amount = Decimal(str(amount))
        self._currency = currency
    
    @property
    def amount(self) -> Decimal:
        """Retourne le montant."""
        return self._amount
    
    @property
    def currency(self) -> Currency:
        """Retourne la devise."""
        return self._currency
    
    def round(self, decimal_places: int = 2) -> 'Money':
        """
        Arrondit le montant au nombre de décimales spécifié.
        
        Args:
            decimal_places: Nombre de décimales (défaut: 2)
            
        Returns:
            Nouvelle instance Money avec montant arrondi
        """
        rounded_amount = self._amount.quantize(
            Decimal('0.1') ** decimal_places,
            rounding=ROUND_HALF_UP
        )
        return Money(rounded_amount, self._currency)
    
    def __eq__(self, other) -> bool:
        """Égalité entre deux objets Money."""
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount and self._currency == other._currency
    
    def __lt__(self, other) -> bool:
        """Comparaison inférieur (<)."""
        self._check_same_currency(other)
        return self._amount < other._amount
    
    def __le__(self, other) -> bool:
        """Comparaison inférieur ou égal (<=)."""
        self._check_same_currency(other)
        return self._amount <= other._amount
    
    def __gt__(self, other) -> bool:
        """Comparaison supérieur (>)."""
        self._check_same_currency(other)
        return self._amount > other._amount
    
    def __ge__(self, other) -> bool:
        """Comparaison supérieur ou égal (>=)."""
        self._check_same_currency(other)
        return self._amount >= other._amount
    
    def __add__(self, other) -> 'Money':
        """Addition de deux objets Money de même devise."""
        self._check_same_currency(other)
        return Money(self._amount + other._amount, self._currency)
    
    def __sub__(self, other) -> 'Money':
        """Soustraction de deux objets Money de même devise."""
        self._check_same_currency(other)
        return Money(self._amount - other._amount, self._currency)
    
    def __mul__(self, factor: Union[int, float, Decimal]) -> 'Money':
        """Multiplication par un facteur numérique."""
        if not isinstance(factor, (int, float, Decimal)):
            raise TypeError("Le facteur doit être numérique")
        return Money(self._amount * Decimal(str(factor)), self._currency)
    
    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
        """Division par un diviseur numérique."""
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError("Le diviseur doit être numérique")
        if divisor == 0:
            raise ZeroDivisionError("Division par zéro")
        return Money(self._amount / Decimal(str(divisor)), self._currency)
    
    def __str__(self) -> str:
        """Représentation textuelle formatée."""
        # Arrondi à 2 décimales pour l'affichage
        rounded_amount = self._amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if self._currency.symbol:
            return f"{rounded_amount} {self._currency.symbol}"
        return f"{rounded_amount} {self._currency.code}"
    
    def __repr__(self) -> str:
        """Représentation technique."""
        return f"Money(amount={self._amount}, currency={self._currency.code})"
    
    def _check_same_currency(self, other: 'Money') -> None:
        """Vérifie que deux objets Money ont la même devise."""
        if not isinstance(other, Money):
            raise TypeError("Opération possible uniquement entre objets Money")
        if self._currency != other._currency:
            raise ValueError(
                f"Opération impossible entre devises différentes: "
                f"{self._currency.code} et {other._currency.code}"
            ) 