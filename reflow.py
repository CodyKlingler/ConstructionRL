import json
from numpy import random


# this file reads in a flow file and generated a new one that is normally distributed from the orginal.

# what ratio of the data should the std. dev.
dist_perc = .15

# read input.json
flow = open("test_simulation/flow.json", "r")
flow_js = json.loads(flow.read())


# fields to write the normal distribution to
# This can also be retreived from flow_js[0][vehicle].keys()
v_fields = ['length', 'width', 'maxPosAcc', 'maxNegAcc', 'usualPosAcc', 'usualNegAcc', 'minGap', 'maxSpeed', 'headwayTime']


for v in range(0,len(flow_js)):
    for s in v_fields:
        n = flow_js[v]['vehicle'][s]
        new_n = random.normal(n, dist_perc*n)
        new_n = round(new_n,1)
        flow_js[v]['vehicle'][s] = new_n # change to normal dist.

    n = flow_js[v]['interval']
    new_n = random.normal(n, dist_perc*n)
    new_n = round(new_n,1)
    flow_js[v]['interval'] = new_n # change to normal dist.
    flow_js[v]['startTime'] = round(random.random_sample() * n,1)
    

# dump output.json
out_js = open('test_simulation copy/flow.json', 'w')
out_js.write(json.dumps(flow_js, indent=2))