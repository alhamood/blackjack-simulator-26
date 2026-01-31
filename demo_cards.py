"""
Demo script showing the cards module in action.
"""

from src.cards import Card, Deck, Shoe


def demo_card():
    """Demonstrate Card class."""
    print("=== Card Demo ===")
    card = Card('A', '♠')
    print(f"Card: {card}")
    print(f"Value: {card.value()}")
    print()


def demo_deck():
    """Demonstrate Deck class."""
    print("=== Deck Demo ===")
    deck = Deck()
    print(f"New deck: {deck}")
    print(f"First 5 cards: {deck.cards[:5]}")

    deck.shuffle()
    print(f"After shuffle: {deck.cards[:5]}")
    print()


def demo_normal_shoe():
    """Demonstrate normal (non-infinite) shoe."""
    print("=== Normal Shoe Demo (6 decks, 75% penetration) ===")
    shoe = Shoe(num_decks=6, penetration=0.75)
    print(f"Shoe: {shoe}")
    print(f"Total cards: {shoe.total_cards}")
    print(f"Cards remaining: {shoe.cards_remaining()}")

    # Deal some cards
    print("\nDealing 10 cards:")
    for i in range(10):
        card = shoe.deal_card()
        print(f"  Card {i+1}: {card}")

    print(f"\nAfter dealing 10 cards:")
    print(f"  Cards remaining: {shoe.cards_remaining()}")
    print(f"  Cards dealt: {shoe.cards_dealt}")
    print()


def demo_infinite_shoe():
    """Demonstrate infinite shoe (CSM)."""
    print("=== Infinite Shoe Demo (Continuous Shuffle Machine) ===")
    shoe = Shoe(num_decks=6, infinite=True)
    print(f"Shoe: {shoe}")
    print(f"Cards remaining: {shoe.cards_remaining()}")

    # Deal many cards
    print("\nDealing 100 cards from infinite shoe:")
    dealt = [shoe.deal_card() for _ in range(100)]
    print(f"  First 10: {dealt[:10]}")
    print(f"  Last 10: {dealt[-10:]}")

    print(f"\nAfter dealing 100 cards:")
    print(f"  Cards remaining: {shoe.cards_remaining()}")
    print(f"  Cards dealt counter: {shoe.cards_dealt}")
    print(f"  Needs shuffle? {shoe.needs_shuffle()}")
    print()


def demo_penetration():
    """Demonstrate penetration and auto-reshuffle."""
    print("=== Penetration Demo (1 deck, 50% penetration) ===")
    shoe = Shoe(num_decks=1, penetration=0.5)
    print(f"Initial: {shoe}")

    # Deal 26 cards (exactly at penetration)
    print("\nDealing 26 cards (reaches 50% penetration)...")
    for _ in range(26):
        shoe.deal_card()
    print(f"After 26 cards: {shoe.cards_dealt} dealt, {len(shoe.cards)} remaining")
    print(f"Needs shuffle? {shoe.needs_shuffle()}")

    # Deal one more card (triggers reshuffle)
    print("\nDealing 1 more card (triggers reshuffle)...")
    shoe.deal_card()
    print(f"After reshuffle: {shoe.cards_dealt} dealt, {len(shoe.cards)} remaining")
    print()


if __name__ == '__main__':
    demo_card()
    demo_deck()
    demo_normal_shoe()
    demo_infinite_shoe()
    demo_penetration()

    print("✓ Cards module demo complete!")
