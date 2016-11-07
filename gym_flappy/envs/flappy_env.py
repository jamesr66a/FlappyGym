import gym
from gym import error, spaces, utils
from gym.utils import seeding

class FlappyEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    dims = (640, 480)
    self.action_space = (spaces.Discrete(2))
    self.observation_space = spaces.Box(low=-1, high=1, shape=dims)

  def _step(self, action):
    print 'step'

  def _reset(self):
    print 'reset'

  def _render(self, mode='human', close=False):
    print 'render'
