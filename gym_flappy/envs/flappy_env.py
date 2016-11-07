import gym
from gym import error, spaces, utils
from gym.utils import seeding
import Image
import os
import pygame
import random
import sys

class FlappyEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    dims = (640, 480)
    self.action_space = (spaces.Discrete(2))
    self.observation_space = spaces.Box(low=-1, high=1, shape=dims)

    self.SCREENWIDTH = 288
    self.SCREENHEIGHT = 512

    self.PIPEGAPSIZE = 100
    self.BASEY = self.SCREENHEIGHT * 0.79
    self.IMAGES = {}
    self.SOUNDS = {}
    self.HITMASKS = {}

    file_prefix = os.path.dirname(__file__);

    self.PLAYERS_LIST = (
      # red bird
      (
          file_prefix+'/FlapPyBird/assets/sprites/redbird-upflap.png',
          file_prefix+'/FlapPyBird/assets/sprites/redbird-midflap.png',
          file_prefix+'/FlapPyBird/assets/sprites/redbird-downflap.png',
      ),
      # blue bird
      (
          # amount by which base can maximum shift to left
          file_prefix+'/FlapPyBird/assets/sprites/bluebird-upflap.png',
          file_prefix+'/FlapPyBird/assets/sprites/bluebird-midflap.png',
          file_prefix+'/FlapPyBird/assets/sprites/bluebird-downflap.png',
      ),
      # yellow bird
      (
          file_prefix+'/FlapPyBird/assets/sprites/yellowbird-upflap.png',
          file_prefix+'/FlapPyBird/assets/sprites/yellowbird-midflap.png',
          file_prefix+'/FlapPyBird/assets/sprites/yellowbird-downflap.png',
      ),
    )

    self.BACKGROUNDS_LIST = (
      file_prefix+'/FlapPyBird/assets/sprites/background-day.png',
      file_prefix+'/FlapPyBird/assets/sprites/background-night.png',
    )

    self.PIPES_LIST = (
      file_prefix+'/FlapPyBird/assets/sprites/pipe-green.png',
      file_prefix+'/FlapPyBird/assets/sprites/pipe-red.png',
    )

    self.SCREEN = pygame.display.set_mode((self.SCREENWIDTH, self.SCREENHEIGHT))

    self.IMAGES['numbers'] = (
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/0.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/1.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/2.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/3.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/4.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/5.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/6.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/7.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/8.png').convert_alpha(),
        pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/9.png').convert_alpha()
    )

    self.IMAGES['gameover'] = pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/gameover.png')\
      .convert_alpha()
    # message sprite for welcome screen
    self.IMAGES['message'] = pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/message.png')\
      .convert_alpha()
    # base (ground) sprite
    self.IMAGES['base'] = pygame.image.load(file_prefix+'/FlapPyBird/assets/sprites/base.png')\
      .convert_alpha()

    randBg = random.randint(0, len(self.BACKGROUNDS_LIST) - 1)
    self.IMAGES['background'] = pygame.image.load(self.BACKGROUNDS_LIST[randBg]).convert()

    randPlayer = random.randint(0, len(self.PLAYERS_LIST) - 1)
    self.IMAGES['player'] = (
        pygame.image.load(self.PLAYERS_LIST[randPlayer][0]).convert_alpha(),
        pygame.image.load(self.PLAYERS_LIST[randPlayer][1]).convert_alpha(),
        pygame.image.load(self.PLAYERS_LIST[randPlayer][2]).convert_alpha(),
    )

    # select random pipe sprites
    pipeindex = random.randint(0, len(self.PIPES_LIST) - 1)
    self.IMAGES['pipe'] = (
        pygame.transform.rotate(
            pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(), 180),
        pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(),
    )

    # hismask for pipes
    self.HITMASKS['pipe'] = (
        self.getHitmask(self.IMAGES['pipe'][0]),
        self.getHitmask(self.IMAGES['pipe'][1]),
    )

    # hitmask for player
    self.HITMASKS['player'] = (
        self.getHitmask(self.IMAGES['player'][0]),
        self.getHitmask(self.IMAGES['player'][1]),
        self.getHitmask(self.IMAGES['player'][2]),
    )

    self.score = self.playerIndex = self.loopIter = 0
    self.playerx = int(self.SCREENWIDTH * 0.2)
    self.playery = int((self.SCREENHEIGHT - self.IMAGES['player'][0].get_height()) / 2)

    self.basex = 0
    self.baseShift = self.IMAGES['base'].get_width() - \
      self.IMAGES['background'].get_width()

    newPipe1 = self.getRandomPipe()
    newPipe2 = self.getRandomPipe()

    # list of upper pipes
    self.upperPipes = [
        {'x': self.SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': self.SCREENWIDTH + 200 + (self.SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    self.lowerPipes = [
        {'x': self.SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': self.SCREENWIDTH + 200 + (self.SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    self.pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    self.playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    self.playerMaxVelY =  10   # max vel along Y, max descend speed
    self.playerMinVelY =  -8   # min vel along Y, max ascend speed
    self.playerAccY    =   1   # players downward accleration
    self.playerFlapAcc =  -9   # players speed on flapping
    self.playerFlapped = False # True when player flaps
 

  def getRandomPipe(self):
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(self.BASEY * 0.6 - self.PIPEGAPSIZE))
    gapY += int(self.BASEY * 0.2)
    pipeHeight = self.IMAGES['pipe'][0].get_height()
    pipeX = self.SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + self.PIPEGAPSIZE}, # lower pipe
    ]


  def getHitmask(self, image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask


  def _step(self, action):
    print 'step'

  def _reset(self):
    print 'reset'

  def _render(self, mode='human', close=False):
    pygame.image.save(self.SCREEN, 'temp.bmp')
    bmpfile = Image.open('temp.bmp');
    return bmpfile.bits
