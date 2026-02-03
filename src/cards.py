"""
Card, Deck, and Shoe classes for blackjack simulation.

Classes:
    Card: Represents a single playing card
    Deck: Represents a standard 52-card deck
    Shoe: Represents a multi-deck shoe with shuffle and penetration logic
"""

import random
from typing import List, Optional


class Card:
    """Represents a single playing card."""

    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['♠', '♥', '♦', '♣']
    _RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11,
    }
    # Hi-Lo count values: 2-6 = +1, 7-9 = 0, 10-A = -1
    _HI_LO_VALUES = {
        '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
        '7': 0, '8': 0, '9': 0,
        '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1,
    }
    _VALID_RANKS = frozenset(RANKS)
    _VALID_SUITS = frozenset(SUITS)

    __slots__ = ('rank', 'suit', '_value', '_hi_lo_value', 'is_ace')

    def __init__(self, rank: str, suit: str):
        """
        Initialize a card.

        Args:
            rank: Card rank ('2'-'10', 'J', 'Q', 'K', 'A')
            suit: Card suit ('♠', '♥', '♦', '♣')
        """
        if rank not in self._VALID_RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in self._VALID_SUITS:
            raise ValueError(f"Invalid suit: {suit}")

        self.rank = rank
        self.suit = suit
        self._value = self._RANK_VALUES[rank]
        self._hi_lo_value = self._HI_LO_VALUES[rank]
        self.is_ace = rank == 'A'

    def value(self) -> int:
        """
        Get the blackjack value of the card.

        Returns:
            Card value (2-10 for number cards, 10 for face cards, 11 for Ace)
        """
        return self._value

    def hi_lo_value(self) -> int:
        """
        Get the Hi-Lo count value of the card.

        Returns:
            +1 for 2-6, 0 for 7-9, -1 for 10-A
        """
        return self._hi_lo_value

    def __repr__(self) -> str:
        """String representation of the card."""
        return f"{self.rank}{self.suit}"

    def __eq__(self, other) -> bool:
        """Check equality based on rank and suit."""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit


class Deck:
    """Represents a standard 52-card deck."""

    def __init__(self):
        """Initialize a standard 52-card deck."""
        self.cards: List[Card] = []
        self._build_deck()

    def _build_deck(self):
        """Build a standard 52-card deck."""
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]

    def shuffle(self):
        """Shuffle the deck in place."""
        random.shuffle(self.cards)

    def __len__(self) -> int:
        """Return the number of cards in the deck."""
        return len(self.cards)

    def __repr__(self) -> str:
        """String representation of the deck."""
        return f"Deck({len(self.cards)} cards)"


class Shoe:
    """
    Represents a multi-deck shoe for blackjack.

    Supports:
    - 1-8 physical decks
    - Infinite deck mode (continuous shuffle machine)
    - Penetration tracking (when to reshuffle)
    """

    def __init__(self, num_decks: int = 6, penetration: float = 0.75, infinite: bool = False):
        """
        Initialize a shoe.

        Args:
            num_decks: Number of decks to use (1-8, or any for infinite mode)
            penetration: Fraction of shoe to deal before reshuffling (0.0-1.0)
            infinite: If True, simulates continuous shuffle machine (infinite deck)
        """
        if num_decks < 1:
            raise ValueError("num_decks must be at least 1")
        if not 0.0 <= penetration <= 1.0:
            raise ValueError("penetration must be between 0.0 and 1.0")

        self.num_decks = num_decks
        self.penetration = penetration
        self.infinite = infinite

        # Build card objects once and reuse them across reshuffles
        self._master_cards: List[Card] = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                card = Card(rank, suit)
                for _ in range(num_decks):
                    self._master_cards.append(card)

        self.total_cards = len(self._master_cards)
        self._shuffle_threshold = int(self.total_cards * self.penetration)
        self.cards: List[Card] = self._master_cards.copy()
        self._deck_template: List[Card] = self._master_cards  # For infinite mode
        self.cards_dealt = 0
        self.running_count = 0  # Hi-Lo running count

        self.shuffle()

    def _rebuild_and_shuffle(self):
        """Reset the shoe by copying master cards and shuffling."""
        self.cards = self._master_cards.copy()
        self.cards_dealt = 0
        self.running_count = 0
        random.shuffle(self.cards)

    def shuffle(self):
        """Shuffle the shoe and reset cards dealt counter."""
        if not self.infinite:
            random.shuffle(self.cards)
        self.cards_dealt = 0
        self.running_count = 0

    def deal_card(self) -> Card:
        """
        Deal one card from the shoe.

        Returns:
            The dealt card

        Raises:
            ValueError: If the shoe is empty (shouldn't happen with proper penetration)
        """
        if self.infinite:
            # Infinite deck: sample with replacement from template
            card = random.choice(self._deck_template)
            # Don't track count for infinite deck (meaningless)
            return card
        else:
            # Check if we need to reshuffle before dealing
            if self.cards_dealt >= self._shuffle_threshold:
                self._rebuild_and_shuffle()

            card = self.cards.pop()
            self.cards_dealt += 1
            self.running_count += card.hi_lo_value()

            return card

    def needs_shuffle(self) -> bool:
        """
        Check if the shoe needs to be reshuffled based on penetration.

        Returns:
            True if penetration threshold has been reached
        """
        if self.infinite:
            return False  # Never needs shuffle in infinite mode

        return self.cards_dealt >= self._shuffle_threshold

    def cards_remaining(self) -> int:
        """
        Get the number of cards remaining in the shoe.

        Returns:
            Number of cards left (infinite for infinite mode)
        """
        if self.infinite:
            return float('inf')
        return len(self.cards)

    def decks_remaining(self) -> float:
        """
        Get the estimated number of decks remaining in the shoe.

        Returns:
            Number of decks left (infinite for infinite mode)
        """
        if self.infinite:
            return float('inf')
        return len(self.cards) / 52.0

    @property
    def true_count(self) -> float:
        """
        Get the true count (running count / decks remaining).

        Returns:
            True count (0.0 for infinite mode)
        """
        if self.infinite:
            return 0.0
        decks = self.decks_remaining()
        if decks <= 0:
            return 0.0
        return self.running_count / decks

    def __repr__(self) -> str:
        """String representation of the shoe."""
        if self.infinite:
            return f"Shoe(infinite, {self.num_decks}-deck template)"
        else:
            return f"Shoe({len(self.cards)}/{self.total_cards} cards, {self.num_decks} decks)"
