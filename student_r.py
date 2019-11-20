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
        target_wall = []
        target_enemie = []
        wlk_path = []
        danger_zones = []
        bomb_danger_zone = []
        powerups = []
        bomberman = []
        game_walls = None
        size_map = mapa.size
        #on_wall = None
        #pos_enemie = []
        #arrive = False
        #arrive2 = False
        #exit_dor = False
        #last_steps = []
        #bug_steps = []
        run_check = False
        #run_check2 = False
        #power_up = False
        enemie_more_close  = []
        #catch_enemies = True # só para começar logo atrás dos inimigos
        #count = 0
        check_balloom_doll = False
        pos_blue = []   #ainda não estamos a usar

        #Novas
        tatic = False
        spawn=list(mapa.bomberman_spawn)


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
                pos_blue = find_enemie_blue(bomberman, state['enemies'])
                danger_zones = set_danger_zones(state['enemies'])

                
                #Is there Bomb on the Map?
                if(bomb != []):
                    #Are you in a savety place?
                    if not verify_range_bomb(state['bomberman'],state['bombs'][0][0],state['bombs'][0][2],size_map,walls):
                        if run_check == False:
                            run_check = True
                            print("Calculando...")
                            w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls, danger_zones)
                            print("WWWWWWWWWWWWWWW: ", w)
                            p = SearchProblem(game_walls, state['bomberman'],w)
                            t = SearchTree(p,'greedy')
                            wlk_path = convert_to_path(t.search(100))
                            print("wlk_path: ",wlk_path)
                            print("go from: ",bomberman," to: ",w)
                            if wlk_path==[]:
                                key="A" #tentar procurar outro caminho em vez de se matar
                                print("S\no\nu\n \nm\ne\ns\nm\no\n \nb\nu\nr\nr\no\n!!!")
                            
                    #Not
                    else:
                        key="A"
                        print(key)

                #Not
                else:
                    #Is the enemies near from me? (run) (enquanto as ainda ouver paredes)
                    if math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 1.5 and check_balloom_doll==True:
                        print("Fugir do inimigo")
                        w = bomb_fled(state['bomberman'], enemie_more_close, 3, size_map, walls, danger_zones)
                        p = SearchProblem(game_walls, state['bomberman'],w)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                        print("go from: ",bomberman," to: ",w)
                        print(wlk_path)
                        print("Running")

                    #Is there item on the Map
                    if state['powerups']!=[]:
                        print("Apanhar POWERUP")
                        target_wall = state["powerups"][0][0]
                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                        t = SearchTree(p,'greedy')
                        wlk_path = convert_to_path(t.search(100))
                    #Not
                    else:
                        #Are there enemies alive? (falta meter para atacar inimigo azul) (só quando não houver mais paredes)
                        if state['enemies']!=[] and state['walls']==[]:
                            if check_balloom_doll==False:
                                target_wall = enemie_more_close
                                print("Apanhar ENEMIE: ",target_wall)
                                p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                t = SearchTree(p,'greedy')
                                wlk_path = convert_to_path_wall(t.search(100))
                        
                            #Can I reach the enemie? (Já não temos paredes?) (Fazer tatic do canto)
                            # elif not state['bomberman']==[3,7] and tatic==False:  ##não pode ter ist para ficar dinamico
                            #     if run_check == False:    
                            #         print("not bombb")
                            #         print("target wall2: ", [3,7])
                            #         p = SearchProblem(game_walls, state['bomberman'], [3,7])
                            #         t = SearchTree(p,'greedy')
                            #         wlk_path = convert_to_path(t.search(100))
                            #         run_check = True
                            #         tatic=True

                            elif not state['bomberman']==spawn:
                                if run_check == False:    
                                    print("not bomb")
                                    print("target wall2: ", spawn)
                                    p = SearchProblem(game_walls, state['bomberman'], spawn)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    run_check = True
                            
                            elif math.hypot(enemie_more_close[0]-bomberman[0],enemie_more_close[1]-bomberman[1]) <= 2:
                                wlk_path=["B"]

                                if run_check == False and bomb!=[]:
                                    w = bomb_fled(state['bomberman'], state['bombs'][0][0], state['bombs'][0][2], size_map, walls, danger_zones)
                                    p = SearchProblem(game_walls, state['bomberman'],w)
                                    t = SearchTree(p,'greedy')
                                    wlk_path = convert_to_path(t.search(100))
                                    wlk_path.insert(0,"B")
                                    run_check = True
                            #Not - (Atacar paredes)
                            # target_wall = find_close_wall(state['bomberman'],walls)
                            # if not near_wall(state['bomberman'],target_wall): #atacar paredes
                            #     if run_check== False:
                            #         run_check = True
                            #         print("target wall: ", target_wall)
                            #         p = SearchProblem(game_walls, state['bomberman'], target_wall)
                            #         t = SearchTree(p,'greedy')
                            #         wlk_path = convert_to_path_wall(t.search(100))
                            #         #tirei código

                        #Not
                        else:
                            #Is the exit avaliable?
                            if state['exit']!= [] and state['enemies']==[]: #ir para a saída
                                target_wall = state['exit']
                                print("-------------------Target_EXIT-----------", target_wall)
                                p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                t = SearchTree(p,'greedy')
                                wlk_path = convert_to_path(t.search(100))
                                tatic=False

                            #Not - (Atacar paredes)
                            
                            #Enquanto ataca paredes ver se não vai contra um inimigo - fazer funções para se desviar para o lado contrario

                            else:   #(Atacar paredes)
                                target_wall = find_close_wall(state['bomberman'],walls)
                                #if state['bombs'] == [] and walls != []:
                                if not near_wall(state['bomberman'],target_wall): #atacar paredes
                                    if run_check== False:
                                        run_check = True
                                        print("target wall: ", target_wall)
                                        p = SearchProblem(game_walls, state['bomberman'], target_wall)
                                        t = SearchTree(p,'greedy')
                                        x = t.search(100)
                                        if x == None:   #Caso o Bomberman fique indeciso entre 2 caminhos
                                            print("NONE\nNONE\nNONE\nNONE")
                                            key = random_valid_key()
                                        else:
                                            wlk_path = convert_to_path_wall(x)

                #LER DATAPATH
                if (wlk_path == ['A'] or wlk_path == []):
                    run_check = False
                    if(near_wall(state['bomberman'],target_wall)) and bomb == []:# and state['bomberman']!=[1,1]:     #!!!era importante, mas agora começou a dar erro com isto
                        key = "B"
                elif wlk_path != []:
                    print("wlk_path: " ,wlk_path)
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

def valid_moove(pos, mov, size_map, walls): #not used
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

def near(bomberman, wall):  #not used but usefull
    if math.hypot(wall[0]-bomberman[0],wall[1]-bomberman[1]) <= 2:
        return True
    return False

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

def bomb_safe(bomberman, bomb_danger_zone): #not used
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

def domain2(bomberman, walls, size_map, enemie_list):   #not used
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

def try_area(bomberman, quadrante, walls, size_map):    #not used
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

def set_bomb_danger_zones(bombs):   #not used
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

def save_bomb_danger_zones(pos, range_bomb):    #not used
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

def find_enemie_pos(enemie,walls,size):     #not used
    if valid_pos([enemie[0]+1,enemie[1]],size,walls):
        return [enemie[0]+1,enemie[1]]
    return None

def near_enemie(target_enemie, bomberman, prox):    #not used
    for enemie in target_enemie:
        if math.hypot(enemie['pos'][0]-bomberman[0],enemie['pos'][1]-bomberman[1]) < prox:
            return True
        else:
            return False
    return False

def atack_enemie(target_enemie, bomberman, prox):  #not used
    for enemie in target_enemie:
        if math.hypot(enemie['pos'][0]-bomberman[0],enemie['pos'][1]-bomberman[1]) < prox:
            return enemie['pos'] #[enemie['pos'][0]-2, enemie['pos'][1]]
        else:
            return None
    return None

def find_balloom_doll(enemies):
    for e in enemies:
        #print(e['name'])
        if e['name'] == "Balloom" or e['name'] == "Doll":
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
