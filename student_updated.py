import sys
import json
import asyncio
import websockets
import getpass
import os
import math

from mapa import Map
from tree_search_bomb import *
from paredes import Paredes
from characters import *
from game import *
import time
import random



async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)

        # You can create your own map representation or use the game representation:
        mapa = Map(size=game_properties["size"], mapa=game_properties["map"])


        walls = []
        bomberman = []
        powerups = []
        target_wall = []
        wlk_path = []
        danger_zones = []
        enemie_more_close  = []
        save_pos = []
        game_walls = None
        run_check = False
        check_balloom_doll = False
        size_map = mapa.size
        spawn = list(mapa.bomberman_spawn)


        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )

                walls = set_walls(state['walls'])
                powerups = state['powerups']
                bomberman = state['bomberman']
                bomb = state['bombs']
                game_walls = Paredes(domain(state['bomberman'],walls,size_map,enemies_all(state['enemies'])),size_map)
                enemie_more_close = find_close_wall(state['bomberman'], enemies_all(state['enemies']))
                check_balloom_doll = find_balloom_doll(state['enemies'])
                danger_zones = set_danger_zones(state['enemies'])

                print("lives: ", state['lives'])

                #Is there Bomb on the Map?
                if(bomb != []):
                    #Are you in a savety place?
                    if not verify_range_bomb(state['bomberman'],state['bombs'][0][0],state['bombs'][0][2],size_map,walls, enemie_more_close):
                        if run_check == False:
                            run_check = True
                            print("\nBomb are panted: ", state['bombs'][0][0])
                            w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls, danger_zones, enemie_more_close)
                            p = SearchProblem(game_walls, state['bomberman'],w)
                            t = SearchTree(p,'greedy')
                            wlk_path = convert_to_path(t.search(100))
                            print("Go from: ",bomberman," to: ",w)
                            if wlk_path==[]:
                                key = random_valid_key()
                                print("kkkey: ", key)
                                # print("Error: the wlk_path is empty, try move to Spawn")
                                # p = SearchProblem(game_walls, state['bomberman'],spawn)
                                # t = SearchTree(p,'greedy')
                                # wlk_path = convert_to_path(t.search(1000)) #experimentar com 10000
                            
                    #Not
                    else:
                        key="A"
                        print("I'm save!")

                #Not
                else:
                    #Is the enemies near from me? (escape from enemie while there are Walls in map)      #1.9?
                    if math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 1.8 and check_balloom_doll==True:
                        print("Escape ENEMIE")
                        w = bomb_fled(state['bomberman'], enemie_more_close, 3, size_map, walls, danger_zones, enemie_more_close)
                        p = SearchProblem(game_walls, state['bomberman'],w)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        if bomberman == [3,28]: # Falta testar estas 2 linhas
                            wlk_path = ['B']    # Falta testar estas 2 linhas

                    #Is there item on the Map
                    if state['powerups']!=[]:
                        print("Catch POWERUP")
                        target_wall = state["powerups"][0][0]
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                    #Not
                    else:
                        #Are there enemies alive? (atack enemies if there isn't walls in map)
                        if state['enemies']!=[] and state['walls']==[]:
                            if check_balloom_doll==False:
                                target_wall = enemie_more_close
                                print("Catch ENEMIE")
                                p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                t = SearchTree(p,'greedy')
                                wlk_path = convert_to_path_wall(t.search(500))
                            
                            elif not state['bomberman']==spawn: #Go to spawn to do tatic
                                if run_check == False:    
                                    p = SearchProblem(game_walls, state['bomberman'], spawn)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    run_check = True
                            
                            elif math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 2:
                                wlk_path=["B"]

                                if run_check == False and bomb!=[]:
                                    w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls, danger_zones, enemie_more_close)
                                    p = SearchProblem(game_walls, state['bomberman'],w)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    wlk_path.insert(0,"B")
                                    run_check = True

                        #Not
                        else:
                            #Is the exit avaliable?
                            if state['exit']!= [] and state['enemies']==[]: #Go to the exit
                                target_wall = state['exit']
                                print("-----------Target EXIT-----------")
                                p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                t = SearchTree(p,'greedy')
                                wlk_path = convert_to_path(t.search(100))

                            #Not - (Atack Walls)
                            else:
                                target_wall = find_close_wall(state['bomberman'],walls)
                                if not near_wall(state['bomberman'],target_wall):
                                    if run_check== False:
                                        run_check = True
                                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                        t = SearchTree(p,'greedy')
                                        x = t.search(100)
                                        if x == None:   #If the Bomberman are undicided in 2 paths
                                            print("Error: Don't know the best path: so try move random!")
                                            key = random_valid_key()
                                        else:
                                            wlk_path = convert_to_path_wall(x)

                #Read DATAPATH
                if (wlk_path == ['A'] or wlk_path == []):
                    run_check = False
                    if(near_wall(state['bomberman'],target_wall)) and bomb == []:
                        key = "B"
                elif wlk_path != []:
                    key = wlk_path[0]
                    wlk_path = wlk_path[1:]

                # save_pos.insert(0,bomberman) #Save the last positions of Bomberman
                if len(save_pos) > 100:       
                    save_pos = save_pos[:-1]
                if pos_last(save_pos, bomberman) == True and bomberman!=spawn:  #If are always in the same position, try move to the spawn
                    # p = SearchProblem(game_walls, state['bomberman'],spawn)
                    # t = SearchTree(p,'greedy')
                    # wlk_path = convert_to_path(t.search(5000)) #Experimentar com 3000
                    print("Error: Try move to the Spawn") #Em vez disto tentar mandar Key Random
                    #key = random_valid_key()
                    key = "A"
                    print("yekey: ", key)
                    print("wwpath ignored: ", wlk_path)

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def valid_pos(pos, size_map, walls):
    if pos[0] % 2 == 0 and pos[1] % 2 == 0:
        return False
    for i in walls:
        if pos == i:
            return False
    if pos[0] <= 0 or pos[0] >= size_map[0] or pos[1] <= 0 or pos[1] >= size_map[1]:
        return False
    return True

def near_wall(bomberman, wall):
    if math.hypot(wall[0]-bomberman[0],wall[1]-bomberman[1]) == 1:
        return True
    return False

def near(bomberman, wall):
    if math.hypot(wall[0]-bomberman[0],wall[1]-bomberman[1]) <= 2:
        return True
    return False

def bomb_fled(bomberman, bomba, radius, size_map, walls, danger_zones, enemie_more_close, a=3):
    b = a
    for x in range(a):
        for y in range(b):
            if verify_range_bomb([bomba[0]-x,bomba[1]-y], bomba, radius, size_map, walls, enemie_more_close) and ([bomba[0]-x,bomba[1]-y] not in danger_zones):
                print("valid scape pos: ", [bomba[0]-x,bomba[1]-y])
                return [bomba[0]-x,bomba[1]-y]
            if verify_range_bomb([bomba[0]-x,bomba[1]+y], bomba, radius, size_map, walls, enemie_more_close) and ([bomba[0]-x,bomba[1]+y] not in danger_zones):
                print("valid scape pos: ", [bomba[0]-x,bomba[1]+y])
                return [bomba[0]-x,bomba[1]+y]
            if verify_range_bomb([bomba[0]+x,bomba[1]-y], bomba, radius, size_map, walls, enemie_more_close) and ([bomba[0]+x,bomba[1]-y] not in danger_zones):
                print("valid scape pos: ", [bomba[0]+x,bomba[1]-y])
                return [bomba[0]+x,bomba[1]-y]
            if verify_range_bomb([bomba[0]+x,bomba[1]+y], bomba, radius, size_map, walls, enemie_more_close) and ([bomba[0]+x,bomba[1]+y] not in danger_zones):
                print("valid scape pos: ", [bomba[0]+x,bomba[1]+y])
                return [bomba[0]+x,bomba[1]+y]
            if verify_range_bomb([bomba[0],bomba[1]-y], bomba, radius, size_map, walls, enemie_more_close) and ([bomba[0],bomba[1]-y] not in danger_zones):
                print("valid scape pos: ", [bomba[0],bomba[1]-y])
                return [bomba[0],bomba[1]-y]
            if verify_range_bomb([bomba[0]-x,bomba[1]], bomba, radius, size_map, walls, enemie_more_close) and ([bomba[0]-x,bomba[1]] not in danger_zones):
                print("valid scape pos: ", [bomba[0]-x,bomba[1]])
                return [bomba[0]-x,bomba[1]]
            if verify_range_bomb([bomba[0]+x,bomba[1]], bomba, radius, size_map, walls, enemie_more_close) and ([bomba[0]+x,bomba[1]] not in danger_zones):
                print("valid scape pos: ", [bomba[0]+x,bomba[1]])
                return [bomba[0]+x,bomba[1]]
            if verify_range_bomb([bomba[0],bomba[1]+y], bomba, radius, size_map, walls, enemie_more_close) and ([bomba[0],bomba[1]+y] not in danger_zones):
                print("valid scape pos: ", [bomba[0],bomba[1]+y])
                return [bomba[0],bomba[1]+y]
    bomb_fled(bomberman,bomba,radius,size_map,walls,b+1)

def find_close_wall(bomberman, walls):
    aux = 100000
    if walls == []:
        return [2,3]
    for i in walls:
        dist = math.hypot(bomberman[0] - i[0], bomberman[1] - i[1])
        if dist < aux:
            aux = dist
            x = i
    return x

def convert_to_path(p):
    if p == None:
        return []
    if len(p) == 1:
        return ["A"]
    if p[0][0] - p[1][0] == 1:
        return ["a"] + convert_to_path(p[1:])
    elif p[0][0] - p[1][0] == -1:
        return ["d"] + convert_to_path(p[1:])
    if p[0][1] - p[1][1] == 1:
        return ["w"] + convert_to_path(p[1:])
    elif p[0][1] - p[1][1] == -1:
        return ["s"] + convert_to_path(p[1:])

def convert_to_path_wall(p):
    if p == None:
        return []
    if len(p) == 2:
        return ["A"]
    if p[0][0] - p[1][0] == 1:
        return ["a"] + convert_to_path_wall(p[1:])
    elif p[0][0] - p[1][0] == -1:
        return ["d"] + convert_to_path_wall(p[1:])
    if p[0][1] - p[1][1] == 1:
        return ["w"] + convert_to_path_wall(p[1:])
    elif p[0][1] - p[1][1] == -1:
        return ["s"] + convert_to_path_wall(p[1:])

def verify_range_bomb(bomberman, bomb, radius, size_map, walls, enemie_more_close):
    area = [bomb]
    close = math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1])
    x = 1
    print(bomb)
    while x <= radius:
        area += [[bomb[0]+x, bomb[1]]]
        area += [[bomb[0]-x, bomb[1]]]
        area += [[bomb[0], bomb[1]+x]]
        area += [[bomb[0], bomb[1]-x]]
        x += 1
    if not valid_pos(bomberman,size_map,walls) or bomberman in area or close < 1.5:
        return False
    if not valid_pos(bomberman,size_map,walls) or bomberman in area:
        return False
    return True

def verify_range_bomb2(bomberman, bomb, radius, size_map, walls):
    x_bomberman = bomberman[0]
    y_bomberman = bomberman[1]
    x_bomb = bomb[0]
    y_bomb = bomb[1]
    
    if not valid_pos(bomberman, size_map, walls):
        return False
    if ((x_bomberman <= x_bomb + radius and x_bomberman >= x_bomb - radius) and y_bomberman == y_bomb) and (abs(x_bomberman)-abs(x_bomb) <= radius):
        return False
    elif (x_bomberman == x_bomb and (y_bomberman >= y_bomb - radius and y_bomberman <= y_bomb + radius)) and (abs(y_bomberman)-abs(y_bomb) <= radius):
        return False
    return True

def domain(bomberman, walls, size_map, enemie_list):
    y = size_map[1]
    x = size_map[0]
    lista = []
    i = 1
    while i < x:
        j = 1
        while j < y:
            if valid_pos([i,j],size_map,walls) and [i,j] not in enemie_list:
                if valid_pos([i+1,j],size_map,walls) and [i+1,j] not in enemie_list:
                    lista += [([i,j],[i+1,j],1)]
                if valid_pos([i-1,j],size_map,walls) and [i-1,j] not in enemie_list:
                    lista += [([i,j],[i-1,j],1)]
                if valid_pos([i,j+1],size_map,walls) and [i,j+1] not in enemie_list:
                    lista += [([i,j],[i,j+1],1)]
                if valid_pos([i,j-1],size_map,walls) and [i,j-1] not in enemie_list:
                    lista += [([i,j],[i,j-1],1)]
            j += 1
        i += 1
    return lista

def set_walls(wall):
    walls = []
    for i in wall:
        walls += [i]
    return walls
    
def set_danger_zones(enemies):
    danger_zones = []
    i = 0
    while i < len(enemies):
        danger_zones += [enemies[i]['pos'],
        [enemies[i]['pos'][0]+1,enemies[i]['pos'][1]+0],
        [enemies[i]['pos'][0]-1,enemies[i]['pos'][1]+0],
        [enemies[i]['pos'][0]-1,enemies[i]['pos'][1]+1],
        [enemies[i]['pos'][0]+0,enemies[i]['pos'][1]+1],
        [enemies[i]['pos'][0]+1,enemies[i]['pos'][1]+1],
        [enemies[i]['pos'][0]-1,enemies[i]['pos'][1]-1],
        [enemies[i]['pos'][0]+0,enemies[i]['pos'][1]-1],
        [enemies[i]['pos'][0]+1,enemies[i]['pos'][1]-1]]
        i += 1
    return danger_zones

def enemies_all(enemies):
    arr = []
    for i in enemies:
        arr += [i['pos']]
    return arr

def find_balloom_doll(enemies):
    for e in enemies:
        if e['name'] == "Balloom" or e['name'] == "Doll":
            return True
    return False

def random_valid_key():
    aux = ["w", "d", "s", "a"]
    val = random.randint(0,3)
    return aux[val]

def pos_last(save_pos, pos):
    c = 0
    c2 = 0
    for p in save_pos:
        c+=1
        if p == pos:
            c2+=1
        if c==95 and c2 <=92:
            return False
        elif c==95 and c2 >=92:
            print("Hora de rebentar com a bomba!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return True
    return False


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
