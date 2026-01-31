"""
Dealer behavior logic for blackjack.

Classes:
    Dealer: Represents the dealer with automatic play logic
"""

from src.hand import Hand
from src.cards import Shoe, Card


class Dealer:
    """
    Represents a blackjack dealer.

    Handles:
    - Automatic dealer play according to house rules
    - Dealer hits on 16 or less
    - Dealer stands on 17 or more
    - Optional: dealer hits soft 17 rule
    """

    def __init__(self, hits_soft_17: bool = False):
        """
        Initialize a dealer.

        Args:
            hits_soft_17: If True, dealer hits on soft 17 (more house-favorable)
        """
        self.hits_soft_17 = hits_soft_17
        self.hand = Hand()

    def deal_initial_cards(self, shoe: Shoe):
        """
        Deal initial two cards to the dealer.

        Args:
            shoe: The shoe to deal from
        """
        self.hand.clear()
        self.hand.add_card(shoe.deal_card())
        self.hand.add_card(shoe.deal_card())

    def upcard(self) -> Card:
        """
        Get the dealer's upcard (first card, visible to players).

        Returns:
            The dealer's first card

        Raises:
            ValueError: If dealer has no cards
        """
        if len(self.hand) < 1:
            raise ValueError("Dealer has no cards")
        return self.hand.cards[0]

    def holecard(self) -> Card:
        """
        Get the dealer's hole card (second card, hidden until dealer's turn).

        Returns:
            The dealer's second card

        Raises:
            ValueError: If dealer has fewer than 2 cards
        """
        if len(self.hand) < 2:
            raise ValueError("Dealer has fewer than 2 cards")
        return self.hand.cards[1]

    def should_hit(self) -> bool:
        """
        Determine if the dealer should hit based on current hand value.

        Returns:
            True if dealer should hit, False if should stand

        Rules:
        - Must hit on 16 or less
        - Must stand on hard 17 or more
        - If hits_soft_17 is True, must hit on soft 17
        """
        value = self.hand.value()

        # Always hit on 16 or less
        if value < 17:
            return True

        # Always stand on 18 or more
        if value > 17:
            return False

        # Value is exactly 17
        if value == 17:
            # If it's soft 17 and dealer hits soft 17, hit
            if self.hand.is_soft() and self.hits_soft_17:
                return True
            # Otherwise stand
            return False

        return False

    def play_hand(self, shoe: Shoe) -> Hand:
        """
        Play out the dealer's hand according to house rules.

        Args:
            shoe: The shoe to draw cards from

        Returns:
            The dealer's final hand
        """
        # Dealer plays according to fixed rules
        while self.should_hit() and not self.hand.is_bust():
            self.hand.add_card(shoe.deal_card())

        return self.hand

    def has_blackjack(self) -> bool:
        """
        Check if dealer has blackjack.

        Returns:
            True if dealer has blackjack (21 in 2 cards)
        """
        return self.hand.is_blackjack()

    def is_bust(self) -> bool:
        """
        Check if dealer is busted.

        Returns:
            True if dealer's hand value exceeds 21
        """
        return self.hand.is_bust()

    def value(self) -> int:
        """
        Get the dealer's hand value.

        Returns:
            The dealer's hand value
        """
        return self.hand.value()

    def clear_hand(self):
        """Clear the dealer's hand."""
        self.hand.clear()

    def __repr__(self) -> str:
        """String representation of the dealer."""
        if len(self.hand) == 0:
            return "Dealer(no cards)"
        elif len(self.hand) == 1:
            return f"Dealer(upcard: {self.upcard()})"
        else:
            upcard = self.upcard()
            return f"Dealer(upcard: {upcard}, hand: {self.hand})"
