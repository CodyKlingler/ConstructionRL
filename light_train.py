import gym
import numpy as np
#from stable_baselines3.deepq.policies import MlpPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import DQN, PPO

from light_1x1_MD import CityFlow_1x1_LowTraffic
from construction_4x4_MD_rand import *


# make true to load the model saved with name model_n
load = False
logdir = "logdir"

env = CityFlow_1x1_LowTraffic()
if load:
    model = PPO.load("ppo_1x1")
else:
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=logdir)

log_interval = 10
total_episodes = 200
model.learn(total_timesteps=env.steps_per_episode*total_episodes, log_interval=log_interval, tb_log_name="ppo1x1_log")
model.save("ppo_1x1")

obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
