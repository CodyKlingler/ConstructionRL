import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding
import cityflow
import numpy as np
import os
from construction_router import *
import json

    # function to grab the roadnet inside a config.json
def get_roadnet(config_path: str) -> str:
    config_file = open(config_path+'/config.json', 'r')
    config_obj = json.loads(config_file.read())
    return config_obj['dir'] + config_obj['roadnetFile']

# no construction is applied. (lower bound on wait time) 
class construction_4x4_MD_no_cons(gym.Env):
    def __init__(self):
        self.name = "construction_4x4_MD_no_cons"
        self.X = 6
        self.Y = 6
        
        self.max_jobs = 3

        self.steps_per_episode = 6000
        self.sec_per_step = 1.0
        self.construction_period = (self.steps_per_episode // (self.X * self.Y))*self.max_jobs

        self.config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/4x4 test/normalized")
        self.cityflow = cityflow.Engine(os.path.join(self.config_dir, "config.json"), thread_num=1)
        self.router = construction_router(self.cityflow, get_roadnet(self.config_dir))
      
        
        self.possible_roads = [['road_2_4_2', 'road_3_4_2', 'road_4_4_2',  'road_1_4_0', 'road_2_4_0', 'road_3_4_0'],
                                ['road_2_3_2', 'road_3_3_2', 'road_4_3_2',  'road_1_3_0', 'road_2_3_0', 'road_3_3_0'],
                                ['road_2_2_2', 'road_3_2_2', 'road_4_2_2',  'road_1_2_0', 'road_2_2_0', 'road_3_2_0'],
                                ['road_1_2_3', 'road_1_3_3', 'road_1_4_3', 'road_1_1_1', 'road_1_2_1', 'road_1_3_1'],
                                ['road_2_2_3', 'road_2_3_3', 'road_2_4_3', 'road_2_1_1', 'road_2_2_1', 'road_2_3_1'],
                                ['road_3_2_3', 'road_3_3_3', 'road_3_4_3', 'road_3_1_1', 'road_3_2_1', 'road_3_3_1']]
                                
        self.jobs_left = [[1,1,1,1,1,1],   
                          [1,1,1,1,1,1],
                          [1,1,1,1,1,1],
                          [1,1,1,1,1,1],
                          [1,1,1,1,1,1],
                          [1,1,1,1,1,1]]

        self.blocked_routes = []
        self.blocked_route_states = []
        self.route_time_left = []

        for i in range(0, self.max_jobs):
            self.route_time_left.append(0)

        self.current_step = 0
        self.is_done = False
        self.reward_range = (-float('inf'), float('inf'))
                                                        # n left + cur_jobs + traffic
        self.observation_space = spaces.MultiDiscrete(([10]*self.X*self.Y)+[self.X,self.Y]*self.max_jobs)
        self.action_space = spaces.MultiDiscrete([self.X,self.Y])

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))

        # decrement the time remaining
        for i in range(0, len(self.route_time_left)):
            self.route_time_left[i] = self.route_time_left[i] - 1

        # mark expired jobs
        remove_indices = []
        for i in range(0,len(self.route_time_left)):
            if self.route_time_left[i] <= 0:
                remove_indices.append(i)
        # remove expired jobs
        for i in reversed(remove_indices):
            self.blocked_routes.pop(i)
            self.route_time_left.pop(i)
            self.blocked_route_states.pop((2*i)+1)
            self.blocked_route_states.pop(2*i)
            
        # if there are unscheduled workers
        if len(self.blocked_routes) < self.max_jobs:
            a = action[0]
            b = action[1]
            job_left = self.jobs_left[a][b] # see if the selected job needs completed
            valid_job = False
            if job_left <= 0: # find a random job of the ones remaining
                for x in range(0,self.X):
                    for y in range(0,self.Y):
                        if self.jobs_left[x][y] > 0:
                            a = x
                            b = y
                            valid_job = True
                if not valid_job and len(self.blocked_routes) == 0: # no job found and no jobs remaining
                    self.is_done = True
            else:
                valid_job = True

            self.jobs_left[a][b] -= 1
            self.jobs_left[a][b] = 0 if self.jobs_left[a][b] < 0 else self.jobs_left[a][b]
            self.blocked_routes.append(self.possible_roads[a][b])
            self.blocked_route_states.append(a)
            self.blocked_route_states.append(b)
            self.route_time_left.append(self.construction_period)
        
        self.cityflow.next_step()
        # self.router.reroute_construction(self.blocked_routes)

        state = self._get_state()
        reward = self._get_reward()

        self.current_step += 1

        if self.is_done:
            reward = 0.0

        if self.current_step + 1 == self.steps_per_episode:
            self.is_done = True


        return state, reward, self.is_done, {}




    def render(self, mode='human'):
        print("Current time: " + self.cityflow.get_current_time())

    def _get_state(self):
        lane_vehicles_dict = self.cityflow.get_lane_vehicle_count()
        lane_waiting_vehicles_dict = self.cityflow.get_lane_waiting_vehicle_count()
        
               # n_left - cur_job - lanes
        #([10]*6*3)+[3,6,3,6,3,6]+([100]*(18*2*3))

        cur_job = self.blocked_route_states.copy()

        while(len(cur_job) < self.max_jobs*2):
            cur_job.append(0)

        n_left_state = []
        for row in self.jobs_left:
            n_left_state += row

        state = n_left_state + cur_job
        return np.asarray(state, dtype=np.float32)

    def _get_reward(self):
        lane_waiting_vehicles_dict = self.cityflow.get_lane_waiting_vehicle_count()
        reward = 0.0

        for (road_id, num_vehicles) in lane_waiting_vehicles_dict.items():
                reward -= self.sec_per_step * num_vehicles
        return reward

    def set_replay_path(self, path):
        self.cityflow.set_replay_file(path)

    def seed(self, seed=None):
        self.cityflow.set_random_seed(seed)

    def get_path_to_config(self):
        return self.config_dir

    def set_save_replay(self, save_replay):
        self.cityflow.set_save_replay(save_replay)

    def reset(self):
        self.cityflow.reset()
        self.is_done = False
        self.current_step = 0

        self.jobs_left = [[1,1,1,1,1,1],   
                          [1,1,1,1,1,1],
                          [1,1,1,1,1,1],
                          [1,1,1,1,1,1],
                          [1,1,1,1,1,1],
                          [1,1,1,1,1,1]]

        self.blocked_routes = []
        self.blocked_route_states = []
        self.route_time_left = []
        
        return self._get_state()