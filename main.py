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


def play(iters,name):
    """
        this function is the main function of the game and it is responsible for the game loop and training the agent
    Args:
        iters (int): number of iterations that agent has been trained
        name (str): name of the Qtable file
    """


    # game is the object of the class Board which is responsible for the game logic and visualise the board
    game = Board(walk_punishment,flag_reward,target_reward,back_punishment,been_punishment,alpha,gamma)
    
    # game reset function is responsible for reseting the game's attr
    game.reset(iters)
    
    # this function is responsible for creating the zeros Qtable. if we want to train agent from first place
    # game.resetQtable()
    
    # this function is responsible for loading the Qtable from the file. if we want to train agent from the last place
    # game.loadQtable()

    # agent is the object of the class Agent which is responsible for the agent's actions and choices
    agent = Agent(game)

    
    # steps is variable that is responsible for the number of steps that agent has been moved in this iteration
    step = 0
    # main loop of code that is responsible for the training agent for infinite times
    while True:
        step += 1 

        state = agent.get_state()
        choices = agent.get_choices(state)        
        action = agent.make_action(state,choices,iters)
        flag,target = game.run(action,step,iters)
        
        # if agent has been moved to the flag then it could move 15 more step in this iteration
        if flag :
            step -= 15
        
        # if agent has been moved to the target then it game should be reset
        if target:
            step = -np.NINF
        # agent's step never should be more than 20. for avoiding infinite loop 
        if step > step_treshhold:
            iters += 1
            game.saveQtable(name)
            game.reset(iters)
            step = 0


'''
    this function is responsible for printing the Qtable
'''
def printQtable(qTable):
    Qtable = np.loadtxt('{}.txt'.format(qTable))
    Qtable = Qtable.reshape(10,10,4)

    for i in range(10):
        for j in range(10):
            print('({},{})'.format(i,j),end=' ')
            print(Qtable[i][j])
        print()

# Class for agent. responsible for agent's actions and choices
class Agent:
    def __init__(self,game):
        self.game = game
        self.qTable = None
        self.choices = ['left','up','right','down']

    # this function is responsible for getting the state that agent is in. state is the board at the moment
    def get_state(self):
        cords = self.game.player.rect.center
        i = (cords[0] - 30) // 60
        j = (cords[1] - 30) // 60
        return self.game.nodes[j][i]

    # return the possible choices that agent can move 
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
 
    # this function is responsible for making the action for agent. it is responsible for choosing the best action recording to the Qtable
    # or move randomly for exploring the environment
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

# this function is responsible for generating the random environment and board for task assignment
def generate_random_env():
    env = np.ones((10,10),dtype=int)
    for i in range(10):
        for j in range(10):
            if i == j == 0 or i == j == 9:
                continue

            if random.randint(0,100) < 20:
                env[i][j] = 3
            elif random.randint(0,100) < 7:
                env[i][j] = 2
    env[9][9] = 4

    return env

# this function is responsible for training the agent for random environment for task assignment
def train_random(iters,board,randomName):
    game = Board(walk_punishment,flag_reward,target_reward,back_punishment,been_punishment,alpha,gamma,board)
    game.reset(iters,board)
    
    game.resetQtable(randomName)
    
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
            game.saveQtable(randomName)
            game.reset(iters,board)
            step = 0

    


if __name__ == "__main__":

    # board = generate_random_env()
    # train_random(iters,board,'random')
    play(iters,'Qtable')
    printQtable('Qtable')
