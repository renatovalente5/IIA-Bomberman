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
        danger_zones = []
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
        enemie_more_close  = []
        catch_enemies = True # só para começar logo atrás dos inimigos
        count = 0

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  

                print("\n\n")
                #print(state)
                try:
                    bomberman = state['bomberman']
                except:
                    print("--+--+-+-+-+-+-+-+-+-+-+-+-+-+-+-+--+--ERROR BOMBERMAN")
                    pass

                try:
                    walls = set_walls(state['walls'])
                    powerups = state['powerups']
                except:
                    print("--+--+-+-+-+-+-+-+-+-+-+-+-+-+-+-+--+--ERROR WALLS")
                    pass

                game_walls = Paredes(domain(state['bomberman'],walls,size_map,enemies_all(state['enemies'])),size_map)
                enemie_more_close = find_close_wall(state['bomberman'], enemies_all(state['enemies']))
                check_balloom = find_balloom(state['enemies'])
                
                # if in_range(bomberman, enemie_more_close, 3, game_walls):
                if math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 1 and state['enemies']!=[]:
                    print("Fugir do inimigo")
                    w = bomb_fled(state['bomberman'], enemie_more_close, 3, size_map, walls)
                    p = SearchProblem(game_walls, state['bomberman'],w)
                    t = SearchTree(p,'greedy')
                    wlk_path = convert_to_path(t.search(10))
                    print("go from: ",bomberman," to: ",w)
                    print(wlk_path)
                    print("Running")
                    if len(wlk_path) == 1:
                        key = wlk_path[0]
                        wlk_path = []
                        #run_check = False
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]

                # if state['enemies']!=[] and check_balloom==False and state['walls']==[]:   #apanhar os outros inimigos sem ser os Ballooms
                #     if state['bombs'] == []:
                #         if count%3==0: 
                #             print("apanhar ENEMIE")
                #             print(enemie_more_close)
                #             target_wall = enemie_more_close
                #             print(target_wall)
                #             p = SearchProblem(game_walls, state['bomberman'], target_wall)
                #             t = SearchTree(p,'greedy')
                #             wlk_path = convert_to_path(t.search(100))
                #             #
                #             count+=1
                #             if near(state['bomberman'],target_wall):
                #                 key = "B"
                #             else:
                #                 key = wlk_path[0]
                #                 wlk_path = wlk_path[1:]

                #     else:   #Fugir da bomba
                #         print("Fugir da bomba")
                #         w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls)
                #         p = SearchProblem(game_walls, state['bomberman'],w)
                #         t = SearchTree(p,'greedy')
                #         wlk_path = convert_to_path(t.search(10))
                #         print("go from: ",bomberman," to: ",w)
                #         print(wlk_path)
                #         print("bomb")
                #         if len(wlk_path) == 1:
                #             key = wlk_path[0]
                #             wlk_path = []
                #             #run_check = False
                #         elif wlk_path != []:
                #             key = wlk_path[0]
                #             wlk_path = wlk_path[1:]

                if check_balloom==False and state['enemies']!=[] and state['walls']==[] and catch_enemies == True:   #and state['exit']==[] and state['walls']==[]    #Apanhar os inimigos logo no início
                    if state['bombs'] == []:  
                        print("apanhar ENEMIE")
                        print(enemie_more_close)
                        target_wall = enemie_more_close
                        print(target_wall)
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        #
                        if near(state['bomberman'],target_wall):
                            key = "B"
                        else:
                            key = wlk_path[0]
                            wlk_path = wlk_path[1:]

                    else:   #Fugir da bomba
                        print("Fugir da bomba")
                        w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls)
                        p = SearchProblem(game_walls, state['bomberman'],w)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(10))
                        print("go from: ",bomberman," to: ",w)
                        print(wlk_path)
                        print("bomb")
                        if len(wlk_path) == 1:
                            key = wlk_path[0]
                            wlk_path = []
                            #run_check = False
                        elif wlk_path != []:
                            key = wlk_path[0]
                            wlk_path = wlk_path[1:]

                elif state['powerups']!=[]:
                    if power_up==False:
                        print("apanhar POWERUP")
                        target_wall = state["powerups"][0][0]
                        print(target_wall)
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        power_up=True
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]
                elif state['exit']!= [] and state['enemies']==[]: #ir para a saída
                    target_wall = state['exit']
                    power_up =False
                    if exit_dor == False:
                        print("-------------------target_wall-----------", target_wall)
                        print("exit go")
                        print("target wall: ", target_wall)
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        exit_dor = True
                    if (wlk_path == [''] or wlk_path == []):#and near_wall(bomberman, find_close_wall(bomberman, walls)):# and x==None:
                        exit_dor = False
                        print("cheguei exit")
                        #arrive = True
                        #key = "B"
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]
                else:
                    if state['walls']!=[]:
                        target_wall = find_close_wall(state['bomberman'],walls) #acrescentar
                        if state['bombs'] == [] and walls != []:
                            if not near_wall(state['bomberman'],target_wall): #atacar paredes
                                if run_check == False:
                                    print("not bomb")
                                    print("target wall: ", target_wall)
                                    p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path_wall(t.search(100))
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
                            print("bomb")
                            if not verify_range_bomb(state['bomberman'],state['bombs'][0][0],state['bombs'][0][2],size_map,walls):
                                if run_check == False:
                                    w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls)
                                    p = SearchProblem(game_walls, state['bomberman'],w)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(10))
                                    print("go from: ",bomberman," to: ",w)
                                    run_check = True
                            if len(wlk_path) == 1:
                                key = wlk_path[0]
                                wlk_path = []
                                run_check = False
                            elif wlk_path != []:
                                key = wlk_path[0]
                                wlk_path = wlk_path[1:]
                    else:
                        if arrive == False:     #ir até à partida
                            target_wall = [1,1]
                            if not state['bomberman']==target_wall: #atacar paredes
                                if run_check == False:    
                                    print("not bomb")
                                    print("target wall: ", target_wall)
                                    p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    run_check = True
                            if (wlk_path == [''] or wlk_path == []):#and near_wall(bomberman, find_close_wall(bomberman, walls)):# and x==None:
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
                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent

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

def near(bomberman, wall):
    if math.hypot(wall[0]-bomberman[0],wall[1]-bomberman[1]) <= 2:
        return True
    return False

def bomb_fled(bomberman, bomba, radius, size_map, walls):
    i = -2
    while i <= radius:
        j = -2
        while j <= radius:
            if verify_range_bomb([bomba[0]+i,bomba[1]+j], bomba, radius, size_map, walls):
                print("valid scape pos: ", [bomba[0]+i,bomba[1]+j])
                return [bomba[0]+i,bomba[1]+j]
            elif verify_range_bomb([bomba[0]-i,bomba[1]+j], bomba, radius, size_map, walls):
                print("valid scape pos: ", [bomba[0]-i,bomba[1]+j])
                return [bomba[0]-i,bomba[1]+j]
            elif verify_range_bomb([bomba[0]+i,bomba[1]-j], bomba, radius, size_map, walls):
                print("valid scape pos: ", [bomba[0]+i,bomba[1]-j])
                return [bomba[0]+i,bomba[1]-j]
            elif verify_range_bomb([bomba[0]-i,bomba[1]-j], bomba, radius, size_map, walls):
                print("valid scape pos: ", [bomba[0]-i,bomba[1]-j])
                return [bomba[0]-i,bomba[1]-j]
            j+=1
        i+=1
    bomb_fled(bomberman,bomba,radius+1,size_map,walls)

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
        [enemies[i]['pos'][0]+1,enemies[i]['pos'][1]-1]]
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
    for i in enemies:
        arr += [i['pos']]
    return arr

def enemies_random(enemie):
    if enemie != []:
        for i in enemie:
            return i
    #maybe need other return aqui
    print("Já sabia boy, na fun enemies_random +-------------------------------------- ")

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

def find_balloom(enemies):
    for e in enemies:
        print(e['name'])
        if e['name'] == "Balloom":
            return True
    return False

def in_range(pos, alvo, radius, game_walls):
        bx, by = pos
        cx, cy = alvo

        if by == cy:
            for r in range(radius + 1):
                if game_walls.is_stone((bx + r, by)):
                    break  # protected by stone to the right
                if (cx, cy) == (bx + r, by):
                    return True
            for r in range(radius + 1):
                if game_walls.is_stone((bx - r, by)):
                    break  # protected by stone to the left 
                if (cx, cy) == (bx - r, by):
                    return True
        if bx == cx:
            for r in range(radius + 1):
                if game_walls.is_stone((bx, by + r)):
                    break  # protected by stone in the bottom
                if (cx, cy) == (bx, by + r):
                    return True
            for r in range(radius + 1):
                if game_walls.is_stone((bx, by - r)):
                    break  # protected by stone in the top
                if (cx, cy) == (bx, by - r):
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