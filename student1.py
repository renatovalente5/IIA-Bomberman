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

# Next 2 lines are not needed for AI agent
import pygame

pygame.init()





async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)

        # You can create your own map representation or use the game representation:
        mapa = Map(size=game_properties["size"], mapa=game_properties["map"])

        walls = []
        target_wall = []
        target_enemie = []
        wlk_path = []
        danger = []
        bomb_danger_zone = []
        powerups = []
        bomberman = []
        game_walls = None
        size_map = mapa.size
        on_wall = None
        pos_enemie = []
        arrive = False
        exit_dor = False
        last_steps = []
        bug_steps = []
        run_check = False
        power_up = False
        

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server

                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                print("\n")
                #print(state)
                #print(state['enemies']['pos'])
                try:
                    bomberman = state['bomberman']
                except:
                    print("--+--+-+-+-+-+-+-+-+-+-+-+-+-+-+-+--+--ERROR BOMBERMAN")
                    pass
                try:
                    walls = set_walls(state['walls'])
                    powerups = state['powerups']
                    # last_steps.append(bomberman)
                    # bug_steps = verify_last_steps(last_steps)
                except:
                    print("--+--+-+-+-+-+-+-+-+-+-+-+-+-+-+-+--+--ERROR WALLS")
                    pass
                print(state['enemies'])
                danger = set_danger_zones(state['enemies'])
                game_walls = Paredes(domain(state['bomberman'],walls,size_map,danger),size_map)
                enemie_more_close = find_close_wall(state['bomberman'], enemies_all(state['enemies']))
                check_balloom = find_balloom(state['enemies'])
                pos_blue = find_enemie_blue(bomberman, state['enemies'])

                if state['powerups'] != []:
                    print("apanhar POWERUP")
                    if power_up==False:
                        p = SearchProblem(game_walls, state['bomberman'], state['powerups'][0][0])
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        print("caminho definido")
                        print("power up: ",wlk_path)
                        power_up=True
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]
                elif state['exit'] != [] and state['enemies'] == []: #ir para a saída
                    target_wall = state['exit']
                    print("exit go")
                    if exit_dor == False:
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        print("caminho definido")
                        print("saida: ",wlk_path)
                        exit_dor = True
                        power_up =False
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]
                else:
                    if state['walls'] != []:#    and state['exit'] == []:
                        print("destruir parede ")
                        target_wall = find_close_wall(state['bomberman'],walls) #acrescentar
                        if state['bombs'] == [] and walls != []:
                            if not near_wall(state['bomberman'],target_wall): #atacar paredes
                                if run_check == False:
                                    print("target wall: ", target_wall)
                                    p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path_wall(t.search(100))
                                    print("caminho definido")
                                    run_check = True
                            if (wlk_path == [''] or wlk_path == []):#and near_wall(bomberman, find_close_wall(bomberman, walls)):# and x==None:
                                on_wall = True
                                run_check = False
                                if(near_wall(state['bomberman'],target_wall)):
                                    key = "B"
                            elif wlk_path != []:
                                key = wlk_path[0]
                                wlk_path = wlk_path[1:]
                        elif state['bombs'] != []:
                            print("fugir da bomba")
                            if not verify_range_bomb(state['bomberman'],state['bombs'][0][0],state['bombs'][0][2],size_map,walls):
                                if run_check == False:
                                    w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls)
                                    p = SearchProblem(game_walls, state['bomberman'],w)
                                    t = SearchTree(p,'a*')
                                    wlk_path = convert_to_path(t.search(100))
                                    print("caminho definido")
                                    print("go from: ",bomberman," to: ",w)
                                    run_check = True
                            if len(wlk_path) == 1:
                                key = wlk_path[0]
                                wlk_path = []
                                run_check = False
                            elif wlk_path != []:
                                key = wlk_path[0]
                                wlk_path = wlk_path[1:]
                            target_wall = [1,1]
                    else:
                        print("matar balloons")
                        if arrive == False:     #ir até à partida
                            target_wall = [1,1]
                            if not state['bomberman']==target_wall: #atacar paredes
                                if run_check == False:    
                                    print("not bomb")
                                    print("target wall: ", target_wall)
                                    p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    print("caminho definido")
                                    run_check = True
                            if (wlk_path == [''] or wlk_path == []) and math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 2:
                                print("cheguei [1,1]")
                                arrive = True
                                run_check = False
                                key = "B"
                            elif wlk_path != []:
                                key = wlk_path[0]
                                wlk_path = wlk_path[1:]
                        else:
                            target_wall = [2,3]     #esconder-se da bomba na partida
                            if not state['bomberman']==target_wall: #atacar paredes
                                if run_check == False:    
                                    print("not bomb")
                                    print("target wall: ", target_wall)
                                    p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    run_check =  True
                            if ((wlk_path == [''] or wlk_path == []) and state['bombs']==[]):#and near_wall(bomberman, find_close_wall(bomberman, walls)):# and x==None:
                                print("cheguei [3,3]")
                                arrive = False
                                run_check = False
                                #key = "B"
                            elif wlk_path != []:
                                key = wlk_path[0]
                                wlk_path = wlk_path[1:]
                    if math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 1 and state['enemies']!=[]:
                        print("Fugir do inimigo")
                        w = bomb_fled(state['bomberman'], enemie_more_close, 1, size_map, walls)
                        p = SearchProblem(game_walls, state['bomberman'],w)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(10))
                        print("go from: ",bomberman," to: ",w)
                        if len(wlk_path) == 1:
                            key = wlk_path[0]
                            wlk_path = []
                            #run_check = False
                        elif wlk_path != []:
                            key = wlk_path[0]
                            wlk_path = wlk_path[1:]
                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def find_enemie_blue(pos, enemies):
    for enemie in enemies:
        if enemie['name'] == "Oneal":    #falta garantir que é só para os blue
            return enemie['pos']
    return []

def find_balloom(enemies):
    for e in enemies:
        print(e['name'])
        if e['name'] == "Balloom":
            return True
    return False


def valid_pos(pos, size_map, walls):
    if pos[0] % 2 == 0 and pos[1] % 2 == 0:
        return False
    for i in walls:
        if pos == i:
            return False
    if pos[0] <= 0 or pos[0] >= size_map[0] or pos[1] <= 0 or pos[1] >= size_map[1]:
        return False
    return True

def valid_moove(pos, mov, size_map, walls):
    if pos[0] == 1 and mov == "a":
        return False
    if pos[1] == 1 and mov == "w":
        return False
    if pos[0] == size_map[0]-1 and mov == "d":
        return False
    if pos[1] == size_map[1]-1 and mov == "s":
        return False
    if pos[0] % 2 == 0 and (mov == "s" or mov == "w"):
        return False
    if pos[1] % 2 == 0 and (mov == "d" or mov == "a"):
        return False
    for i in walls:
        if mov == "w" and [pos[0],pos[1]-1] == i:
            return False
        if mov == "a" and [pos[0]-1,pos[1]] == i:
            return False
        if mov == "s" and [pos[0],pos[1]+1] == i:
            return False
        if mov == "d" and [pos[0]+1,pos[1]] == i:
            return False
    return True

def near_wall(bomberman, wall):
    if math.hypot(wall[0]-bomberman[0],wall[1]-bomberman[1]) == 1:
        return True
    return False

def bomb_fled(bomberman, bomba, radius, size_map, walls, a=3):
    b = a
    print(bomba)
    for x in range(a):
        for y in range(b):
            if verify_range_bomb([bomba[0]-x,bomba[1]], bomba, radius, size_map, walls):
                return [bomba[0]-x,bomba[1]]
            if verify_range_bomb([bomba[0]+x,bomba[1]], bomba, radius, size_map, walls):
                return [bomba[0]+x,bomba[1]]
            if verify_range_bomb([bomba[0],bomba[1]+y], bomba, radius, size_map, walls):
                return [bomba[0],bomba[1]+y]
            if verify_range_bomb([bomba[0],bomba[1]-y], bomba, radius, size_map, walls):
                return [bomba[0],bomba[1]-y]
            if verify_range_bomb([bomba[0]-x,bomba[1]-y], bomba, radius, size_map, walls):
                return [bomba[0]-x,bomba[1]-y]
            if verify_range_bomb([bomba[0]+x,bomba[1]+y], bomba, radius, size_map, walls):
                return [bomba[0]+x,bomba[1]+y]
    bomb_fled(bomberman,bomba,radius,size_map,walls,b+1)

def bomb_safe(bomberman, bomb_danger_zone):
    for i in bomb_danger_zone:
        if bomberman == i:
            return False
    return True

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
        return [""]
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
        return [""]
    if p[0][0] - p[1][0] == 1:
        return ["a"] + convert_to_path_wall(p[1:])
    elif p[0][0] - p[1][0] == -1:
        return ["d"] + convert_to_path_wall(p[1:])
    if p[0][1] - p[1][1] == 1:
        return ["w"] + convert_to_path_wall(p[1:])
    elif p[0][1] - p[1][1] == -1:
        return ["s"] + convert_to_path_wall(p[1:])

def verify_range_bomb(bomberman, bomb, radius, size_map, walls):
    x_bomberman = bomberman[0]
    y_bomberman = bomberman[1]
    x_bomb = bomb[0]
    y_bomb = bomb[1]
    
    if (x_bomberman >= x_bomb - radius and y_bomberman == y_bomb) and (abs(x_bomberman)-abs(x_bomb) <= radius):
        return False
    elif (x_bomberman <= x_bomb + radius and y_bomberman == y_bomb) and (abs(x_bomberman)-abs(x_bomb) <= radius):
        return False
    elif (x_bomberman == x_bomb and y_bomberman >= y_bomb - radius) and (abs(y_bomberman)-abs(y_bomb) <= radius):
        return False
    elif (x_bomberman == x_bomb and y_bomberman <= y_bomb + radius) and (abs(y_bomberman)-abs(y_bomb) <= radius):
        return False
    elif not valid_pos(bomberman, size_map, walls):
        return False
    print(True)
    return True

def domain(bomberman, walls, size_map, enemie_list):
    print("domain: ",enemie_list)
    y = size_map[1]
    x = size_map[0]
    lista = []
    i = 1
    while i < x:
        j = 1
        while j < y:
            if valid_pos([i,j],size_map,walls) and [i,j] not in enemie_list:
                if valid_pos([i+1,j],size_map,walls):
                    lista += [([i,j],[i+1,j],1)]
                if valid_pos([i-1,j],size_map,walls):
                    lista += [([i,j],[i-1,j],1)]
                if valid_pos([i,j+1],size_map,walls):
                    lista += [([i,j],[i,j+1],1)]
                if valid_pos([i,j-1],size_map,walls):
                    lista += [([i,j],[i,j-1],1)]
            j += 1
        i += 1
    return lista

def try_area(bomberman, quadrante, walls, size_map):
    i = 6
    j = 6
    if quadrante == 1:
        while i > 0:
            while j > 0:
                if(valid_pos([bomberman[0]-i,bomberman[1]-j],size_map,walls)):
                    return [bomberman[0]-i,bomberman[1]-j]
                j -= 1
            i -=1
    elif quadrante == 2:
        while i > 0:
            while j > 0:
                if(valid_pos([bomberman[0]+i,bomberman[1]-j],size_map,walls)):
                    return [bomberman[0]+i,bomberman[1]-j]
                j -= 1
            i -=1
    elif quadrante == 3:
        while i > 0:
            while j > 0:
                if(valid_pos([bomberman[0]+i,bomberman[1]+j],size_map,walls)):
                    return [bomberman[0]+i,bomberman[1]+j]
                j -= 1
            i -=1
    elif quadrante == 4:
        while i > 0:
            while j > 0:
                if(valid_pos([bomberman[0]-i,bomberman[1]+j],size_map,walls)):
                    return [bomberman[0]-i,bomberman[1]+j]
                j -= 1
            i -=1
    elif quadrante == 5:
        while i > 0:
            if(valid_pos([bomberman[0],bomberman[1]-i],size_map,walls)):
                    return [bomberman[0],bomberman[1]-i]
            i -= 1
    elif quadrante == 6:
        while i > 0:
            if(valid_pos([bomberman[0]+i,bomberman[1]],size_map,walls)):
                    return [bomberman[0]+i,bomberman[1]]
            i -= 1
    elif quadrante == 7:
        while i > 0:
            if(valid_pos([bomberman[0],bomberman[1]+i],size_map,walls)):
                    return [bomberman[0],bomberman[1]+i]
            i -= 1
    elif quadrante == 8:
        while i > 0:
            if(valid_pos([bomberman[0]-i,bomberman[1]],size_map,walls)):
                    return [bomberman[0]-i,bomberman[1]]
            i -= 1
    print("YAP ACORREU ERRO++++++++++++++++++++++++++++++++++")
    return [bomberman[0] +1,bomberman[1]+1]

def set_walls(wall):
    walls = []
    for i in wall:
        walls += [i]
    return walls

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
        [enemies[i]['pos'][0]+1,enemies[i]['pos'][1]-1],
        [enemies[i]['pos'][0],enemies[i]['pos'][1]]]
        i += 1
    return danger_zones

def set_bomb_danger_zones(bombs):
    bomb_danger_zone = []
    for bomb in bombs:
        i = -bomb[2]
        while i <= bomb[2]:
            bomb_danger_zone += [[bomb[0][0]+i,bomb[0][1]],
            [bomb[0][0],bomb[0][1]+i]]
            i += 1
        bomb_danger_zone += bomb
    return bomb_danger_zone

def enemies_all(enemies):
    arr = []
    if len(enemies):
        for i in enemies:
            arr += [i['pos']]
    return arr

def find_enemie_pos(enemie,walls,size):
    if valid_pos([enemie[0]+1,enemie[1]],size,walls):
        return [enemie[0]+1,enemie[1]]
    return None

def near_enemie(target_enemie, bomberman, prox):
    for enemie in target_enemie:
        if math.hypot(enemie['pos'][0]-bomberman[0],enemie['pos'][1]-bomberman[1]) < prox:
            return True
        else:
            return False
    return False

def atack_enemie(target_enemie, bomberman, prox):
    for enemie in target_enemie:
        if math.hypot(enemie['pos'][0]-bomberman[0],enemie['pos'][1]-bomberman[1]) < prox:
            return enemie['pos'] #[enemie['pos'][0]-2, enemie['pos'][1]]
        else:
            return None
    return None

def verify_last_steps(steps):
    aux = []
    i = 0
    if i < 12:
        aux.append(steps.pop(-1))
        i +=1
    if aux[1]==aux[5] and aux[5]==aux[9] and aux[9]==[14] and aux[2]==aux[4] and aux[4]==aux[6] and aux[6]==[8] :
        return ["d","s"]
    return []


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))