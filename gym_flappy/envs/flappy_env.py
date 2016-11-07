import gym
from gym import error, spaces, utils
from gym.utils import seeding

class FlappyEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    print 'init'

  def _step(self, action):
    print 'step'

  def _reset(self):
    print 'reset'

  def _render(self, mode='human', close=False):
    print 'render'
