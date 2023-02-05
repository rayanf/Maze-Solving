from board import Board
import random
import numpy as np

walk_punishment = -1/100
flag_reward = 1/7
target_reward = None
back_punishment = 0
been_punishment = -2/100
alpha = 0.2
gamma = 0.3

step_treshhold = 20
iters = 0

name = 'normilize_test'

def play(iters):
    game = Board(walk_punishment,flag_reward,target_reward,back_punishment,been_punishment,alpha,gamma)
    game.reset(iters)
    
    game.resetQtable(name)
    
    # game.loadQtable()
    agent = Agent(game)

    
    step = 0
    while True:
        step += 1 

        state = agent.get_state()
        choices = agent.get_choices(state)        
        action = agent.make_action(state,choices,iters)
        flag,target = game.run(action,step,iters)
        
        if flag :
            step -= 15
            
        if target:
            step = -np.NINF
        if step > step_treshhold:
            iters += 1
            game.saveQtable(name)
            game.reset(iters)
            step = 0

    

def printQtable(qTable):
    Qtable = np.loadtxt('{}.txt'.format(qTable))
    Qtable = Qtable.reshape(10,10,4)

    for i in range(10):
        for j in range(10):
            print('({},{})'.format(i,j),end=' ')
            print(Qtable[i][j])
        print()

class Agent:
    def __init__(self,game):
        self.game = game
        self.qTable = None
        self.choices = ['left','up','right','down']

    def get_state(self):
        cords = self.game.player.rect.center
        i = (cords[0] - 30) // 60
        j = (cords[1] - 30) // 60
        return self.game.nodes[j][i]
    
    def get_choices(self,state):
        i = state.j
        j = state.i
        choices = ['left','up','right','down']
        if j == 0:
            choices.remove('left')
        elif j == 9:
            choices.remove('right')
        if i == 0:
            choices.remove('up')
        elif i == 9:
            choices.remove('down')

        if i > 0 and self.game.nodes[i-1][j].type == 'block':
            try:
                choices.remove('up')
            except:
                pass
        if i < 9 and self.game.nodes[i+1][j].type == 'block':
            try:
                choices.remove('down')
            except:
                pass
        if j > 0 and self.game.nodes[i][j-1].type == 'block':
            try:
                choices.remove('left')
            except:
                pass
        if j < 9 and self.game.nodes[i][j+1].type == 'block':
            try:
                choices.remove('right')
            except:
                pass

        return choices
 
 
    def make_action(self,state,choices,iters):
        if random.randint(0,500) < 200 - iters:
            action = random.choice(choices)
        else:
            actionChoices = [0 for i in range(4)]
            if 'left' in choices:
                actionChoices[0] = 1
            if 'up' in choices:
                actionChoices[1] = 1
            if 'right' in choices:
                actionChoices[2] = 1
            if 'down' in choices:
                actionChoices[3] = 1

            q = state.q
            
            for i in range(4):
                if actionChoices[i] == 0:
                    q[i] = np.NINF

            action = self.choices[np.argmax(q)]

        return action

def generate_random_env():
    env = np.ones((10,10),dtype=int)
    for i in range(10):
        for j in range(10):
            if i == j == 0 or i == j == 9:
                continue

            if random.randint(0,100) < 10:
                env[i][j] = 3
            elif random.randint(0,100) < 7:
                env[i][j] = 2
    env[9][9] = 4

    return env

if __name__ == "__main__":
    play(iters)
    # printQtable('Qtable')
