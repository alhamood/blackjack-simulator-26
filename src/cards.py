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

    def __init__(self, rank: str, suit: str):
        """
        Initialize a card.

        Args:
            rank: Card rank ('2'-'10', 'J', 'Q', 'K', 'A')
            suit: Card suit ('♠', '♥', '♦', '♣')
        """
        if rank not in self.RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}")

        self.rank = rank
        self.suit = suit

    def value(self) -> int:
        """
        Get the blackjack value of the card.

        Returns:
            Card value (2-10 for number cards, 10 for face cards, 11 for Ace)
        """
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Aces are 11 by default; hand logic handles soft/hard
        else:
            return int(self.rank)

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

        self.cards: List[Card] = []
        self._deck_template: List[Card] = []  # For infinite mode
        self.cards_dealt = 0
        self.total_cards = 0

        self._build_shoe()

    def _build_shoe(self):
        """Build the shoe by combining multiple decks."""
        self.cards = []
        for _ in range(self.num_decks):
            deck = Deck()
            self.cards.extend(deck.cards)

        # Store a template for infinite mode (one full shoe)
        self._deck_template = self.cards.copy()
        self.total_cards = len(self.cards)
        self.shuffle()

    def shuffle(self):
        """Shuffle the shoe and reset cards dealt counter."""
        if not self.infinite:
            random.shuffle(self.cards)
        self.cards_dealt = 0

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
            self.cards_dealt += 1
            return card
        else:
            # Check if we need to reshuffle before dealing
            if self.needs_shuffle():
                self._build_shoe()  # Rebuild and reshuffle

            # Normal deck: remove card from shoe
            if not self.cards:
                raise ValueError("Shoe is empty - should have been reshuffled")

            card = self.cards.pop()
            self.cards_dealt += 1

            return card

    def needs_shuffle(self) -> bool:
        """
        Check if the shoe needs to be reshuffled based on penetration.

        Returns:
            True if penetration threshold has been reached
        """
        if self.infinite:
            return False  # Never needs shuffle in infinite mode

        cards_remaining = len(self.cards)
        dealt_fraction = self.cards_dealt / self.total_cards
        return dealt_fraction >= self.penetration

    def cards_remaining(self) -> int:
        """
        Get the number of cards remaining in the shoe.

        Returns:
            Number of cards left (infinite for infinite mode)
        """
        if self.infinite:
            return float('inf')
        return len(self.cards)

    def __repr__(self) -> str:
        """String representation of the shoe."""
        if self.infinite:
            return f"Shoe(infinite, {self.num_decks}-deck template)"
        else:
            return f"Shoe({len(self.cards)}/{self.total_cards} cards, {self.num_decks} decks)"
