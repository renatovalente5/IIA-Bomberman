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
        wlk_path = []
        danger_zones = []
        bomb_danger_zone = []
        powerups = []
        bomberman = []
        size_map = mapa.size
        on_wall = None

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server

                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                print("\n\n")
                walls = set_walls(state['walls'])
                powerups = state['powerups']
                bomberman = state['bomberman']
                target_wall = find_close_wall(state['bomberman'],walls)
                if math.hypot(target_wall[0]-bomberman[0]+1,target_wall[1]-bomberman[1]+1) > 8.6:
                    target_wall = [bomberman[0]+4, bomberman[1]+4]
                danger_zones = set_danger_zones(state['enemies'])
                bomb_danger_zone = set_bomb_danger_zones(state['bombs'])
                game_walls = Paredes(domain(state['bomberman'],walls,find_close_wall(state['bomberman'],walls),size_map),size_map)
                p = SearchProblem(game_walls, state['bomberman'], target_wall)
                t = SearchTree(p,'a*')
                if wlk_path == [] and t.search(100) != None and on_wall != True:
                    try:
                        print(t.search(100))
                        wlk_path = convert_to_path(list(t.search(100)))
                    except:
                        pass
                print("path: "+str(wlk_path))
                if state['bombs'] == []:
                    if walls == [] and state['exit'] != [] and state['enemies'] == []:
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'a*')
                        wlk_path = convert_to_path(list(t.search(100)))
                    print("not bomb")
                    bomb_danger_zone = []
                    if (wlk_path == [''] or wlk_path == []) and near_wall(bomberman, find_close_wall(bomberman, walls)):
                        print("on wall")
                        on_wall = True
                        key = "B"
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]
                else:
                    bomb_danger_zone = set_bomb_danger_zones(state['bombs'])
                    for danger_zone in bomb_danger_zone:
                        if bomberman != danger_zone:
                            wlk_path = []
                        elif bomberman == danger_zone and wlk_path == []:
                            vec = vector2dir(bomberman[0]-target_wall[0], bomberman[1]-target_wall[1])
                            if vec == 1 or vec == 3:   #a/d
                                if not valid_pos([target_wall[0],target_wall[1]-1], size_map, walls):
                                    if valid_pos([target_wall[0]+1,target_wall[1]-2], size_map, walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]+1,target_wall[1]-2])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]+1,target_wall[1]+2],size_map,walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]+1,target_wall[1]+2])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]-1,target_wall[1]-2],size_map,walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]-1,target_wall[1]-2])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]-1,target_wall[1]+2],size_map,walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]-1,target_wall[1]+2])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]-3,target_wall[1]+1],size_map,walls) and vec == 1:
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]-3,target_wall[1]+1])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                elif valid_pos([target_wall[0],target_wall[1]-1],size_map,walls):
                                    if valid_pos([target_wall[0]-2,target_wall[1]-1],size_map,walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]-2,target_wall[1]-1])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]-2,target_wall[1]+1],size_map,walls):
                                        pass
                            if vec == 0 or vec == 2:   #w/s
                                if not valid_pos([target_wall[0],target_wall[1]-1], size_map, walls):
                                    if valid_pos([target_wall[0]+1,target_wall[1]-2], size_map, walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]+1,target_wall[1]-2])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]+1,target_wall[1]+2],size_map,walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]+1,target_wall[1]+2])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]-1,target_wall[1]-2],size_map,walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]-1,target_wall[1]-2])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]-1,target_wall[1]+2],size_map,walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]-1,target_wall[1]+2])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]-3,target_wall[1]+1],size_map,walls) and vec == 1:
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]-3,target_wall[1]+1])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                elif valid_pos([target_wall[0],target_wall[1]-1],size_map,walls):
                                    if valid_pos([target_wall[0]-2,target_wall[1]-1],size_map,walls):
                                        p = SearchProblem(game_walls, state['bomberman'], [target_wall[0]-2,target_wall[1]-1])
                                        t = SearchTree(p,'a*')
                                        wlk_path = convert_to_path(list(t.search(100)))
                                    elif valid_pos([target_wall[0]-2,target_wall[1]+1],size_map,walls):
                                        pass
                    on_wall = False
                    print("bomb")
                    if len(wlk_path) == 1:
                        key = wlk_path[0]
                        count = 2
                        wlk_path = []
                    elif wlk_path != []:
                        key = wlk_path[0]
                        wlk_path = wlk_path[1:]
                    elif wlk_path == []:
                        key = ""
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
    if pos[0] == 0 or pos[0] == size_map[0] or pos[1] == 0 or pos[1] == size_map[1]:
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
def bomb_fled(bomberman, bomba, mapa, detonador = False):
    b = Bomb(bomberman, mapa,bomba[2])
def bomb_safe(bomberman, bomb_danger_zone):
    for i in bomb_danger_zone:
        if bomberman == i:
            return False
    return True
def find_close_wall(bomberman, walls):
    aux = 100000
    for i in walls:
        dist = math.hypot(bomberman[0] - i[0], bomberman[1] - i[1])
        if dist < aux:
            aux = dist
            x = i
    return x
def convert_to_path(p):
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


def next_move(bomberman, cw, walls, danger_zone):
        better_mov = ""
        dist = math.hypot(bomberman[0]-cw[0],bomberman[1]-cw[1])
        if math.hypot(bomberman[0]+1-cw[0],bomberman[1]-cw[1]) < dist and valid_pos([bomberman[0]+1,bomberman[1]]) and [bomberman[0]+1,bomberman[1]] not in danger_zone:
                dist = math.hypot(bomberman[0]+1-cw[0],bomberman[1]-cw[1])
                better_mov = "d"
        if math.hypot(bomberman[0]-1-cw[0],bomberman[1]-cw[1]) < dist and valid_pos([bomberman[0]-1,bomberman[1]]) and [bomberman[0]-1,bomberman[1]] not in danger_zone:
                dist = math.hypot(bomberman[0]-1-cw[0],bomberman[1]-cw[1])
                better_mov = "a"
        if math.hypot(bomberman[0]-cw[0],bomberman[1]-1-cw[1]) < dist and valid_pos([bomberman[0],bomberman[1]-1]) and [bomberman[0],bomberman[1]-1] not in danger_zone:
                dist = math.hypot(bomberman[0]-cw[0],bomberman[1]-1-cw[1])
                better_mov = "w"
        if math.hypot(bomberman[0]-cw[0],bomberman[1]+1-cw[1]) < dist and valid_pos([bomberman[0],bomberman[1]+1]) and [bomberman[0],bomberman[1]+1] not in danger_zone:
                dist = math.hypot(bomberman[0]-cw[0],bomberman[1]+1-cw[1])
                better_mov = "d"

def domain(bomberman,walls,mr,size_map):
    print(mr)
    '''if mr[0] - bomberman[0] > 0 and mr[1] - bomberman[1] > 0:
        if mr[0]+2 < size_map[0]:
            x = mr[0]+2
        elif mr[0]+1 < size_map[0]:
            x = mr[0]+1
        else:
            x = mr[0]
        if mr[1]+2 < size_map[1]:
            y = mr[1]+2
        elif mr[1]+1 < size_map[1]:
            y = mr[1]+1
        else:
            y = mr[1]
    else:
        if mr[0]-2 > 0:
            x = mr[0]-2
        elif mr[0]-1 > 0:
            x = mr[0]-1
        else:
            x = mr[0]
        if mr[1]-2 > 0:
            y = mr[1]-2
        elif mr[1]-1 > 0:
            y = mr[1]-1
        else:
            y = mr[1]
    if x<y and x>0:
        x = y
    i = bomberman[1]
    lista = []
    w = 0
    z = 0
    aux = [w,z]'''
    y = size_map[1]
    x = size_map[0]
    lista = []
    i = 1
    while i < y:
        j = 1
        while j < x:
            if valid_pos([i,j],size_map,walls):
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


def find_path(pos, dest):
    path = []
    x = dest[0]-pos[0]
    y = dest[1]-pos[1]
    if x < 0:
        x_key = "a"
        x = x*(-1)
    else:
        x_key = "d"
    if y < 0:
        y_key = "w"
        y = y*(-1)
    else:
        y_key = "s"
    i = 0
    while i < x:
        path += [x_key]
        i += 1
    i = 1
    while i < y:
        path += [y_key]
        i += 1
    return path
def find_path2(pos, dest):
    path = []
    x = dest[0]-pos[0]
    y = dest[1]-pos[1]
    if x < 0:
        x_key = "a"
        x = x*-1
    else:
        x_key = "d"
    if y < 0:
        y_key = "w"
        y = y*-1
    else:
        y_key = "s"
    i = 0
    while i < y:
        path += [y_key]
        i += 1
    i = 1
    while i < x:
        path += [x_key]
        i += 1
    return path
def set_walls(wall):
    walls = []
    for i in wall:
        walls += [i]
    return walls
    
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))