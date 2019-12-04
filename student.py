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
        detonator = False
        check_balloom_doll = False
        spawn = list(mapa.bomberman_spawn)
        count_best = 1
        count_c = 0


        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )

                walls = set_walls(state['walls'])
                powerups = state['powerups']
                bomberman = state['bomberman']
                bomb = state['bombs']
                game_walls = Paredes(domain(state['bomberman'],walls,mapa,enemies_all(state['enemies'])))
                enemie_more_close = find_close_wall(state['bomberman'], enemies_all(state['enemies']))
                check_balloom_doll = find_balloom_doll(state['enemies'])
                count_c = count_close(enemie_more_close, bomberman, count_c)

                #Is there Bomb on the Map?
                if(bomb != []):
                    #Are you in a savety place?
                    if not verify_range_bomb(state['bomberman'],state['bombs'][0][0],state['bombs'][0][2],mapa,walls):
                        if run_check == False:
                            run_check = True
                            w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], mapa, walls, danger_zones)
                            p = SearchProblem(game_walls, state['bomberman'],w)
                            t = SearchTree(p,'greedy')
                            wlk_path = convert_to_path(t.search(50))
                            if wlk_path==[]:
                                key = random_valid_key()
                                if detonator == True:
                                    key = random_valid_key()
                                    run_check = False
                                else:
                                    p = SearchProblem(game_walls,bomberman,spawn)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(200))
                                    run_check = False
                            
                    #Not
                    else:   #Press Detonator
                        key="A"

                #Not
                else:
                    #Is the enemies near from me? (escape from enemie while there are Walls in map)
                    if math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 1.8 and check_balloom_doll==True:
                        w = bomb_fled(state['bomberman'], enemie_more_close, 3, mapa, walls, danger_zones)
                        p = SearchProblem(game_walls, state['bomberman'],w)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(50))
                        if bomberman == [3,28] or bomberman == [5,28]:
                            wlk_path = ['B'] 

                    #Is there item on the Map
                    if state['powerups']!=[]:
                        target_wall = state["powerups"][0][0]
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(50))
                        if state['level']==3:
                            detonator = True
                    #Not
                    else:
                        #Are there enemies alive? (atack enemies if there isn't walls in map)
                        if state['enemies']!=[] and state['walls']==[]:
                            if math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 1.8:
                                wlk_path=["B"]

                            elif check_balloom_doll==False:
                                target_wall = enemie_more_close
                                p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                t = SearchTree(p,'greedy')
                                wlk_path = convert_to_path_wall(t.search(200))
                            
                            elif not state['bomberman']==spawn: #Go to spawn to do tatic
                                if run_check == False:    
                                    p = SearchProblem(game_walls, state['bomberman'], spawn)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(500))
                                    run_check = True
                            
                            elif math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 2:
                                wlk_path=["B"]

                                if run_check == False and bomb!=[]:
                                    w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], mapa, walls, danger_zones)
                                    p = SearchProblem(game_walls, state['bomberman'],w)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(50))
                                    wlk_path.insert(0,"B")
                                    run_check = True

                        #Not
                        else:
                            #Is the exit avaliable?
                            if state['exit']!= [] and state['enemies']==[]: #Go to the exit
                                target_wall = state['exit']
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
                                        x = t.search(200)
                                        if x == None:   #If the Bomberman are undicided in 2 paths
                                            key = random_valid_key()
                                            run_check = False
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

                save_pos.insert(0,bomberman) #Save the last positions of Bomberman
                if len(save_pos) > 100:       
                    save_pos = save_pos[:-1]
                if pos_last(save_pos, bomberman) == True and bomberman!=spawn:  #If are always in the same position, try move to the spawn
                    if count_best%2==0:   #If the Bomberman are undicided in 2 paths
                        count_best+=1
                        key = "A"
                    else:
                        count_best+=1   #Try move sometimes with key random
                        key = random_valid_key()
                if count_c > 50:   #If bomberman are in a infinity loop
                    key = random_valid_key() 
                    print("LOOP, so random")

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def valid_pos(pos, mapa, walls):
    x = pos[0]
    y = pos[1]
    if mapa.is_stone((x,y)):
        return False
    for i in walls:
        if pos == i:
            return False
    return True

def near_wall(bomberman, wall):
    if math.hypot(wall[0]-bomberman[0],wall[1]-bomberman[1]) == 1:
        return True
    return False

def bomb_fled(bomberman, bomba, radius, mapa, walls, danger_zones, a=3):
    b = a
    for x in range(a):
        for y in range(b):
            if verify_range_bomb([bomba[0]-x,bomba[1]-y], bomba, radius, mapa, walls) and ([bomba[0]-x,bomba[1]-y] not in danger_zones):
                return [bomba[0]-x,bomba[1]-y]
            if verify_range_bomb([bomba[0]-x,bomba[1]+y], bomba, radius, mapa, walls) and ([bomba[0]-x,bomba[1]+y] not in danger_zones):
                return [bomba[0]-x,bomba[1]+y]
            if verify_range_bomb([bomba[0]+x,bomba[1]-y], bomba, radius, mapa, walls) and ([bomba[0]+x,bomba[1]-y] not in danger_zones):
                return [bomba[0]+x,bomba[1]-y]
            if verify_range_bomb([bomba[0]+x,bomba[1]+y], bomba, radius, mapa, walls) and ([bomba[0]+x,bomba[1]+y] not in danger_zones):
                return [bomba[0]+x,bomba[1]+y]
            if verify_range_bomb([bomba[0],bomba[1]-y], bomba, radius, mapa, walls) and ([bomba[0],bomba[1]-y] not in danger_zones):
                return [bomba[0],bomba[1]-y]
            if verify_range_bomb([bomba[0]-x,bomba[1]], bomba, radius, mapa, walls) and ([bomba[0]-x,bomba[1]] not in danger_zones):
                return [bomba[0]-x,bomba[1]]
            if verify_range_bomb([bomba[0]+x,bomba[1]], bomba, radius, mapa, walls) and ([bomba[0]+x,bomba[1]] not in danger_zones):
                return [bomba[0]+x,bomba[1]]
            if verify_range_bomb([bomba[0],bomba[1]+y], bomba, radius, mapa, walls) and ([bomba[0],bomba[1]+y] not in danger_zones):
                return [bomba[0],bomba[1]+y]
    bomb_fled(bomberman,bomba,radius,mapa,walls,b+1)

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

def verify_range_bomb(bomberman, bomb, radius, mapa, walls):
    x_bomberman = bomberman[0]
    y_bomberman = bomberman[1]
    x_bomb = bomb[0]
    y_bomb = bomb[1]
    
    if (x_bomberman >= x_bomb and y_bomberman == y_bomb) and (abs(x_bomberman)-abs(x_bomb) <= radius):
        return False
    elif (x_bomberman <= x_bomb and y_bomberman == y_bomb) and (abs(x_bomberman)-abs(x_bomb) <= radius):
        return False
    elif (x_bomberman == x_bomb and y_bomberman >= y_bomb) and (abs(y_bomberman)-abs(y_bomb) <= radius):
        return False
    elif (x_bomberman == x_bomb and y_bomberman <= y_bomb) and (abs(y_bomberman)-abs(y_bomb) <= radius):
        return False
    elif not valid_pos(bomberman, mapa, walls):
        return False
    return True

def domain(bomberman, walls, mapa, enemie_list):
    y = mapa.size[1]
    x = mapa.size[0]
    lista = []
    i = 0
    while i <= x:
        j = 0
        while j <= y:
            if valid_pos([i,j],mapa,walls) and [i,j] not in enemie_list:
                if valid_pos([i+1,j],mapa,walls) and [i+1,j] not in enemie_list:
                    lista += [([i,j],[i+1,j],1)]
                if valid_pos([i-1,j],mapa,walls) and [i-1,j] not in enemie_list:
                    lista += [([i,j],[i-1,j],1)]
                if valid_pos([i,j+1],mapa,walls) and [i,j+1] not in enemie_list:
                    lista += [([i,j],[i,j+1],1)]
                if valid_pos([i,j-1],mapa,walls) and [i,j-1] not in enemie_list:
                    lista += [([i,j],[i,j-1],1)]
            j += 1
        i += 1
    return lista

def set_walls(wall):
    walls = []
    for i in wall:
        walls += [i]
    return walls

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
            return True
    return False

def count_close(enemie_more_close, pos, count_c):
    if math.hypot(enemie_more_close[0]-pos[0],enemie_more_close[1]-pos[1]) <= 4:
        return count_c + 1   
    else:
        return 0

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))