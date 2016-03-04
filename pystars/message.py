import pygame

__author__ = 'sweidman'

FONT_SIZE = 32
BLACK = pygame.color.THECOLORS['black']
WHITE = pygame.color.THECOLORS['white']


class MessageArea(pygame.Surface):

    def __init__(self, top, left, height, width, initial_text=None,
                 margin=10, duration=5, fg_color=BLACK,
                 bg_color=WHITE, font_size=FONT_SIZE, font=None):
        self.height = height
        self.top = top
        self.left = left
        self.width = width
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font_size = font_size
        self.initial_text = initial_text
        self.margin = margin
        self.duration = duration
        self.font = font
        super(MessageArea, self).__init__((self.width, self.height))
        self._setup_messagebar()

    def _setup_messagebar(self):
        self.fill(self.bg_color)
        pygame.font.init()
        self.msgsrc = pygame.font.SysFont(self.font, self.font_size)
        self.surf = self.msgsrc.render(self.initial_text, True, self.fg_color)
        self.blit(self.surf, (self.margin, self.left))

    def display(self, text):
        print text
        self.fill(self.bg_color)
        self.surf = self.msgsrc.render(text, True, self.fg_color)
        self.blit(self.surf, (self.margin, self.left))

    def clear(self):
        self.surf.fill(self.bg_color)
        self.fill(self.bg_color)
        self.blit(self.surf, (self.margin, self.left))
