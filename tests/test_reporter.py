"""
Unit tests for reporter module.
"""

import unittest
import os
import csv
import json
import tempfile
from pathlib import Path
from src.reporter import (
    export_summary_csv,
    export_sessions_csv,
    export_hands_csv,
    export_all_csv,
    export_to_json
)
from src.simulator import Simulator, SimulationResult, SessionResult
from src.game import GameRules, GameResult, HandOutcome, PlayerAction
from src.hand import Hand
from src.cards import Card


class TestExportSummaryCSV(unittest.TestCase):
    """Test cases for export_summary_csv function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_export_summary_csv_basic(self):
        """Test basic summary CSV export."""
        # Create a simple result
        session = SessionResult(
            hands_played=100,
            total_payout=-2.5,
            win_count=45,
            loss_count=50,
            push_count=5,
            blackjack_count=4,
            bust_count=12
        )
        result = SimulationResult(
            total_hands=100,
            total_payout=-2.5,
            sessions=[session],
            win_count=45,
            loss_count=50,
            push_count=5,
            blackjack_count=4,
            bust_count=12
        )

        # Export to CSV
        filepath = os.path.join(self.temp_dir, 'summary.csv')
        export_summary_csv(result, filepath)

        # Verify file exists
        self.assertTrue(os.path.exists(filepath))

        # Read and verify content
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)

            row = rows[0]
            self.assertEqual(row['total_hands'], '100')
            self.assertEqual(row['win_count'], '45')
            self.assertEqual(row['loss_count'], '50')
            self.assertEqual(row['push_count'], '5')

    def test_export_summary_csv_creates_directory(self):
        """Test that export creates parent directory if needed."""
        filepath = os.path.join(self.temp_dir, 'subdir', 'summary.csv')

        result = SimulationResult(total_hands=10)
        export_summary_csv(result, filepath)

        self.assertTrue(os.path.exists(filepath))


class TestExportSessionsCSV(unittest.TestCase):
    """Test cases for export_sessions_csv function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_export_sessions_csv_multi_session(self):
        """Test sessions CSV export with multiple sessions."""
        sessions = [
            SessionResult(hands_played=100, total_payout=-1.5, win_count=48, loss_count=52),
            SessionResult(hands_played=100, total_payout=2.0, win_count=52, loss_count=48),
            SessionResult(hands_played=100, total_payout=-0.5, win_count=49, loss_count=51)
        ]

        result = SimulationResult(
            total_hands=300,
            total_payout=0.0,
            sessions=sessions
        )

        # Export to CSV
        filepath = os.path.join(self.temp_dir, 'sessions.csv')
        export_sessions_csv(result, filepath)

        # Verify file exists
        self.assertTrue(os.path.exists(filepath))

        # Read and verify content
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)

            # Check first session
            self.assertEqual(rows[0]['session_num'], '1')
            self.assertEqual(rows[0]['hands_played'], '100')

            # Check second session
            self.assertEqual(rows[1]['session_num'], '2')

    def test_export_sessions_csv_no_sessions(self):
        """Test that no file is created when there are no sessions."""
        result = SimulationResult(total_hands=0, sessions=[])

        filepath = os.path.join(self.temp_dir, 'sessions.csv')
        export_sessions_csv(result, filepath)

        # No file should be created
        self.assertFalse(os.path.exists(filepath))


class TestExportHandsCSV(unittest.TestCase):
    """Test cases for export_hands_csv function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_export_hands_csv_with_hands(self):
        """Test hands CSV export with hand results."""
        # Create sample hands
        player_hand = Hand()
        player_hand.add_card(Card('K', '♥'))
        player_hand.add_card(Card('8', '♦'))

        dealer_hand = Hand()
        dealer_hand.add_card(Card('10', '♠'))
        dealer_hand.add_card(Card('6', '♣'))

        hand_result = GameResult(
            outcome=HandOutcome.PLAYER_WIN,
            player_hand=player_hand,
            dealer_hand=dealer_hand,
            payout=1.0,
            bet=1.0
        )

        session = SessionResult(hand_results=[hand_result])
        result = SimulationResult(sessions=[session])

        # Export to CSV
        filepath = os.path.join(self.temp_dir, 'hands.csv')
        export_hands_csv(result, filepath)

        # Verify file exists
        self.assertTrue(os.path.exists(filepath))

        # Read and verify content
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)

            row = rows[0]
            self.assertEqual(row['hand_num'], '1')
            self.assertEqual(row['outcome'], 'PLAYER_WIN')
            self.assertEqual(row['player_value'], '18')
            self.assertEqual(row['dealer_value'], '16')

    def test_export_hands_csv_no_hands(self):
        """Test that no file is created when there are no hand results."""
        session = SessionResult(hand_results=[])
        result = SimulationResult(sessions=[session])

        filepath = os.path.join(self.temp_dir, 'hands.csv')
        export_hands_csv(result, filepath)

        # No file should be created
        self.assertFalse(os.path.exists(filepath))


class TestExportAllCSV(unittest.TestCase):
    """Test cases for export_all_csv function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_export_all_csv_single_session_no_hands(self):
        """Test export_all with single session, no hand tracking."""
        session = SessionResult(hands_played=100, total_payout=-1.0)
        result = SimulationResult(
            total_hands=100,
            total_payout=-1.0,
            sessions=[session]
        )

        base_path = os.path.join(self.temp_dir, 'test')
        files = export_all_csv(result, base_path)

        # Should only create summary file
        self.assertIn('summary', files)
        self.assertNotIn('sessions', files)
        self.assertNotIn('hands', files)
        self.assertTrue(os.path.exists(files['summary']))

    def test_export_all_csv_multi_session_with_hands(self):
        """Test export_all with multi-session and hand tracking."""
        hand_result = GameResult(
            outcome=HandOutcome.PLAYER_WIN,
            player_hand=Hand(),
            dealer_hand=Hand(),
            payout=1.0,
            bet=1.0
        )

        sessions = [
            SessionResult(hands_played=50, hand_results=[hand_result]),
            SessionResult(hands_played=50)
        ]

        result = SimulationResult(
            total_hands=100,
            total_payout=0.0,
            sessions=sessions
        )

        base_path = os.path.join(self.temp_dir, 'test')
        files = export_all_csv(result, base_path)

        # Should create all three files
        self.assertIn('summary', files)
        self.assertIn('sessions', files)
        self.assertIn('hands', files)

        for filepath in files.values():
            self.assertTrue(os.path.exists(filepath))


class TestExportToJSON(unittest.TestCase):
    """Test cases for export_to_json function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_export_to_json_basic(self):
        """Test basic JSON export."""
        session = SessionResult(
            hands_played=100,
            total_payout=-2.5,
            win_count=45,
            loss_count=50,
            push_count=5
        )
        result = SimulationResult(
            total_hands=100,
            total_payout=-2.5,
            sessions=[session],
            win_count=45,
            loss_count=50,
            push_count=5
        )

        filepath = os.path.join(self.temp_dir, 'result.json')
        export_to_json(result, filepath, include_hands=False)

        # Verify file exists
        self.assertTrue(os.path.exists(filepath))

        # Read and verify content
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.assertIn('summary', data)
        self.assertIn('sessions', data)
        self.assertEqual(data['summary']['total_hands'], 100)
        self.assertEqual(data['summary']['win_count'], 45)
        self.assertEqual(len(data['sessions']), 1)

    def test_export_to_json_with_hands(self):
        """Test JSON export with hand results."""
        player_hand = Hand()
        player_hand.add_card(Card('K', '♥'))
        player_hand.add_card(Card('9', '♦'))

        dealer_hand = Hand()
        dealer_hand.add_card(Card('10', '♠'))
        dealer_hand.add_card(Card('7', '♣'))

        hand_result = GameResult(
            outcome=HandOutcome.PLAYER_WIN,
            player_hand=player_hand,
            dealer_hand=dealer_hand,
            payout=1.0,
            bet=1.0
        )

        session = SessionResult(hands_played=1, hand_results=[hand_result])
        result = SimulationResult(
            total_hands=1,
            sessions=[session]
        )

        filepath = os.path.join(self.temp_dir, 'result_with_hands.json')
        export_to_json(result, filepath, include_hands=True)

        # Read and verify content
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.assertIn('hands', data['sessions'][0])
        self.assertEqual(len(data['sessions'][0]['hands']), 1)
        self.assertEqual(data['sessions'][0]['hands'][0]['outcome'], 'PLAYER_WIN')

    def test_export_to_json_multi_session_variance(self):
        """Test JSON export includes variance stats for multi-session."""
        sessions = [
            SessionResult(hands_played=100, total_payout=-1.0),
            SessionResult(hands_played=100, total_payout=1.0)
        ]

        result = SimulationResult(
            total_hands=200,
            total_payout=0.0,
            sessions=sessions
        )

        filepath = os.path.join(self.temp_dir, 'variance.json')
        export_to_json(result, filepath, include_hands=False)

        # Read and verify content
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.assertIn('variance', data)
        self.assertIn('session_ev_mean', data['variance'])
        self.assertIn('session_ev_stdev', data['variance'])


class TestIntegrationWithSimulator(unittest.TestCase):
    """Integration tests with actual simulator runs."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_full_simulation_export_workflow(self):
        """Test complete workflow: simulate and export."""
        sim = Simulator(infinite_shoe=True)

        # Simple strategy
        def always_stand(player_hand, dealer_upcard):
            return PlayerAction.STAND

        # Run simulation with hand tracking
        result = sim.run_simulation(
            50,
            always_stand,
            num_sessions=1,
            track_hands=True,
            max_tracked_hands=50
        )

        # Export all formats
        base_path = os.path.join(self.temp_dir, 'integration_test')
        csv_files = export_all_csv(result, base_path)

        json_path = os.path.join(self.temp_dir, 'integration_test.json')
        export_to_json(result, json_path, include_hands=True)

        # Verify files exist
        self.assertTrue(os.path.exists(csv_files['summary']))
        self.assertTrue(os.path.exists(csv_files['hands']))
        self.assertTrue(os.path.exists(json_path))

        # Verify we tracked the right number of hands
        self.assertEqual(len(result.sessions[0].hand_results), 50)


if __name__ == '__main__':
    unittest.main()
