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

    def add_card(self, card: Card):
        """
        Add a card to the hand.

        Args:
            card: The card to add
        """
        self.cards.append(card)

    def value(self) -> int:
        """
        Calculate the best value of the hand.

        Returns:
            The highest value <= 21, or lowest value if all bust

        Rules:
        - Aces are worth 11 if that doesn't bust, otherwise 1
        - Multiple aces: at most one ace can be counted as 11
        """
        if not self.cards:
            return 0

        total = 0
        aces = 0

        # Count all cards, treating aces as 11 initially
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                total += 11
            else:
                total += card.value()

        # Adjust aces from 11 to 1 if necessary to avoid bust
        while total > 21 and aces > 0:
            total -= 10  # Convert one ace from 11 to 1
            aces -= 1

        return total

    def is_soft(self) -> bool:
        """
        Check if the hand is soft (has an ace counted as 11).

        Returns:
            True if hand contains an ace counted as 11
        """
        if not self.cards:
            return False

        # A hand is soft if it has an ace and treating it as 11 doesn't bust
        has_ace = any(card.rank == 'A' for card in self.cards)
        if not has_ace:
            return False

        # Calculate value treating all aces as 1
        total_hard = sum(1 if card.rank == 'A' else card.value() for card in self.cards)

        # If we can add 10 (treat one ace as 11) without busting, it's soft
        return (total_hard + 10) <= 21

    def is_bust(self) -> bool:
        """
        Check if the hand is busted (value > 21).

        Returns:
            True if hand value exceeds 21
        """
        return self.value() > 21

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
