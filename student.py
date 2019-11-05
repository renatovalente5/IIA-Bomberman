#Este é o Ficheiro para avaliação

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
        arrive2 = False
        exit_dor = False
        last_steps = []
        bug_steps = []
        run_check = False
        run_check2 = False
        power_up = False
        enemie_more_close  = []
        catch_enemies = True # só para começar logo atrás dos inimigos
        count = 0
        check_balloom = False
        pos_blue = []
        search_blue = True
        count_powerups = 0

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  

                #print("\n\n")
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
                pos_blue = find_enemie_blue(bomberman, state['enemies'])
                danger_zones = set_danger_zones(state['enemies'])
                

                '''if pos_blue != [] and walls==[]:     #Apanhar Blue Enemie
                if state['bombs'] != []:
                    print("bomb")   # fugir da bomb que metemos no enemie blue
                    if not verify_range_bomb(state['bomberman'],state['bombs'][0][0],state['bombs'][0][2],size_map,walls):
                        if run_check2 == False:
                            w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls)
                            p = SearchProblem(game_walls, state['bomberman'],w)
                            t = SearchTree(p,'greedy')
                            wlk_path = convert_to_path(t.search(10))
                            print("go from: ",bomberman," to: ",w)
                            run_check2 = True
                    if len(wlk_path) == 1:
                        key = wlk_path[0]
                        wlk_path = []
                        run_check2 = False
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]

                else:
                    if search_blue == True or wlk_path == [] or wlk_path == ['']:
                        print("apanhar ENEMIE blue")
                        print(pos_blue)
                        #target_wall = enemie_more_close
                        p = SearchProblem(game_walls, state['bomberman'], pos_blue)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        search_blue = False
                        #
                        print("aqui1")
                    print("aqui2")
                    if near(state['bomberman'],pos_blue):
                        key = "B"
                        search_blue = True
                        print("aqui3")
                    else:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]
                        print("aqui4")
                    '''
                
                '''if math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 1 and state['enemies']!=[]:
                    print("Fugir do inimigo")
                    w = bomb_fled(state['bomberman'], enemie_more_close, 3, size_map, walls, danger_zones)
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
                        wlk_path = wlk_path[1:]'''
                
                if state['powerups']!=[] and count_powerups <=2: # condição para não apanhar o detonator no nivel 3 (falta melhorar para apanhar)
                    if power_up==False:
                        print("apanhar POWERUP")
                        target_wall = state["powerups"][0][0]
                        print(target_wall)
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        power_up=True
                    if (wlk_path == [''] or wlk_path == []):#and near_wall(bomberman, find_close_wall(bomberman, walls)):# and x==None:
                        power_up=False
                        count_powerups+=1
                        print("cheguei POWER_UP")
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]
                
                elif check_balloom==False and state['enemies']!=[] and state['walls']==[] and catch_enemies == True:   #and state['exit']==[] and state['walls']==[]    #Apanhar os inimigos logo no início
                    if state['bombs'] == []:  
                        print("apanhar ENEMIE")
                        print(enemie_more_close)
                        target_wall = enemie_more_close
                        print(target_wall)
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path_wall(t.search(100))
                        #
                        if near(state['bomberman'],target_wall):
                            key = "B"
                        else:
                            key = wlk_path[0]
                            wlk_path = wlk_path[1:]

                    else:   #Fugir da bomba
                        print("Fugir da bomba")
                        #if run_check == False:
                        w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls, danger_zones)
                        p = SearchProblem(game_walls, state['bomberman'],w)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(20))
                            #run_check == True
                        print("go from: ",bomberman," to: ",w)
                        print(wlk_path)
                        print("bomb-apagar")
                        # if (wlk_path == [''] or wlk_path == []):
                        #     run_check = False

                        if wlk_path != []:
                            key = wlk_path[0]
                            wlk_path = wlk_path[1:]

                elif state['exit']!= [] and state['enemies']==[]: #ir para a saída
                    target_wall = state['exit']
                    power_up =False
                    if exit_dor == False:
                        print("-------------------Target_EXIT-----------", target_wall)
                        print("exit go")
                        print("target wall4: ", target_wall)
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
                                    print("AAAAA")
                                    x = t.search(35)
                                    if x == None:
                                        print("NONE\nNONE\nNONE\nNONE")
                                        key = random_valid_key()
                                        #y==True
                                    else:
                                        print("converting...")
                                        wlk_path = convert_to_path_wall(x)
                                        print("wlk_pathh: ", wlk_path)
                                    
                                    if wlk_path != [] :
                                        run_check = True
                                    else:
                                        print("Super erro de parar!!!!!!!!!!!!!!!")
                                        # key = random_valid_key(bomberman, size_map, walls)
                                        # print("Correu: ", key)
                                        run_check = False
                                    
                                        
                            # if set_bomb_danger_zones(state['bombs']) and state['bombs']!=[]:
                            #     key = "A"
                            #     wlk_path = []
                            #     on_wall = True
                            #     run_check = False
                            if (wlk_path == [''] or wlk_path == []):#and near_wall(bomberman, find_close_wall(bomberman, walls)):# and x==None:
                                run_check = False
                                if(near_wall(state['bomberman'],target_wall)) and state['bomberman']!=[1,1]:     #!!!era importante, mas agora começou a dar erro com isto
                                #if(near_wall(state['bomberman'],target_wall))
                                    key = "B"
                                    #on_wall = True
                                
                                print("Aqui maluco")
                            elif wlk_path != []:
                                key = wlk_path[0]
                                wlk_path = wlk_path[1:]

                        elif state['bombs'] != []:
                            #print("bomb")
                            if not verify_range_bomb(state['bomberman'],state['bombs'][0][0],state['bombs'][0][2],size_map,walls):
                                if run_check == False:
                                    w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls, danger_zones)
                                    p = SearchProblem(game_walls, state['bomberman'],w)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(20))
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
                        if arrive2 == False:
                            target_wall = [2,7]
                            if not state['bomberman']==target_wall: #atacar paredes
                                if run_check == False:    
                                    print("not bomb")
                                    print("target wall2: ", target_wall)
                                    p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    run_check = True
                            # if set_bomb_danger_zones(state['bombs']) and state['bombs']!=[]:
                            #     key = "A"
                            #     wlk_path = []
                            if (wlk_path == [''] or wlk_path == []):#and near_wall(bomberman, find_close_wall(bomberman, walls)):# and x==None:
                                print("cheguei [2,7]")
                                arrive2 = True
                                run_check = False
                                key = "B"
                            elif wlk_path != []:
                                key = wlk_path[0]
                                wlk_path = wlk_path[1:]

                        elif arrive == False:     #ir até à partida
                            target_wall = [1,1]
                            if not state['bomberman']==target_wall: #atacar paredes
                                if run_check == False:    
                                    print("not bomb")
                                    print("target wall2: ", target_wall)
                                    p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    run_check = True
                            # if set_bomb_danger_zones(state['bombs']) and state['bombs']!=[]:
                            #     key = "A"
                            #     wlk_path = []
                            if (wlk_path == [''] or wlk_path == []) and math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 2:#and near_wall(bomberman, find_close_wall(bomberman, walls)):# and x==None:
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
                                    print("target wall3: ", target_wall)
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
                print("KEY: ", key)
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

def bomb_fled_renato(bomberman, bomba, radius, size_map, walls, danger_zones, i, j):
    radius = -i
    # i = -2
    # j = -2
    for a in range(i,radius):
        for b in range(j, radius):
            print("try")
            if verify_range_bomb([bomba[0]+i,bomba[1]+j], bomba, radius, size_map, walls):
                print("Bem verify")
                print([bomba[0]+i,bomba[1]+j])
                return [bomba[0]+i,bomba[1]+j]
    print("Recursiva\n")
    bomb_fled(bomberman,bomba,radius+1,size_map,walls,danger_zones, i-1, j-1)

def bomb_fled(bomberman, bomba, radius, size_map, walls, danger_zones, a=3):
    b = a
    print("bomb: ",bomba)
    for x in range(a):
        for y in range(b):
            if verify_range_bomb([bomba[0]-x,bomba[1]-y], bomba, radius, size_map, walls) and ([bomba[0]-x,bomba[1]-y] not in danger_zones):
                return [bomba[0]-x,bomba[1]-y]
            if verify_range_bomb([bomba[0]-x,bomba[1]+y], bomba, radius, size_map, walls) and ([bomba[0]-x,bomba[1]+y] not in danger_zones):
                return [bomba[0]-x,bomba[1]+y]
            if verify_range_bomb([bomba[0]+x,bomba[1]-y], bomba, radius, size_map, walls) and ([bomba[0]+x,bomba[1]-y] not in danger_zones):
                return [bomba[0]+x,bomba[1]-y]
            if verify_range_bomb([bomba[0]+x,bomba[1]+y], bomba, radius, size_map, walls) and ([bomba[0]+x,bomba[1]+y] not in danger_zones):
                return [bomba[0]+x,bomba[1]+y]
            if verify_range_bomb([bomba[0],bomba[1]-y], bomba, radius, size_map, walls) and ([bomba[0],bomba[1]-y] not in danger_zones):
                return [bomba[0],bomba[1]-y]
            if verify_range_bomb([bomba[0]-x,bomba[1]], bomba, radius, size_map, walls) and ([bomba[0]-x,bomba[1]] not in danger_zones):
                return [bomba[0]-x,bomba[1]]
            if verify_range_bomb([bomba[0]+x,bomba[1]], bomba, radius, size_map, walls) and ([bomba[0]+x,bomba[1]] not in danger_zones):
                return [bomba[0]+x,bomba[1]]
            if verify_range_bomb([bomba[0],bomba[1]+y], bomba, radius, size_map, walls) and ([bomba[0],bomba[1]+y] not in danger_zones):
                return [bomba[0],bomba[1]+y]
    bomb_fled(bomberman,bomba,radius,size_map,walls,b+1)

def bomb_fled_bom(bomberman, bomba, radius, size_map, walls, danger_zones, a=3):
    b = a
    #print(bomba)
    for x in range(a):
        for y in range(b):
            if verify_range_bomb([bomba[0]-x,bomba[1]], bomba, radius, size_map, walls) and [bomba[0]-x,bomba[1]] not in danger_zones:
                return [bomba[0]-x,bomba[1]]
            if verify_range_bomb([bomba[0]+x,bomba[1]], bomba, radius, size_map, walls) and [bomba[0]+x,bomba[1]] not in danger_zones:
                return [bomba[0]+x,bomba[1]]
            if verify_range_bomb([bomba[0],bomba[1]+y], bomba, radius, size_map, walls) and [bomba[0],bomba[1]+y] not in danger_zones:
                return [bomba[0],bomba[1]+y]
            if verify_range_bomb([bomba[0],bomba[1]-y], bomba, radius, size_map, walls) and [bomba[0],bomba[1]-y] not in danger_zones:
                return [bomba[0],bomba[1]-y]
            if verify_range_bomb([bomba[0]-x,bomba[1]-y], bomba, radius, size_map, walls) and [bomba[0]-x,bomba[1]-y] not in danger_zones:
                return [bomba[0]-x,bomba[1]-y]
            if verify_range_bomb([bomba[0]+x,bomba[1]+y], bomba, radius, size_map, walls) and [bomba[0]+x,bomba[1]+y] not in danger_zones:
                return [bomba[0]+x,bomba[1]+y]
    bomb_fled(bomberman,bomba,radius,size_map,walls,danger_zones,b+1)

def bomb_fled_antigo(bomberman, bomba, radius, size_map, walls):
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

def bomb_fled_try(bomberman, bomba, radius, size_map, walls, i, j):
    while i <= radius:
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
    bomb_fled_try(bomberman,bomba,radius+1,size_map,walls,i-1,j-1)

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
    print("YESSSSSSSSSSSSSSSSSSSSSSSSSSS")
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
    #print(True)
    return True

def domain2(bomberman, walls, size_map, enemie_list):
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
    if bomb_danger_zone !=[]:
        bomb_danger_zone.pop()
        bomb_danger_zone.pop()
    print("bomb_danger_zone: ", bomb_danger_zone)
    return bomb_danger_zone

def save_bomb_danger_zones(pos, range_bomb):
    for bomb in range_bomb:
        if pos == range_bomb or range_bomb== []:
            print("pos: ",pos)
            print("range_bomb: ",range_bomb)
            print("false")
            return False
    print("pos: ",pos)
    print("range_bomb: ",range_bomb)
    print("True")        
    return True

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
        #print(e['name'])
        if e['name'] == "Balloom":
            return True
    return False

def find_enemie_blue(pos, enemies):
    for enemie in enemies:
        if enemie['name'] == "Oneal":    #falta garantir que é só para os blue
            return enemie['pos']
    return []

def random_valid_key():
    aux = ["w", "d", "s", "a"]
    val = random.randint(0,3)
    print("val: ",val)
    return aux[val]

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))