import optparse
import os
import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN
from pygame.locals import K_n, K_q, K_r, K_p
from pygame.locals import K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8
from pystars.message import MessageArea

package_directory = os.path.dirname(os.path.abspath(__file__))

NUMKEYS = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8]

HEIGHT = 820
WIDTH = 710
H_BGND = 730
H_MSG = 90

TOKEN_SIZE = 40
BLUE = pygame.color.THECOLORS['blue']
GREEN = pygame.color.THECOLORS['green']
WHITE = pygame.color.THECOLORS['white']
BLACK = pygame.color.THECOLORS['black']

COLORS = (BLUE, GREEN)

COLOR_NAME = {BLUE: 'blue', GREEN: 'green'}

parser = optparse.OptionParser()

stars = dict(left_upper =      (20, 217),
             top_right=(483, 22),
             right_upper=(666, 217),
             right_lower=(666, 493),
             bottom_right=(474, 684),
             bottom_left=(205, 681),
             left_lower=(18, 491),
             top_left=(213, 19),
             center=(345, 355),
             )

ring_names = """top_left
top_right
right_upper
right_lower
bottom_right
bottom_left
left_lower
left_upper""".splitlines()

adjacents = { 'center': ring_names,
              'top_left': ['top_right','left_upper','center'],
              'top_right':['top_left', 'right_upper', 'center'],
              'right_upper':['top_right', 'right_lower', 'center'],
              'right_lower':['right_upper', 'bottom_right', 'center'],
              'bottom_right':['right_lower', 'bottom_left', 'center'],
              'bottom_left':['bottom_right', 'left_lower', 'center'],
              'left_lower':['bottom_left', 'left_upper', 'center'],
              'left_upper':['left_lower', 'top_left', 'center'],}


class InvalidMove(Exception):
    pass

class Player(object):
    def __init__(self, color, name=None, is_cpu=False):
        if color not in COLORS:
            raise ValueError("Invalid value for color. Use BLUE or GREEN")
        self.color = color
        self.tokens = []
        self._is_cpu = is_cpu
        if name:
            self.name = name
        else:
            self.name = COLOR_NAME[self.color]

    @property
    def is_cpu(self):
        return self._is_cpu

    @is_cpu.setter
    def is_cpu(self, value):
        if value:
            self._is_cpu = True
        else:
            self._is_cpu = False

    def add_token(self, token):
        self.tokens.append(token)

    def move(self, token, to_slot):
        if self.is_cpu:
            # TODO: Implement CPU Move
            pass
        if token.color != self.color or token not in self.tokens:
            raise InvalidMove("That token is not yours")
        token.move(to_slot)


class Token(pygame.Rect):
    radius = int(TOKEN_SIZE / 2.0)
    instances = []

    def __init__(self, screen, color, pos):
        if not isinstance(pos, pygame.Rect):
            raise TypeError("Invalid type for token position")
        pygame.Rect.__init__(self, pos)
        self.image = pygame.Surface((TOKEN_SIZE, TOKEN_SIZE))
        self.image.fill(WHITE)
        self.screen = screen
        self.color = color
        self.selected = False
        self.played = False
        self._draw()
        Token.instances.append(self)

    def on_click(self, event):
        if not self.selected:
            self.selected = True
        for t in Token.instances:
            if t is not self:
                t.selected = False
        self.update()

    def _draw(self):
        if self.selected or self.played:
            border = 0
        else:
            border = 3
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, border)
        self.screen.blit(self.image, self)

    def draw(self):
        return self._draw()

    def update(self):
        return self._draw()

    def move(self, to_slot):
        """Move the peg to a new position.
        """
        self.top, self.left = to_slot.top, to_slot.left


class Slot(pygame.Rect):

    by_name = {}

    def __init__(self, rect, token=None, name=None, adjacents=None):
        pygame.Rect.__init__(self, rect)
        self.token = token
        if not name:
            name = "{0:s}".format((self.left, self.top), )
        self.name = name
        Slot.by_name[self.name] = self

    def on_click(self, token):
        print self
        print self.left, self.top
        token.move(self)
        self.token = token

    def __str__(self):
        return self.name


class Game(object):

    winners = [(stars['top_left'], stars['center'], stars['bottom_right']),
               (stars['top_right'], stars['center'], stars['bottom_left']),
               (stars['right_upper'], stars['center'], stars['left_lower']),
               (stars['right_lower'], stars['center'], stars['left_upper']),
               ]

    HOME = {
        BLUE: ((35, 40),
               (35, 100),
               (35, 160),),
        GREEN: ((660, 40),
                (660, 100),
                (660, 160),),
    }

    def __init__(self, mode=(WIDTH, HEIGHT)):
        self.screen = pygame.display.set_mode(mode)
        self.imgfile = os.path.join(package_directory, 'images', 'board.png')
        self.background = pygame.image.load(self.imgfile).convert()
        self.messages = MessageArea(H_BGND, 0, H_MSG, WIDTH, "BLUE'S TURN")
        self.msg = self.messages.display
        self.screen.blit(self.messages, (0, self.messages.top))
        self.running = True
        self.players = {BLUE: Player(BLUE), GREEN: Player(GREEN)}
        self.player = self.players[BLUE]
        self.winner = None
        self._setup_tokens()
        self.tokens = []
        for p in self.players:
            for t in self.players[p].tokens:
                self.tokens.append(t)
        self.active_token = None
        self.active_slot = None
        self.slots = []
        self._setup_slots()

    def _setup_tokens(self):
        for color in self.players:
            for t in Game.HOME[color]:
                tkn = Token(self.screen, color, pygame.Rect(t, (TOKEN_SIZE, TOKEN_SIZE)))
                self.players[color].add_token(tkn)

    def _setup_slots(self):
        for k, s in stars.iteritems():
            rect = pygame.Rect((s[0], s[1]), (TOKEN_SIZE, TOKEN_SIZE))
            slot = Slot(rect, name=k)
            self.slots.append(slot)

    def all_tokens_played(self):
        return all([t.played for t in self.tokens])

    def check_winner(self):
        for color in self.players:
            alltokens = [(i.left, i.top) for i in self.players[color].tokens]
            for trio in self.winners:
                if set(trio) == set(alltokens):
                    return color
        return None

    def on_key_down(self, event):
        """Handle keyboard events"""
        if event.key == K_r:
            self.msg("Restarting")
            self.__init__()
            self.screen.blit(self.background, (0, 0))
        if event.key in NUMKEYS:
            print "Not implemented"
            return
        if event.key == K_n:
            print "Not implemented"
            return
        if event.key == K_p:
            print "Not implemented"
            return
        if event.key == K_q:
            self.on_quit()

    def on_mousebutton_down(self, event):
        """Handle mouse events"""
        if self.winner:
            self.msg("Press r to restart or q to quit.")
            return
        print "Click: %s" % (event.pos,)
        # First deal with selecting a token
        for tkn in self.player.tokens:
            if tkn.collidepoint(event.pos):
                tkn.on_click(event)
                self.active_token = tkn
                if self.all_tokens_played():
                    slot = [i for i in self.slots if i.collidepoint(event.pos)][0]
                    self.active_slot = slot
                    self.msg("Token at %s selected. Click on a star..." % (slot.name,))
                else:
                    self.msg("Token selected. Click on a star...")
                return
        if not self.active_token:
            self.msg("Please select a token first")
            return
        # a token has already been selected, so the mouse click
        # is to choose a destination slot
        for dst in self.slots:
            if dst.collidepoint(event.pos):
                # TODO: Validation for move
                try:
                    if self.all_tokens_played():
                        if dst.name not in adjacents[self.active_slot.name]:
                            raise InvalidMove
                except InvalidMove:
                    self.msg("Move from %s to %s is invalid" % (self.active_slot.name, dst.name,))
                    return
                dst.on_click(self.active_token)
                self.active_slot = dst
                self.active_token.played = True
                self.active_token.selected = False
                self.active_token = None
                self.winner = self.check_winner()
                if self.winner is not None:
                    self.msg("%s WINS! Press r to restart or q to quit." % (self.player.name,))
                    return
                if self.player.color is BLUE:
                    self.player = self.players[GREEN]
                else:
                    self.player = self.players[BLUE]
                self.msg(r"Token moved. %s's TURN" % (self.player.name.upper(),))
                return
        return

    def on_quit(self):
        self.running = False


def main(*args, **kwargs):
    """Start the main loop

    Arguments:
    - `*args`:
    - `**kwargs`:
    """
    pygame.init()
    game = Game()
    while game.running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                game.on_key_down(event)
            if event.type == MOUSEBUTTONDOWN:
                game.on_mousebutton_down(event)
            if event.type == QUIT:
                game.on_quit()
        game.screen.blit(game.messages, (0, game.messages.top))
        game.screen.blit(game.background, (0, 0))
        for t in game.tokens:
            t.update()
        pygame.display.flip()
        pygame.time.delay(100)


if __name__ == '__main__':
    (opts, args) = parser.parse_args()
    sys.exit(main(*args, **opts.__dict__))
