"""
Hand evaluation logic for blackjack.

Classes:
    Hand: Represents a player or dealer hand with value calculation
"""

from typing import List
from src.cards import Card


class Hand:
    """
    Represents a blackjack hand.

    Handles:
    - Adding cards to the hand
    - Calculating hand value (with soft/hard ace logic)
    - Detecting pairs, blackjack, and busts
    """

    def __init__(self):
        """Initialize an empty hand."""
        self.cards: List[Card] = []
        self._cached_value: int = 0
        self._cached_soft: bool = False
        self._dirty: bool = False

    def add_card(self, card: Card):
        """
        Add a card to the hand.

        Args:
            card: The card to add
        """
        self.cards.append(card)
        self._dirty = True

    def _recalculate(self):
        """Recalculate cached value and soft flag."""
        total = 0
        aces = 0

        for card in self.cards:
            if card.is_ace:
                aces += 1
                total += 11
            else:
                total += card._value

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        self._cached_value = total
        # Hand is soft if at least one ace is still counted as 11
        self._cached_soft = aces > 0
        self._dirty = False

    def value(self) -> int:
        """
        Calculate the best value of the hand.

        Returns:
            The highest value <= 21, or lowest value if all bust
        """
        if self._dirty:
            self._recalculate()
        return self._cached_value

    def is_soft(self) -> bool:
        """
        Check if the hand is soft (has an ace counted as 11).

        Returns:
            True if hand contains an ace counted as 11
        """
        if not self.cards:
            return False
        if self._dirty:
            self._recalculate()
        return self._cached_soft

    def is_bust(self) -> bool:
        """
        Check if the hand is busted (value > 21).

        Returns:
            True if hand value exceeds 21
        """
        if self._dirty:
            self._recalculate()
        return self._cached_value > 21

    def is_blackjack(self) -> bool:
        """
        Check if the hand is a blackjack (21 in exactly 2 cards).

        Returns:
            True if hand is 21 with exactly 2 cards (ace + 10-value card)
        """
        if len(self.cards) != 2:
            return False
        return self.value() == 21

    def is_pair(self) -> bool:
        """
        Check if the hand is a pair (2 cards of same rank).

        Returns:
            True if hand has exactly 2 cards with the same rank
        """
        if len(self.cards) != 2:
            return False
        return self.cards[0].rank == self.cards[1].rank

    def can_split(self) -> bool:
        """
        Check if the hand can be split (is a pair).

        Returns:
            True if hand is a pair
        """
        return self.is_pair()

    def clear(self):
        """Remove all cards from the hand."""
        self.cards = []
        self._cached_value = 0
        self._cached_soft = False
        self._dirty = False

    def __len__(self) -> int:
        """Return the number of cards in the hand."""
        return len(self.cards)

    def __repr__(self) -> str:
        """String representation of the hand."""
        if not self.cards:
            return "Hand(empty)"

        cards_str = ", ".join(str(card) for card in self.cards)
        value = self.value()
        soft = " (soft)" if self.is_soft() else ""

        return f"Hand([{cards_str}] = {value}{soft})"
