import gym
import numpy as np
#from stable_baselines3.deepq.policies import MlpPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_checker import *
from stable_baselines3 import DQN, PPO

#from CityFlow_1x1_LowTraffic import CityFlow_1x1_LowTraffic
from construction_4x4_MD import *
from construction_4x4_MD_copy import *
from construction_4x2_MD import *

# make true to load the model saved with name model_n
load = False

# check_env(construction_4x2_env())

env = construction_4x4_MD()
if load:
    model = PPO.load("trained_models/"+env.name)
else:
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log='logs')

log_interval = 1
total_episodes = 20
for i in range(0, total_episodes):
    model.learn(total_timesteps=env.steps_per_episode*total_episodes, log_interval=log_interval, tb_log_name=env.name)
model.save("trained_models/"+env.name)


obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
