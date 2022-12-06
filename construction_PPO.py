import gym
import numpy as np
#from stable_baselines3.deepq.policies import MlpPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_checker import *
from stable_baselines3 import DQN, PPO

#from CityFlow_1x1_LowTraffic import CityFlow_1x1_LowTraffic
from construction_4x4_env import *

# make true to load the model saved with name model_n
load = False
logdir = "logdir"

# check_env(construction_4x2_env())

env = construction_4x4_env()
if load:
    model = PPO.load("ppo_1x1")
else:
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=logdir)

log_interval = 1
total_episodes = 20
for i in range(0, total_episodes):
    model.learn(total_timesteps=env.steps_per_episode*total_episodes, log_interval=log_interval, tb_log_name="ppo1x1_log")
model.save("ppo_1x1")


obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
