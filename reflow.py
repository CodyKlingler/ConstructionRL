import json
from numpy import random
import random as pyrand
import os
import random as pyrand
import copy

# this file reads in a flow file and generated a new one that is normally distributed from the orginal.

# what ratio of the data should the std. dev.

def normalize_traffic_flow(scenario_path:str, deviation:float, interval:float, interval_deviation:float, vehicle_mult:float) -> str:

    # read input.json
    og_config_path = scenario_path + 'config.json'
    og_config = open(og_config_path, "r").read()
    config_js = json.loads(og_config)

    og_flow_path = scenario_path + config_js['flowFile']
    og_roadnet_path = scenario_path + config_js['roadnetFile']

    # Check whether the normalized folder exists
    if not os.path.exists(scenario_path + 'normalized'):
        # Create a new directory because it does not exist
        os.makedirs(scenario_path + 'normalized')

    # copy roadnet to normalized folder
    og_roadnet = open(og_roadnet_path, 'r')
    new_roadnet = open(scenario_path + 'normalized/' + config_js['roadnetFile'], 'w')
    new_roadnet.write(og_roadnet.read())

    # copy config to normalized folder, with new seed
    config_js['seed'] += pyrand.randint(0, 10_000_000)
    config_js['dir'] += 'normalized/'
    new_config = open(scenario_path + 'normalized/' + 'config.json', 'w')
    new_config.write(json.dumps(config_js, indent=2))

    # now we will normalize traffic flow
    # open old flow.js
    flow_js = open(og_flow_path, 'r').read()
    flow_js = json.loads(flow_js)

    # fields to write the normal distribution to
    # This can also be retreived from flow_js[0][vehicle].keys()
    v_fields = ['length', 'width', 'maxPosAcc', 'maxNegAcc', 'usualPosAcc', 'usualNegAcc', 'minGap', 'maxSpeed', 'headwayTime']

    l = len(flow_js)
    for v in range(0,l):
        for _ in range(0,vehicle_mult):        
            d2 = copy.deepcopy(flow_js[v])
            flow_js.append(d2)

    for v in range(0,len(flow_js)):
        for s in v_fields:
            n = flow_js[v]['vehicle'][s]
            new_n = random.normal(n, deviation*n)
            new_n = round(new_n,1)
            flow_js[v]['vehicle'][s] = new_n # change to normal dist.

        if interval != 0:
            new_n = random.normal(interval, interval_deviation*interval)
            new_n = round(new_n,2)
            if new_n <= 0:
                new_n = interval
            flow_js[v]['interval'] = new_n  #new_n # change to normal dist.
            flow_js[v]['startTime'] = round(pyrand.random()*interval, 2)
            # flow_js[v]['endTime']
            


    # dump output.json
    out_js = open(scenario_path + 'normalized/' + config_js['flowFile'], 'w')
    out_js.write(json.dumps(flow_js, indent=2))