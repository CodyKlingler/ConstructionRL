import cityflow
import json
import heapq
from reflow import *
from construction_train import *

# various simulations that may run. (points to folder containing config)
ny_sim =    'data/NewYork/16_3/'
nyc_sim =   'data/manhattan/'
jinan_sim = 'data/Jinan/3_4/'
x4_sim =    'data/4x4 test/'
x2_sim =    'data/4x2/'
hang_sim =  'data/Hangzhou/4_4/'

    ############### SETTINGS ###############
selected_scenario = x4_sim  # change to select the current simulation
n_steps = 400               # the number of steps to simulate

normalized = True           # set to true to adjust simulation according to normal distribution.
deviation = .15             # deviation to normalize data to (percent of original)
vehicle_mult = 6
interval = 100
interval_deviation = .33
    ############# END  SETTINGS##############

# go to normalized folder
if normalized:
    normalize_traffic_flow(selected_scenario, deviation, interval, interval_deviation, vehicle_mult)
    selected_scenario += 'normalized/'

# select config file
selected_config = selected_scenario + 'config.json'



# function to grab the roadnet inside a config.json
def get_roadnet(config_path: str) -> str:
    config_file = open(config_path, 'r')
    config_obj = json.loads(config_file.read())
    return config_obj['dir'] + config_obj['roadnetFile']

# the routes blocked in the current simulation
blocked_routes = ['road_2_4_2', 'road_1_4_0'] #"road_1_2_1", "road_2_2_1", "road_4_2_1", "road_1_3_3", "road_2_3_3", "road_4_3_3"]

# create simulation
eng = cityflow.Engine(selected_config, thread_num=4)

# create a construction routing object for the simulation
router: construction_router = construction_router(eng, get_roadnet(selected_config))

# actually run simulation
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