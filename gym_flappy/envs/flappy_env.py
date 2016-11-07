import gym
from gym import error, spaces, utils
from gym.utils import seeding

class FlappyEnv(gym.Env):
  metadata = {'render.modes': ['human']}
  (w, h) = (640, 480)


  def __init__(self):
    self.action_space = spaces.Tuple((spaces.discrete(2)))
    self.observation_space = spaces.Box(low=-1, high=1, shape=(w,h))

  def _step(self, action):
    print 'step'

  def _reset(self):
    print 'reset'

  def _render(self, mode='human', close=False):
    print 'render'
