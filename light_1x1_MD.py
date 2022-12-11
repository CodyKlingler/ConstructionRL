import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding
import cityflow
import numpy as np
import os

class light_1x1_D(gym.Env):
    self.name = "light_1x1_D"

    metadata = {'render.modes':['human']}
    def __init__(self):
        #super(CityFlow_1x1_LowTraffic, self).__init__()
        # hardcoded settings from "config.json" file
        self.config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1x1_config")
        self.cityflow = cityflow.Engine(os.path.join(self.config_dir, "config.json"), thread_num=1)
        self.intersection_id = "intersection_1_1"

        self.sec_per_step = 1.0

        self.steps_per_episode = 1000
        self.current_step = 0
        self.is_done = False
        self.reward_range = (-float('inf'), float('inf'))
        self.start_lane_ids = \
            ["road_0_1_0_0",
             "road_0_1_0_1",
             "road_1_0_1_0",
             "road_1_0_1_1",
             "road_2_1_2_0",
             "road_2_1_2_1",
             "road_1_2_3_0",
             "road_1_2_3_1"]

        self.all_lane_ids = \
            ["road_0_1_0_0",
             "road_0_1_0_1",
             "road_1_0_1_0",
             "road_1_0_1_1",
             "road_2_1_2_0",
             "road_2_1_2_1",
             "road_1_2_3_0",
             "road_1_2_3_1",
             "road_1_1_0_0",
             "road_1_1_0_1",
             "road_1_1_1_0",
             "road_1_1_1_1",
             "road_1_1_2_0",
             "road_1_1_2_1",
             "road_1_1_3_0",
             "road_1_1_3_1"]

        """
        road id:
        ["road_0_1_0",
         "road_1_0_1",
         "road_2_1_2",
         "road_1_2_3",
         "road_1_1_0",
         "road_1_1_1",
         "road_1_1_2",
         "road_1_1_3"]
         
        start road id:
        ["road_0_1_0",
        "road_1_0_1",
        "road_2_1_2",
        "road_1_2_3"]
        
        lane id:
        ["road_0_1_0_0",
         "road_0_1_0_1",
         "road_1_0_1_0",
         "road_1_0_1_1",
         "road_2_1_2_0",
         "road_2_1_2_1",
         "road_1_2_3_0",
         "road_1_2_3_1",
         "road_1_1_0_0",
         "road_1_1_0_1",
         "road_1_1_1_0",
         "road_1_1_1_1",
         "road_1_1_2_0",
         "road_1_1_2_1",
         "road_1_1_3_0",
         "road_1_1_3_1"]
         
         start lane id:
         ["road_0_1_0_0",
         "road_0_1_0_1",
         "road_1_0_1_0",
         "road_1_0_1_1",
         "road_2_1_2_0",
         "road_2_1_2_1",
         "road_1_2_3_0",
         "road_1_2_3_1"]
        """

        self.mode = "start_waiting"
        assert self.mode == "all_all" or self.mode == "start_waiting", "mode must be one of 'all_all' or 'start_waiting'"
        """
        `mode` variable changes both reward and state.
        
        "all_all":
            - state: waiting & running vehicle count from all lanes (incoming & outgoing)
            - reward: waiting vehicle count from all lanes
            
        "start_waiting" - 
            - state: only waiting vehicle count from only start lanes (only incoming)
            - reward: waiting vehicle count from start lanes
        """
        """
        if self.mode == "all_all":
            self.state_space = len(self.all_lane_ids) * 2

        if self.mode == "start_waiting":
            self.state_space = len(self.start_lane_ids)
        """
        
        self.action_space = spaces.Discrete(9)
        if self.mode == "all_all":
            self.observation_space = spaces.MultiDiscrete([100]*16)
        else:
            self.observation_space = spaces.MultiDiscrete([100]*8)

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))
        self.cityflow.set_tl_phase(self.intersection_id, action)
        self.cityflow.next_step()

        state = self._get_state()
        reward = self._get_reward()

        self.current_step += 1

        if self.is_done:
            logger.warn("You are calling 'step()' even though this environment has already returned done = True. "
                        "You should always call 'reset()' once you receive 'done = True' "
                        "-- any further steps are undefined behavior.")
            reward = 0.0

        if self.current_step + 1 == self.steps_per_episode:
            self.is_done = True
            

        return state, reward, self.is_done, {}


    def reset(self):
        self.cityflow.reset()
        self.is_done = False
        self.current_step = 0

        return self._get_state()

    def render(self, mode='human'):
        print("Current time: " + self.cityflow.get_current_time())

    def _get_state(self):
        lane_vehicles_dict = self.cityflow.get_lane_vehicle_count()
        lane_waiting_vehicles_dict = self.cityflow.get_lane_waiting_vehicle_count()

        state = None

        if self.mode=="all_all":
            state = np.zeros(len(self.all_lane_ids) * 2, dtype=np.float32)
            for i in range(len(self.all_lane_ids)):
                state[i*2] = lane_vehicles_dict[self.all_lane_ids[i]]
                state[i*2 + 1] = lane_waiting_vehicles_dict[self.all_lane_ids[i]]

        if self.mode=="start_waiting":
            state = np.zeros(len(self.start_lane_ids), dtype=np.float32)
            for i in range(len(self.start_lane_ids)):
                state[i] = lane_waiting_vehicles_dict[self.start_lane_ids[i]]

        return state

    def _get_reward(self):
        lane_waiting_vehicles_dict = self.cityflow.get_lane_waiting_vehicle_count()
        reward = 0.0


        if self.mode == "all_all":
            for (road_id, num_vehicles) in lane_waiting_vehicles_dict.items():
                if road_id in self.all_lane_ids:
                    reward -= self.sec_per_step * num_vehicles

        if self.mode == "start_waiting":
            for (road_id, num_vehicles) in lane_waiting_vehicles_dict.items():
                if road_id in self.start_lane_ids:
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