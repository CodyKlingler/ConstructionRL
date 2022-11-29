import cityflow

# load simulation

sim_ny = 'data/NewYork/16_3/config.json'
sim_nyc = 'data/manhattan/config.json'

test_jinan = "jinan_normalized/config.json"

eng = cityflow.Engine(test_jinan, thread_num=4)

n_steps = 40000
for i in range(0,n_steps):
    if i% (n_steps // 100) == 0:
        print(f"\r{round((i/n_steps)*100,1)}%", end='')
    eng.next_step()
print()