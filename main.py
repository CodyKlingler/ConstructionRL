import cityflow
import json
import heapq
from reflow import *
from construction import *

# various simulations that may run. (folder containing config)
ny_sim =    'data/NewYork/16_3/'
nyc_sim =   'data/manhattan/'
jinan_sim = 'jinan_normalized/'

    ############### SETTINGS ###############
# change to select the current simulation
selected_scenario = jinan_sim

# set to true to adjust simulation according to normal distribution.
normalized = False
deviation = .15 # deviation to normalize data to (percent of original)

# the number of steps to simulate
n_steps = 400
    ############# END  SETTINGS##############

# go to normalized foler
if normalized:
    selected_scenario += 'normalized/' if normalized else ''

# select config file
selected_scenario += 'config.json'

# function to grab the roadnet inside a config.json
def get_roadnet(config_path: str) -> str:
    config_file = open(config_path, 'r')
    config_obj = json.loads(config_file.read())
    return config_obj['dir'] + config_obj['roadnetFile']

# the routes blocked in the current simulation
blocked_routes = ["road_1_2_1", "road_2_2_1", "road_4_2_1", "road_1_3_3", "road_2_3_3", "road_4_3_3"]

# create simulation
eng = cityflow.Engine(selected_scenario, thread_num=4)

# create a construction routing object for the simulation
router: construction_router = construction_router(eng, get_roadnet(selected_scenario))

for i in range(0,n_steps):

    # print simulation progress
    if i % (n_steps // 100) == 0:
        print(f"\r{round((i/n_steps)*100,1)}%", end='')
        router.print_status()

    # Do a simulation step
    eng.next_step()

    # reroute any vehicles that will enter an active contruction zone.
    router.reroute_construction(blocked_routes)
    
print()