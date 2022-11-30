import cityflow
import json
import heapq

# load simulation

sim_ny = 'data/NewYork/16_3/config.json'
sim_nyc = 'data/manhattan/config.json'

test_jinan = "jinan_normalized/config.json"

roadnet_file_loc = "jinan_normalized/roadnet_3_4.json"
roadnet_file = open(roadnet_file_loc, "r")
roadnet = json.loads(roadnet_file.read())

def get_2d_dist(p1, p2):
    return (p1 * p1 + p2 * p2)**(0.5)

def get_road_min_time(road):
    total_time = 0
    for i in range(1, len(road["points"])):
        total_time += get_2d_dist(road["points"][i]["x"], road["points"][i]["y"]) / r["lanes"][0]["maxSpeed"]
    return total_time

# build graph 
intersections = {}
for i in roadnet["intersections"]:
    roads_from = []
    for r in roadnet["roads"]:
        if r["startIntersection"] == i["id"]:
            roads_from.append(r)
    roads_from.sort(key=get_road_min_time)
    intersections[i["id"]] = roads_from
    # print(f"\n{i['id']}")
    # print([x["startIntersection"] for x in roads_from])


def find_fastest_path_helper(intersections_map, ending_intersection, blocked_routes, distance_dict, from_dict, next_queue):
    next = next_queue.pop(0)
    while next["endIntersection"] in distance_dict or next["id"] in blocked_routes:
        if len(next_queue) == 0:
            return []
        next = next_queue.pop(0)

    # print(f"\nStartIntersection: {next['startIntersection']}")
    # print(f"EndIntersection: {next['endIntersection']}")

    from_dict[next["endIntersection"]] = next
    distance_dict[next["endIntersection"]] = distance_dict[next["startIntersection"]] + get_road_min_time(next)

    if next["endIntersection"] == ending_intersection:
        prev_path = next
        new_car_path = []
        while prev_path != None:
            new_car_path.insert(0, prev_path["id"])
            prev_path = from_dict[prev_path["startIntersection"]]
        return new_car_path

    for road in intersections_map[next["endIntersection"]]:
        next_queue.append(road)
    next_queue.sort(key=get_road_min_time)

    return find_fastest_path_helper(intersections_map, ending_intersection, blocked_routes, distance_dict, from_dict, next_queue)
        

def find_fastest_path(intersections_map, starting_intersection, ending_road, blocked_routes):
    distance_dict = {}
    from_dict = {}
    distance_dict[starting_intersection] = 0
    from_dict[starting_intersection] = None

    # print(f"Searching again! {starting_intersection}")

    # next_queue = intersections_map[starting_intersection]
    next_queue = []
    next_queue.extend(intersections_map[starting_intersection])
    # print([x["startIntersection"] for x in next_queue])

    return find_fastest_path_helper(intersections_map, ending_road["endIntersection"], blocked_routes, distance_dict, from_dict, next_queue)


eng = cityflow.Engine(test_jinan, thread_num=4)

n_steps = 4000
rerouted_vehicles = 0
failed_rerouted_vehicles = 0
blocked_routes = ["road_1_2_1", "road_2_2_1", "road_4_2_1", "road_1_3_3", "road_2_3_3", "road_4_3_3"]
dict_success = {}
for i in range(0,n_steps):
    if i% (n_steps // 100) == 0:
        print(f"\r{round((i/n_steps)*100,1)}%", end='')
    eng.next_step()

    vehicles = eng.get_vehicles()
    for v_id in vehicles:
        if v_id not in dict_success:
            vehicle = eng.get_vehicle_info(v_id)
            route = vehicle["route"].strip().split(" ")
            if any(r in blocked_routes for r in route):
                print(f"\nVehicle {v_id}: {vehicle}")
                # next_intersection = [x for x in roadnet["roads"] if x["id"] == route[0]][0]["startIntersection"] # probably
                # next_intersection = [x for x in roadnet["roads"] if x["id"] == route[1]][0]["startIntersection"] # maybe
                next_intersection = [x for x in roadnet["roads"] if x["id"] == route[2]][0]["startIntersection"]
                last_road = [x for x in roadnet["roads"] if x["id"] == route[-1]][0]

                # proposed_route = find_fastest_path(intersections, next_intersection, last_road, blocked_routes)[1:] # probably
                # proposed_route = find_fastest_path(intersections, next_intersection, last_road, blocked_routes) # maybe
                proposed_route = find_fastest_path(intersections, next_intersection, last_road, blocked_routes)
                proposed_route.insert(0, route[1]) # probably shouldnt need to be here
                success = eng.set_vehicle_route(v_id, proposed_route)
                if success:
                    rerouted_vehicles += 1
                    dict_success[v_id] = True
                    print(f"\nSuccess: \n{vehicle['drivable']} \n{vehicle['route']} \n{proposed_route}")
                else:
                    print(f"\nFailure: \n{vehicle['drivable']} \n{vehicle['route']} \n{proposed_route}")
                    failed_rerouted_vehicles += 1
                    dict_success[v_id] = False
                # rewrite route to run breadth first search from a to c excluding b
print()
print(f"Rerouted vehicles: {rerouted_vehicles}")
print(f"Failed rerouted vehicles: {failed_rerouted_vehicles}")