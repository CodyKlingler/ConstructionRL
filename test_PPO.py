import gym
import numpy as np
#from stable_baselines3.deepq.policies import MlpPolicy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import DQN, PPO

from CityFlow_1x1_LowTraffic import CityFlow_1x1_LowTraffic

if __name__ == "__main__":
    env = CityFlow_1x1_LowTraffic()
    model = PPO("MlpPolicy", env, verbose=1)
    log_interval = 10
    total_episodes = 100
    model.learn(total_timesteps=env.steps_per_episode*total_episodes, log_interval=log_interval)
    model.save("ppo_1x1")

    model = PPO.load("ppo_1x1")

    obs = env.reset()
    done = False
    while not done:
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        print(rewards)
