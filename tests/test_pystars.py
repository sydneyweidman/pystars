__author__ = 'sweidman'

import unittest
import pygame
from pystars.game import Game, Player, Token, Slot, InvalidMove

BLUE = pygame.color.THECOLORS['blue']
GREEN = pygame.color.THECOLORS['green']


class Event(object):
    "Dummy class for creating mock GUI events"

    def __init__(self, pos=None, eventtype=pygame.locals.MOUSEBUTTONDOWN):
        self.pos = pos
        self.type = eventtype


class TestToken(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.token = Token(self.game.screen, BLUE, pygame.Rect((0,0),(40,40)))

    def test_on_click(self):
        self.token.selected = False
        event = pygame.locals.MOUSEBUTTONDOWN
        self.token.on_click(event)
        self.assertTrue(self.token.selected)
        self.token.on_click(event)
        self.assertTrue(self.token.selected, "Make sure the token isn't deselected")

    def test_token_count(self):
        self.assertEqual(len(self.game.players[BLUE].tokens), 3)
        self.assertEqual(len(self.game.players[GREEN].tokens), 3)

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.players = {}
        self.token = Token(self.game.screen, BLUE, pygame.Rect((0,0),(40,40)))
        self.players[BLUE] = Player(color=BLUE)
        self.players[GREEN] = Player(color=GREEN)

    def test_player_count(self):
        self.assertEqual(len(self.game.players), 2)

    def test_wrong_token(self):
        "Make sure moving the wrong token raises InvalidMove"
        green_token = Token(self.game.screen, GREEN, pygame.Rect((40, 366), (40, 40)))
        self.players[GREEN].add_token(green_token)
        self.assertRaises(InvalidMove, self.players[BLUE].move, green_token, self.game.slots[7])

    def test_add_token(self):
        self.players[BLUE].add_token(self.token)
        self.assertEqual(self.players[BLUE].tokens[0].color, BLUE)
        self.assertEqual(len(self.players[BLUE].tokens), 1)

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_game_running(self):
        assert self.game.running

    def test_initial_winner_state(self):
        self.assertIsNone(self.game.winner)

    def execute_moves(self, slot_list):
        event = Event()
        for idx in range(3):
            for color in [BLUE, GREEN]:
                event.pos = self.game.HOME[color][idx]
                self.game.on_mousebutton_down(event)
                try:
                    event.pos = self.game.stars[slot_list.pop()]
                except IndexError:
                    break
                self.game.on_mousebutton_down(event)

    def test_non_winner(self):
        slot_list = ['top_left', 'right_upper', 'center', 'right_lower', 'bottom_left']
        self.execute_moves(slot_list)
        self.assertIsNone(self.game.winner)

    def test_winner(self):
        slot_list = ['top_right', 'right_upper', 'center', 'right_lower', 'bottom_left']
        self.execute_moves(slot_list)
        self.assertIsNotNone(self.game.winner)

if __name__ == '__main__':
    unittest.main()
