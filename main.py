import cityflow

# load simulation
eng = cityflow.Engine('test_simulation copy/config.json', thread_num=4)

for i in range(0,4000):
    eng.next_step()
