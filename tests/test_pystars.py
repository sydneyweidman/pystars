__author__ = 'sweidman'

import unittest
import pygame
from pystars.game import Game, Player, Token, Slot

BLUE = pygame.color.THECOLORS['blue']
GREEN = pygame.color.THECOLORS['green']

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

    def test_add_token(self):
        self.players[BLUE].add_token(self.token)
        self.assertEqual(self.players[BLUE].tokens.get_sprite(0).color, BLUE)
        self.assertEqual(len(self.players[BLUE].tokens), 1)

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_game_running(self):
        assert self.game.running

if __name__ == '__main__':
    unittest.main()
