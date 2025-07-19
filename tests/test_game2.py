import pytest
import numpy as np
from collections import deque

from app.utils.game import BaseballGame
from app.utils.player import Player
from app.utils.constants import EVENT_CONFIG

class MockPlayer:
    def __init__(self, name, event_type, speed=0):
        self.name = name
        self._event_type = event_type
        self.speed = speed
        self.stats = {"runs_batted_in": 0}

    def simulate_at_bat(self):
        return self._event_type, EVENT_CONFIG[self._event_type]["bases_to_advance"]


def test_walk_pushes_runners():
    players = [
        MockPlayer("A", "walk"),
        MockPlayer("B", "walk"),
        MockPlayer("C", "walk"),
        MockPlayer("D", "walk"),  # 押し出しで1点
        MockPlayer("A", "out"),
        MockPlayer("B", "out"),
        MockPlayer("C", "out"),
    ]
    game = BaseballGame(players)
    score, log = game.simulate_game(num_innings=1)
    assert score == 1
    assert players[3].stats["runs_batted_in"] == 1


def test_homerun_scores_all():
    players = [
        MockPlayer("A", "walk"),
        MockPlayer("B", "walk"),
        MockPlayer("C", "walk"),
        MockPlayer("D", "homerun"),  # 満塁ホームラン → 4点
        MockPlayer("A", "out"),
        MockPlayer("B", "out"),
        MockPlayer("C", "out"),
    ]
    game = BaseballGame(players)
    score, log = game.simulate_game(num_innings=1)
    assert score == 4
    assert players[3].stats["runs_batted_in"] == 4


def test_single_advances_runners():
    players = [
        MockPlayer("A", "single"),
        MockPlayer("B", "single"),
        MockPlayer("C", "single"),
        MockPlayer("D", "single"),
        MockPlayer("A", "out"),
        MockPlayer("B", "out"),
        MockPlayer("C", "out"),
    ]
    game = BaseballGame(players)
    score, log = game.simulate_game(num_innings=1)
    assert score >= 1  # 少なくとも1点入っているはず


def test_double_advances_runners_further():
    players = [
        MockPlayer("A", "walk"),
        MockPlayer("B", "double"),
        MockPlayer("C", "double"),
        MockPlayer("D", "double"),
        MockPlayer("A", "out"),
        MockPlayer("B", "out"),
        MockPlayer("C", "out"),
    ]
    game = BaseballGame(players)
    score, log = game.simulate_game(num_innings=1)
    assert score >= 2  # doubleが複数あれば複数点が見込める


def test_out_does_not_score():
    players = [
        MockPlayer("A", "out"),
        MockPlayer("B", "out"),
        MockPlayer("C", "out"),
    ]
    game = BaseballGame(players)
    score, log = game.simulate_game(num_innings=1)
    assert score == 0
    assert len(log[0]) == 3
    assert all(e[1] == "out" for e in log[0])


def test_rbi_tracking():
    players = [
        MockPlayer("A", "walk"),
        MockPlayer("B", "walk"),
        MockPlayer("C", "walk"),
        MockPlayer("D", "homerun"),
        MockPlayer("A", "out"),
        MockPlayer("B", "out"),
        MockPlayer("C", "out"),
    ]
    game = BaseballGame(players)
    game.simulate_game(num_innings=1)
    assert players[3].stats["runs_batted_in"] == 4
