import gym
import numpy as np
#from stable_baselines3.deepq.policies import MlpPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.env_checker import *
from stable_baselines3 import DQN, PPO

#from CityFlow_1x1_LowTraffic import CityFlow_1x1_LowTraffic

from construction_4x4_MD_first import *
from construction_4x4_MD_no_action_rand import *
from construction_4x4_MD_no_action import *
from construction_4x4_MD_no_cons import *
from construction_4x4_MD_rand import *

# make true to load the model saved with name model_n
load = False


env_list = [construction_4x4_MD_first(),
            construction_4x4_MD_no_action_rand(),
            construction_4x4_MD_no_action(),
            construction_4x4_MD_no_cons(),
            construction_4x4_MD_rand() ]
model_list = []
for env in env_list:
    print(env.name)
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log='logs')
    model_list.append( model )



log_interval = 1
total_episodes = 1
for i in range(0, total_episodes):
    for j in range(0,len(env_list)):
        env = env_list[j]
        print("aa: " + env.name)
        model = model_list[j]
        model.learn(total_timesteps=env.steps_per_episode*total_episodes, log_interval=log_interval, tb_log_name=env.name)

# model.save("trained_models/"+env.name)


obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
