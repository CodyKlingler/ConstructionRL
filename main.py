import cityflow

# load simulation
eng = cityflow.Engine('test_simulation/config.json', thread_num=1)

for i in range(0,2000):
    eng.next_step()