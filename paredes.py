from tree_search_bomb import *
import math

class Paredes(SearchDomain):
    def __init__(self,connections,size_map):
        self.connections = connections
        self.size_map = size_map
    def actions(self,pos):
        actlist = []
        for (C1,C2,D) in self.connections:
            if C1 == pos:
                if (pos[0]-C2[0]) == 1:
                    actlist += ["a"]
                elif (pos[0]-C2[0]) == -1:
                    actlist += ["d"]
                elif (pos[1]-C2[1]) == 1:
                    actlist += ["w"]
                elif (pos[1]-C2[1]) == -1:
                    actlist += ["s"]
            elif C2 == pos:
                if (pos[0]-C1[0]) == 1:
                    actlist += ["d"]
                elif (pos[0]-C1[0]) == -1:
                    actlist += ["a"]
                elif (pos[1]-C1[1]) == 1:
                    actlist += ["s"]
                elif (pos[1]-C1[1]) == -1:
                    actlist += ["w"]
        return actlist
    def result(self,pos, action):
        k = action
        if k=="w" and not pos[1] == 1:
            return [pos[0],pos[1]-1]
        if k=="a" and not pos[0] == 1:
            return [pos[0]-1,pos[1]]
        if k=="s" and not pos[1]-1 == self.size_map[1]:
            return [pos[0],pos[1]+1]
        if k=="d" and not pos[0]-1 == self.size_map[0]:
            return [pos[0]+1,pos[1]]
    def cost(self, pos, action):
        return 1
    def heuristic(self, state, goal_state):
        c1_x, c1_y = state
        c2_x, c2_y = goal_state
        return math.hypot(c1_x-c2_x, c1_y-c2_y)