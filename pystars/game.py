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

HEIGHT = 800
WIDTH = 690
H_BGND = 710
H_MSG = 90

TOKEN_SIZE = 40
BLUE = pygame.color.THECOLORS['blue']
GREEN = pygame.color.THECOLORS['green']
WHITE = pygame.color.THECOLORS['white']
BLACK = pygame.color.THECOLORS['black']

COLORS = (BLUE, GREEN)

COLOR_NAME = { BLUE:'blue', GREEN:'green' }

parser = optparse.OptionParser()

class Player(object):

    def __init__(self, color, name=None):
        if not color in COLORS:
            raise ValueError("Invalid value for color. Use BLUE or GREEN")
        self.color = color
        self.tokens = pygame.sprite.LayeredUpdates()
        if name:
            self.name = name
        else:
            self.name = COLOR_NAME[self.color]

    def add_token(self, token):
        self.tokens.add(token)

    def move(self, token, to_slot):
        token.pos = to_slot.pos


class Token(pygame.sprite.Sprite):

    radius = int(TOKEN_SIZE/2.0)
    instances = []

    def __init__(self, screen, color, pos):
        pygame.sprite.Sprite.__init__(self)
        if not isinstance(pos, pygame.Rect):
            raise TypeError("Invalid type for token position")
        self.screen = screen
        self.selected = False
        self.pos = pos
        self.image = pygame.Surface((TOKEN_SIZE, TOKEN_SIZE))
        self.image.fill(WHITE)
        self.color = color
        self.played = False
        self.rect = pygame.draw.circle(self.screen, self.color,
                                       (self.pos.left, self.pos.top), Token.radius, 0)
        self.screen.blit(self.image, self)
        Token.instances.append(self)

    def on_click(self, event):
        if not self.selected:
            self.selected = True
            for t in Token.instances:
                if t is not self:
                    t.selected = False

    def _draw(self):
        if self.selected or self.played:
            return pygame.draw.circle(self.screen, self.color,
                                      (self.pos.left, self.pos.top),
                                      self.radius, 0)
        else:
            return pygame.draw.circle(self.screen, self.color,
                                      (self.pos.left, self.pos.top),
                                      self.radius, 3)

    def draw(self):
        return self._draw()

    def update(self):
        return self._draw()

    def move(self, to_slot):
        """Move the peg to a new position.
        """
        self.pos = to_slot


class Slot(pygame.Rect):

    def __init__(self, centerx, centery, height, width, token=None):
        pygame.Rect.__init__(self, (centerx, centery), (height, width))
        self.token = token

    def on_click(self, token):
        token.move(self)
        self.token = token


class Game(object):

    stars = dict(center=(345, 355),
                 top_left=(20, 217),
                 top_right=(213, 19),
                 right_upper=(483, 22),
                 right_lower=(666, 217),
                 bottom_right=(666, 493),
                 bottom_left=(474, 684),
                 left_lower=(205, 681),
                 left_upper=(18, 491),
                 )


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
        self.players = { BLUE:Player(BLUE), GREEN:Player(GREEN) }
        self.player = self.players[BLUE]
        self._setup_tokens()
        self.tokens = pygame.sprite.LayeredUpdates()
        for p in self.players:
            for t in self.players[p].tokens:
                self.tokens.add(t)
        self.active_token = None
        self.slots = []
        self._setup_slots()

    def _setup_tokens(self):
        for p in self.players:
            for t in Game.HOME[p]:
                self.players[p].add_token(Token(self.screen, p,
                                                pygame.Rect(t,(40,40))))

    def _setup_slots(self):
        for s in Game.stars.itervalues():
            slot = Slot(s[0], s[1], TOKEN_SIZE, TOKEN_SIZE)
            self.slots.append(slot)

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
        print "Click: %s" % (event.pos,)
        # First deal with selecting a token
        hits = self.tokens.get_sprites_at(event.pos)
        if len(hits) == 1:
            if hits[0].color == self.player.color:
                hits[0].on_click(event)
                self.active_token = hits[0]
                self.msg("Token selected. Click on a star to place your token.")
            else:
                self.msg("Wrong token")
            return
        if len(hits) > 1:
            self.msg("More than one hit")
        if not self.active_token:
            self.msg("Please select a token first")
            return
        # a token has already been selected, so the mouse click
        # is to choose a destination slot
        for i in self.slots:
            if i.collidepoint(event.pos):
                # TODO: Validation for move
                slot = i
                slot.on_click(self.active_token)
                self.active_token.played = True
                self.active_token.selected = False
                self.active_token = None
                if self.player.color is BLUE:
                    self.player  = self.players[GREEN]
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
    screen = game.screen
    screen.blit(game.background, (0, 0))
    while game.running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                game.on_key_down(event)
            if event.type == MOUSEBUTTONDOWN:
                game.on_mousebutton_down(event)
            if event.type == QUIT:
                game.on_quit()
        game.tokens.clear(game.screen, game.background)
        game.tokens.draw(game.screen)
        game.tokens.update()
        game.screen.blit(game.messages, (0, game.messages.top))
        pygame.display.flip()
        pygame.time.delay(100)


if __name__ == '__main__':
    (opts, args) = parser.parse_args()
    sys.exit(main(*args, **opts.__dict__))
