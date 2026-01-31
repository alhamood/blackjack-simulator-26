"""
Demo script showing the hand module in action.
"""

from src.cards import Card
from src.hand import Hand


def demo_basic_hands():
    """Demonstrate basic hand operations."""
    print("=== Basic Hand Demo ===")

    # Simple hand
    hand = Hand()
    hand.add_card(Card('K', '♠'))
    hand.add_card(Card('7', '♥'))
    print(f"Hard 17: {hand}")
    print(f"  Is soft? {hand.is_soft()}")
    print(f"  Is bust? {hand.is_bust()}")
    print()


def demo_soft_hands():
    """Demonstrate soft hand logic."""
    print("=== Soft Hand Demo ===")

    # Soft 17
    hand = Hand()
    hand.add_card(Card('A', '♠'))
    hand.add_card(Card('6', '♥'))
    print(f"Soft 17: {hand}")

    # Add a card that keeps it soft
    hand.add_card(Card('2', '♦'))
    print(f"After hitting with 2: {hand}")

    # Add a card that makes it hard
    hand.add_card(Card('9', '♣'))
    print(f"After hitting with 9: {hand}")
    print()


def demo_blackjack():
    """Demonstrate blackjack detection."""
    print("=== Blackjack Demo ===")

    # Natural blackjack
    hand1 = Hand()
    hand1.add_card(Card('A', '♠'))
    hand1.add_card(Card('K', '♥'))
    print(f"Blackjack: {hand1}")
    print(f"  Is blackjack? {hand1.is_blackjack()}")

    # 21 in 3 cards (not blackjack)
    hand2 = Hand()
    hand2.add_card(Card('7', '♠'))
    hand2.add_card(Card('7', '♥'))
    hand2.add_card(Card('7', '♦'))
    print(f"21 in 3 cards: {hand2}")
    print(f"  Is blackjack? {hand2.is_blackjack()}")
    print()


def demo_bust():
    """Demonstrate bust detection."""
    print("=== Bust Demo ===")

    hand = Hand()
    hand.add_card(Card('K', '♠'))
    hand.add_card(Card('Q', '♥'))
    print(f"Starting with: {hand}")

    hand.add_card(Card('5', '♦'))
    print(f"After hitting with 5: {hand}")
    print(f"  Is bust? {hand.is_bust()}")
    print()


def demo_aces():
    """Demonstrate ace value adjustments."""
    print("=== Ace Adjustment Demo ===")

    # Single ace
    hand1 = Hand()
    hand1.add_card(Card('A', '♠'))
    hand1.add_card(Card('8', '♥'))
    print(f"A-8: {hand1}")

    # Multiple aces
    hand2 = Hand()
    hand2.add_card(Card('A', '♠'))
    hand2.add_card(Card('A', '♥'))
    print(f"A-A: {hand2}")

    hand2.add_card(Card('9', '♦'))
    print(f"A-A-9: {hand2}")

    # Three aces
    hand3 = Hand()
    hand3.add_card(Card('A', '♠'))
    hand3.add_card(Card('A', '♥'))
    hand3.add_card(Card('A', '♦'))
    print(f"A-A-A: {hand3}")
    print()


def demo_pairs():
    """Demonstrate pair detection."""
    print("=== Pair Detection Demo ===")

    # Number pair
    hand1 = Hand()
    hand1.add_card(Card('8', '♠'))
    hand1.add_card(Card('8', '♥'))
    print(f"Eights: {hand1}")
    print(f"  Is pair? {hand1.is_pair()}")
    print(f"  Can split? {hand1.can_split()}")

    # Ace pair
    hand2 = Hand()
    hand2.add_card(Card('A', '♠'))
    hand2.add_card(Card('A', '♥'))
    print(f"Aces: {hand2}")
    print(f"  Is pair? {hand2.is_pair()}")

    # Not a pair
    hand3 = Hand()
    hand3.add_card(Card('K', '♠'))
    hand3.add_card(Card('Q', '♥'))
    print(f"King-Queen: {hand3}")
    print(f"  Is pair? {hand3.is_pair()}")
    print()


def demo_progression():
    """Demonstrate a hand progressing through multiple hits."""
    print("=== Hand Progression Demo ===")

    hand = Hand()
    print(f"Starting hand: {hand}")

    cards_to_add = [
        Card('A', '♠'),
        Card('5', '♥'),
        Card('3', '♦'),
        Card('7', '♣'),
    ]

    for card in cards_to_add:
        hand.add_card(card)
        soft = " (soft)" if hand.is_soft() else " (hard)"
        bust = " BUST!" if hand.is_bust() else ""
        print(f"  Added {card}: {hand.value()}{soft}{bust}")

    print(f"\nFinal hand: {hand}")
    print()


if __name__ == '__main__':
    demo_basic_hands()
    demo_soft_hands()
    demo_blackjack()
    demo_bust()
    demo_aces()
    demo_pairs()
    demo_progression()

    print("✓ Hand module demo complete!")
