import pygame
import sys
import random
import networkx as nx
import numpy as np
from envCoordinates.boardCoordinate import *
import json


# main class for the game
# this class is responsible for game logic and visualise the board
# update qtable and agent's reward and punishment
class Board:
    def __init__(self,walk_punishment,flag_reward,target_reward,back_punishment,been_punishment,alpha,gamma,boardname):
        # this variable is amount of punishment and reward that agent has been punished for each moving
        self.walk_punishment = walk_punishment
        self.flag_reward = flag_reward
        self.target_reward = target_reward
        self.back_punishment = back_punishment
        self.been_punishment = been_punishment
        # alpha gamma param for qlearning
        self.alpha = alpha
        self.gamma = gamma
    
        pygame.init()
        self.w = 600
        self.h = 600

        self.frameIter = 0
        self.fps = 60
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()

        # player object and position in the board
        self.player = Player([30,30])
        self.playerGp = pygame.sprite.Group()
        self.playerGp.add(self.player)

        # flags object and position in the board
        self.flags = []
        self.flagsObject = pygame.sprite.Group()

        # blocks object and position in the board
        self.blocks = []
        self.blocksObject = pygame.sprite.Group()

        # target object and position in the board
        self.target = Target([570,570])
        self.targetObject = pygame.sprite.Group()
        self.targetObject.add(self.target)

        # last state that agent has been in before last move
        self.lastState = None

        # nodes object of the board graph
        self.nodes = [[Node(i,j) for i in range(10)] for j in range(10)]
        # load environment from the file
        self.create_nodes(boardname)
        
        # start postion of the agent
        self.currentState = (0,0)
        self.seenNodes = []
    
    # make new file for qtables with zero values 
    def resetQtable(self,name):
        self.Qtable = np.zeros((10,10,4))
        arr_reshaped = self.Qtable.reshape(self.Qtable.shape[0], -1)
        np.savetxt('qtables/{}.txt'.format(name), arr_reshaped)
    
    # save current qtable to the file
    def saveQtable(self,name):
        pygame.image.save(self.screen, "screens/{}.jpg".format(name))
        self.Qtable = [[self.nodes[i][j].q for j in range(10)] for i in range(10)]
        self.Qtable = np.array(self.Qtable)
        arr_reshaped = self.Qtable.reshape(self.Qtable.shape[0], -1)
        np.savetxt('qtables/{}.txt'.format(name), arr_reshaped)

    # load qtable from the file
    def loadQtable(self,name):
        self.Qtable = np.loadtxt('qtables/{}.txt'.format(name))
        self.Qtable = self.Qtable.reshape(10,10,4)
        for i in range(10):
            for j in range(10):
                self.nodes[i][j].q = self.Qtable[(i,j)]

    # this function is responsible for one move of agent
    # it takes direction as input
    # its update current position of agent
    # update qtable
    # and return if agent has reached the target and flag or not
    def run(self,direction,step,iters):
        self.seenNodes.append(self.currentState)
        self.lastlastState = self.lastState
        self.lastState = ((self.player.rect.center[1]-30) // 60, (self.player.rect.center[0]-30) // 60)
        self.player.move(direction)
        self.currentState = ((self.player.rect.center[1]-30) // 60, (self.player.rect.center[0]-30) // 60)
        flag,target = self.update_qValues(direction)

        if flag:
            self.player.score += self.flag_reward
            self.remove_flag()
        

        self.update_screen(step,iters)
        return flag,target

    # this function is responsible for update the qtable acording to rewards
    def update_qValues(self,direction):
        r,flag,target = self.getActionReward()
        currentQ = self.nodes[self.lastState[0]][self.lastState[1]].q[self.getActionIndex(direction)]
        maxQ = max(self.nodes[self.currentState[0]][self.currentState[1]].q)
        newQ = (1 - self.alpha) * currentQ + self.alpha * (r + self.gamma * maxQ)
        self.nodes[self.lastState[0]][self.lastState[1]].q[self.getActionIndex(direction)] = newQ
        return flag,target

    # this function is responsible for turn direction to index of choise in qtable
    def getActionIndex(self,direction):
        if direction == 'left':
            return 0
        elif direction == 'up':
            return 1
        elif direction == 'right':
            return 2
        elif direction == 'down':
            return 3

    # this function return agent's reward
    # according to rewards and policy
    def getActionReward(self):
        flag = False
        target = False
        reward = 0
        reward += self.walk_punishment
        if self.rich_flag():
            reward += self.flag_reward
            flag = True

        if self.rich_target():
            reward += 1 - (len(self.flags)/7)
            target = True

        if self.back_move():
            reward += self.back_punishment 

        if self.been_move():
            reward += self.been_punishment

        # if self.target_withOut_flag():
        #     reward -= self.target_reward * 2
        #     target = True

        return reward,flag,target
    
    # check if agent reach target without see all flags
    def target_withOut_flag(self):
        if self.rich_target() and len(self.flags) != 0:
            return True
        else: return False

    # check that agent has been in this state before in this itteration
    def been_move(self):
        if self.currentState in self.seenNodes:
            return True
        else: return False

    # check if agetn see the flag or not, if yes unseen it
    def remove_flag(self):  
        for i in range(len(self.flags)):
            if self.flags[i].rect.center == self.player.rect.center:
                ii = (self.flags[i].rect.center[0] - 30) // 60
                jj = (self.flags[i].rect.center[1] - 30) // 60
                self.flagsObject.remove(self.flags[i])
                self.flags.pop(i)
                self.nodes[jj][ii].type = "way"
                break
    
    # check if agent see any flag or not
    def rich_flag(self):
        if  pygame.sprite.spritecollide(self.player, self.flagsObject, True):
            return True
        else: return False

    # check if agent see the target or not
    def rich_target(self):
        if  pygame.sprite.spritecollide(self.player, self.targetObject, False):
            return True
        else: return False

    # check if agent move back or not
    def back_move(self):
        if self.lastlastState == self.currentState:
            return True
        else: return False

    # this function is responsible for set type of each node
    def create_nodes(self,board = "mainBoard"):
        for i in range(10):
            for j in range(10):
                if board == "mainBoard":
                    types  = mainBoard
                else:
                    types = board

                if i == 0:
                    self.nodes[i][j].q[1] = np.NINF
                elif i == 9:
                    self.nodes[i][j].q[3] = np.NINF
                if j == 0:
                    self.nodes[i][j].q[0] = np.NINF
                elif j == 9:
                    self.nodes[i][j].q[2] = np.NINF
                if types[i][j] == 0:
                    self.nodes[i][j].type = "start"
                    
                elif types[i][j] == 1:
                    self.nodes[i][j].type = "way"
                    
                elif types[i][j] == 2:
                    self.nodes[i][j].type = "flag"
                    self.create_flag(ItoC(j+1,i+1))
                elif types[i][j] == 3:
                    self.nodes[i][j].type = "block"
                    self.create_block(ItoC(j+1,i+1))
                elif types[i][j] == 4:
                    self.nodes[i][j].type = "target"

    # this function is responsible for create flag object and add it to flags list 
    def create_flag(self,pos):
        flagObj = Flag(pos)
        self.flags.append(flagObj)
        self.flagsObject.add(flagObj)

    # this function is responsible for create block object and add it to blocks list
    def create_block(self,pos):
        blockObj = Block(pos)
        self.blocks.append(blockObj)
        self.blocksObject.add(blockObj)

    # this function is responsible for reset game after each itteration
    def reset(self,iters,board):
        self.seenNodes = []
        self.lastState = None
        self.curentState = (0,0)

        self.player.rect.center = [30,30]
        self.flags = []
        self.flagsObject = pygame.sprite.Group()
        self.blocks = []
        self.blocksObject = pygame.sprite.Group()
        self.target = Target([570,570])
        self.targetObject = pygame.sprite.Group()
        self.targetObject.add(self.target)

        self.create_nodes(board)
        self.screen = pygame.display.set_mode([self.w, self.h])
        self.frameIter = 0
        self.player.score = 0
        self.update_screen(0,iters)

    # this function is responsible for update screen after each move   
    def update_screen(self,step,iters):
        self.screen = pygame.display.set_mode([self.w, self.h])
        self.screen.fill((112, 146, 190))
        self.playerGp.draw(self.screen)  
        self.flagsObject.draw(self.screen) 
        self.blocksObject.draw(self.screen)
        self.targetObject.draw(self.screen)

        score_font = pygame.font.SysFont("comicsansms", 10) 
        itter_font = pygame.font.SysFont("comicsansms", 10) 

        value = score_font.render("Step: " + str(step), True, (255, 255, 255))
        self.screen.blit(value, [60, 0])

        value = itter_font.render("Iters: " + str(iters), True, (255, 255, 255))
        self.screen.blit(value, [60, 15])

        # self.write_v()
        self.write_q()
        self.draw_borders()
        pygame.display.update()  
        pygame.display.flip()   

    # this function is responsible for draw borders of each node
    def draw_borders(self):
        for i in range(9):
            pygame.draw.line(self.screen, (0,0,0), ((i+1)*60,0),((i+1)*60,600) , 1)
            pygame.draw.line(self.screen, (0,0,0), (0,(i+1)*60),(600,(i+1)*60) , 1)

    # this function is responsible for write q value of each node in display
    def write_q(self):
        for i in range(10):
            for j in range(10):
                node = self.nodes[i][j]
                direction =np.argmax(node.q)
                if node.type == "block":   
                    continue
                
                if direction == 0:
                    leftQ = pygame.font.SysFont("comicsansms", 10).render("{:.2f}".format(node.q[0]), True, (255, 255, 255))
                else:
                    leftQ = pygame.font.SysFont("comicsansms", 10).render("{:.2f}".format(node.q[0]), True, (0, 0, 0))
                self.screen.blit(leftQ, [node.x-27,node.y-10])

                if direction == 1:
                    upQ = pygame.font.SysFont("comicsansms", 10).render("{:.2f}".format(node.q[1]), True, (255, 255, 255))
                else: 
                    upQ = pygame.font.SysFont("comicsansms", 10).render("{:.2f}".format(node.q[1]), True, (0, 0, 0))
                self.screen.blit(upQ, [node.x-5,node.y-30])

                if direction == 2:
                    rightQ = pygame.font.SysFont("comicsansms", 10).render("{:.2f}".format(node.q[2]), True, (255, 255, 255))
                else:
                    rightQ = pygame.font.SysFont("comicsansms", 10).render("{:.2f}".format(node.q[2]), True, (0, 0, 0))
                self.screen.blit(rightQ, [node.x+5,node.y-4])

                if direction == 3:                
                    downQ = pygame.font.SysFont("comicsansms", 10).render("{:.2f}".format(node.q[3]), True, (255, 255, 255))
                else:
                    downQ = pygame.font.SysFont("comicsansms", 10).render("{:.2f}".format(node.q[3]), True, (0, 0, 0))
                self.screen.blit(downQ, [node.x-5,node.y+15])


    # def write_v(self):
    #     for i in range(10):
    #         for j in range(10):
    #             v_value = pygame.font.SysFont("comicsansms", 15).render(str(self.v_values[i,j]), True, (0, 0, 0))
    #             self.screen.blit(v_value, [j*60+15, i*60+15])

# Class for player responsible for player movement and position
class Player(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([60,60])
        self.rect = self.image.get_rect()
        self.image.fill((137,107,158))
        self.moves = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
        self.vx = 20
        self.vy = 20
        self.rect.center = position
        self.score = 0
    
    def move(self,direction):
        if direction == "left":
            self.rect.x -= 60
        elif direction == "right":
            self.rect.x += 60
        elif direction == "up":
            self.rect.y -= 60
        elif direction == "down":
            self.rect.y += 60


# Class for flag responsible for flag positions
class Flag(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([60,60])
        self.rect = self.image.get_rect()
        self.image.fill((29,232,147))
        self.rect.center = position


# Class for block responsible for block positions
class Block(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([60,60])
        self.rect = self.image.get_rect()
        self.image.fill((64, 61, 56))
        self.rect.center = position


# Class for target responsible for target positions
class Target(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([60,60])
        self.rect = self.image.get_rect()
        self.image.fill((28,145,62))
        self.rect.center = position


# this function is responsible for change i,j of node to x,y of display
def ItoC(i,j):
    return (i*60-30,j*60-30)

# this function is responsible for change x,y of display to i,j of node
def CtoI(x,y):
    return ((x-30)//60,(y-30)//60)


# class node is responsible for each node in grid. it keeps position of each node, type of node and q values.
class Node:
    def __init__(self,i,j):
        self.x = i*60+30
        self.y = j*60+30
        
        self.i = i
        self.j = j

        self.neighbors = [None,None,None,None]
        self.q = [0,0,0,0] # L U R D 

        self.V = 0

        self.type = None

