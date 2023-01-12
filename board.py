import pygame
import sys
import random
import networkx as nx
import numpy as np


class Board:
    def __init__(self):
        self.w = 600
        self.h = 600
        self.squares_hw = 60
        
        self.fps = 60
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()

        self.player = Player([290,290])
        self.flags = []
        self.create_flags()
        self.flagsObject = pygame.sprite.Group()


    def create_flags(self):
        flagObj = Flag([30,30])
        self.flags.append(flagObj)
        self.flagsObject.add(flagObj)


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
        self.direction = pygame.K_RIGHT

    def run(self):
        if self.direction != None:
            for i in range(2):  
                if self.direction == self.move[i]:  
                    self.rect.x += self.vx * [-1, 1][i]  

                elif self.direction == self.move[2:4][i]:  
                    self.rect.y += self.vy * [-1, 1][i]
    

class Flag(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([60,60])
        self.rect = self.image.get_rect()
        self.image.fill((128,255,128))
        self.rect.center = position

