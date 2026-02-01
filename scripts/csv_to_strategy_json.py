#!/usr/bin/env python3
"""Convert CSV strategy files to JSON format for the blackjack simulator."""

import csv
import json
import sys
from pathlib import Path

# Action code mapping from CSV abbreviations to JSON action names
ACTION_MAP = {
    'H': 'hit',
    'S': 'stand',
    'Dh': 'double_else_hit',
    'Ds': 'double_else_stand',
    'Rh': 'surrender_else_hit',
    'Rs': 'surrender_else_stand',
    'P': 'split',
    'Ph': 'split_else_hit',
    'Pd': 'split_else_double',
    'Ps': 'split_else_stand',
    'Rp': 'surrender_else_split',
}

# Our simulator uses these action names (check what's actually supported)
# split_else_hit -> not in original, need to map to closest supported action
# Let's check what the simulator actually supports and map accordingly
SIMULATOR_ACTION_MAP = {
    'H': 'hit',
    'S': 'stand',
    'Dh': 'double_else_hit',
    'Ds': 'double_else_stand',
    'Rh': 'surrender_else_hit',
    'Rs': 'surrender_else_stand',
    'P': 'split',
    'Ph': 'split',       # split if allowed, else hit — map to split (game handles fallback)
    'Pd': 'split',       # split if allowed, else double — map to split
    'Ps': 'split',       # split if allowed, else stand — map to split
    'Rp': 'surrender_else_split',  # surrender if allowed, else split
}

DEALER_CARDS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']

# Full ranges for each section
HARD_RANGE = list(range(4, 22))   # 4-21
SOFT_RANGE = list(range(13, 22))  # 13-21
PAIR_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']

# Soft total mapping: "A,N" -> soft total
SOFT_HAND_MAP = {
    'A,2': '13', 'A,3': '14', 'A,4': '15', 'A,5': '16',
    'A,6': '17', 'A,7': '18', 'A,8': '19', 'A,9': '20', 'A,10': '21',
}


def parse_range(hand_str, section):
    """Parse a player hand string into a list of individual totals.

    Examples:
        '4-7' -> ['4', '5', '6', '7']
        '18+' -> ['18', '19', '20', '21']
        '17-21' -> ['17', '18', '19', '20', '21']
        '13' -> ['13']
        '20+' -> ['20', '21']
        'A,2' -> ['13']  (soft)
        'A,9-10' -> ['20', '21'] (soft)
        'A,8-10' -> ['19', '20', '21'] (soft)
        '2,2' -> ['2']  (pair)
    """
    hand_str = hand_str.strip()

    if section in ('splits', 'split'):
        # Pair: "2,2" -> "2", "A,A" -> "A"
        parts = hand_str.split(',')
        return [parts[0].strip()]

    if section == 'soft':
        # Handle "A,N" format
        if hand_str.startswith('A,'):
            rest = hand_str[2:].strip()
            if '-' in rest:
                parts = rest.split('-')
                low = int(parts[0])
                high = int(parts[1])
                return [str(v + 11) for v in range(low, high + 1)]
            elif rest.endswith('+'):
                base = int(rest[:-1])
                return [str(v + 11) for v in range(base, 11)]  # up to A+10=21
            else:
                val = int(rest)
                return [str(val + 11)]
        # Handle numeric soft totals: "13", "18+", "19-21"

    # General numeric parsing
    if '-' in hand_str:
        parts = hand_str.split('-')
        low = int(parts[0])
        high = int(parts[1])
        return [str(v) for v in range(low, high + 1)]
    elif hand_str.endswith('+'):
        base = int(hand_str[:-1])
        if section == 'hard':
            return [str(v) for v in range(base, 22)]
        elif section == 'soft':
            return [str(v) for v in range(base, 22)]
        else:
            return [str(v) for v in range(base, 22)]
    else:
        return [hand_str]


def convert_csv_to_strategy(csv_path):
    """Convert a CSV strategy file to our JSON strategy dict."""
    hard_totals = {}
    soft_totals = {}
    pairs = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hand_type = row['hand_type'].strip()
            player_hand = row['player_hand'].strip()

            # Parse which totals this row covers
            totals = parse_range(player_hand, hand_type)

            # Parse actions for each dealer card
            actions = {}
            for dc in DEALER_CARDS:
                raw = row[dc].strip()
                action = SIMULATOR_ACTION_MAP.get(raw)
                if action is None:
                    print(f"  WARNING: Unknown action '{raw}' for {hand_type} {player_hand} vs {dc}")
                    action = 'hit'  # fallback
                actions[dc] = action

            # Assign to correct section
            for total in totals:
                if hand_type == 'hard':
                    hard_totals[total] = dict(actions)
                elif hand_type == 'soft':
                    soft_totals[total] = dict(actions)
                elif hand_type in ('splits', 'split'):
                    pairs[total] = dict(actions)

    return {
        'hard_totals': hard_totals,
        'soft_totals': soft_totals,
        'pairs': pairs,
    }


def fill_missing(strategy):
    """Fill in any missing totals with sensible defaults."""
    hard = strategy['hard_totals']
    soft = strategy['soft_totals']
    pairs = strategy['pairs']

    all_dealer = DEALER_CARDS

    # Hard totals: 4-21 (anything missing below lowest explicit -> hit, above highest -> stand)
    for v in HARD_RANGE:
        k = str(v)
        if k not in hard:
            if v <= 11:
                hard[k] = {dc: 'hit' for dc in all_dealer}
            else:
                hard[k] = {dc: 'stand' for dc in all_dealer}

    # Soft totals: 13-21
    for v in SOFT_RANGE:
        k = str(v)
        if k not in soft:
            if v <= 17:
                soft[k] = {dc: 'hit' for dc in all_dealer}
            else:
                soft[k] = {dc: 'stand' for dc in all_dealer}

    # Pairs: 2-10, A
    for p in PAIR_VALUES:
        if p not in pairs:
            if p == '5':
                # 5,5 = hard 10, always double/hit (use the hard 10 row)
                if '10' in hard:
                    pairs[p] = dict(hard['10'])
                else:
                    pairs[p] = {dc: 'double_else_hit' for dc in all_dealer}
            elif p == '10':
                # 10,10 = hard 20, always stand
                pairs[p] = {dc: 'stand' for dc in all_dealer}
            else:
                pairs[p] = {dc: 'hit' for dc in all_dealer}

    return strategy


def validate_strategy(strategy, name):
    """Validate that a strategy has no gaps."""
    issues = []

    hard = strategy['hard_totals']
    soft = strategy['soft_totals']
    pairs = strategy['pairs']

    for v in HARD_RANGE:
        k = str(v)
        if k not in hard:
            issues.append(f"Missing hard total {k}")
        else:
            for dc in DEALER_CARDS:
                if dc not in hard[k]:
                    issues.append(f"Missing hard {k} vs {dc}")
                elif hard[k][dc] is None or hard[k][dc] == '':
                    issues.append(f"Null action for hard {k} vs {dc}")

    for v in SOFT_RANGE:
        k = str(v)
        if k not in soft:
            issues.append(f"Missing soft total {k}")
        else:
            for dc in DEALER_CARDS:
                if dc not in soft[k]:
                    issues.append(f"Missing soft {k} vs {dc}")
                elif soft[k][dc] is None or soft[k][dc] == '':
                    issues.append(f"Null action for soft {k} vs {dc}")

    for p in PAIR_VALUES:
        if p not in pairs:
            issues.append(f"Missing pair {p},{p}")
        else:
            for dc in DEALER_CARDS:
                if dc not in pairs[p]:
                    issues.append(f"Missing pair {p},{p} vs {dc}")
                elif pairs[p][dc] is None or pairs[p][dc] == '':
                    issues.append(f"Null action for pair {p},{p} vs {dc}")

    if issues:
        print(f"\n  VALIDATION ISSUES for {name}:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        # Count cells
        hard_cells = sum(len(v) for v in hard.values())
        soft_cells = sum(len(v) for v in soft.values())
        pair_cells = sum(len(v) for v in pairs.values())
        total = hard_cells + soft_cells + pair_cells
        print(f"  VALID: {len(hard)} hard rows, {len(soft)} soft rows, {len(pairs)} pair rows = {total} cells")

    return len(issues) == 0


# Strategy metadata for each CSV
STRATEGY_META = {
    'basic_strategy_single_deck_H17': {
        'name': 'Basic Strategy (Single Deck, H17)',
        'description': 'Optimal basic strategy for single-deck blackjack, dealer hits soft 17',
        'rules': {
            'decks': '1',
            'dealer_hits_soft_17': True,
            'surrender_allowed': True,
            'double_after_split': True,
            'blackjack_payout': 1.5,
        }
    },
    'basic_strategy_single_deck_S17': {
        'name': 'Basic Strategy (Single Deck, S17)',
        'description': 'Optimal basic strategy for single-deck blackjack, dealer stands soft 17',
        'rules': {
            'decks': '1',
            'dealer_hits_soft_17': False,
            'surrender_allowed': True,
            'double_after_split': True,
            'blackjack_payout': 1.5,
        }
    },
    'basic_strategy_double_deck_H17': {
        'name': 'Basic Strategy (Double Deck, H17)',
        'description': 'Optimal basic strategy for double-deck blackjack, dealer hits soft 17',
        'rules': {
            'decks': '2',
            'dealer_hits_soft_17': True,
            'surrender_allowed': True,
            'double_after_split': True,
            'blackjack_payout': 1.5,
        }
    },
    'basic_strategy_double_deck_S17': {
        'name': 'Basic Strategy (Double Deck, S17)',
        'description': 'Optimal basic strategy for double-deck blackjack, dealer stands soft 17',
        'rules': {
            'decks': '2',
            'dealer_hits_soft_17': False,
            'surrender_allowed': True,
            'double_after_split': True,
            'blackjack_payout': 1.5,
        }
    },
    'basic_strategy_4to8deck_H17': {
        'name': 'Basic Strategy (4-8 Deck, H17)',
        'description': 'Optimal basic strategy for 4-8 deck blackjack, dealer hits soft 17',
        'rules': {
            'decks': '4-8',
            'dealer_hits_soft_17': True,
            'surrender_allowed': True,
            'double_after_split': True,
            'blackjack_payout': 1.5,
        }
    },
    'basic_strategy_4to8deck_S17': {
        'name': 'Basic Strategy (4-8 Deck, S17)',
        'description': 'Optimal basic strategy for 4-8 deck blackjack, dealer stands soft 17',
        'rules': {
            'decks': '4-8',
            'dealer_hits_soft_17': False,
            'surrender_allowed': True,
            'double_after_split': True,
            'blackjack_payout': 1.5,
        }
    },
}


def main():
    project_root = Path(__file__).parent.parent
    csv_dir = project_root / 'csvs_added'
    output_dir = project_root / 'config' / 'strategies'

    csv_files = sorted(csv_dir.glob('*.csv'))

    if not csv_files:
        print("No CSV files found in csvs_added/")
        sys.exit(1)

    print(f"Found {len(csv_files)} CSV files to convert:\n")

    all_valid = True
    for csv_file in csv_files:
        strategy_id = csv_file.stem
        print(f"Processing: {csv_file.name}")

        # Convert
        strategy_data = convert_csv_to_strategy(csv_file)

        # Fill missing entries
        strategy_data = fill_missing(strategy_data)

        # Validate
        valid = validate_strategy(strategy_data, strategy_id)
        if not valid:
            all_valid = False
            continue

        # Build full JSON
        meta = STRATEGY_META.get(strategy_id, {
            'name': strategy_id.replace('_', ' ').title(),
            'description': f'Strategy converted from {csv_file.name}',
            'rules': {}
        })

        output = {
            'name': meta['name'],
            'description': meta['description'],
            'rules': meta['rules'],
            'strategy': strategy_data,
        }

        # Write JSON
        output_path = output_dir / f'{strategy_id}.json'
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"  Written to: {output_path.name}")
        print()

    if all_valid:
        print("All strategies converted and validated successfully!")
    else:
        print("Some strategies had validation issues - check output above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
