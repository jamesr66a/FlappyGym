from gym.envs.registration import register
import envs

register(
  id='flappy-v0',
  entry_point='gym_flappy.envs:FlappyEnv',
)
