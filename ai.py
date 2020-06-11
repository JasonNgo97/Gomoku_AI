from __future__ import absolute_import, division, print_function
from math import sqrt, log
from game import Game, WHITE, BLACK, EMPTY
import copy
import time
import random
import pdb


PLAYER_INDEX = 0
GRID_INDEX = 1
ROW_INDEX = 0
COL_INDEX = 1
class Node:
    # NOTE: modifying this block is not recommended
    def __init__(self, state, actions, parent=None):
        self.state = (state[0], copy.deepcopy(state[1]))
        self.num_wins = 0 #number of wins at the node
        self.num_visits = 0 #number of visits of the node
        self.parent = parent #parent node of the current node
        self.children = [] #store actions and children nodes in the tree as (action, node) tuples
        self.untried_actions = copy.deepcopy(actions) #store actions that have not been tried
        self.parent_action = None
        self.isTerminal = False

# NOTE: deterministic_test() requires BUDGET = 1000
#   You can try higher or lower values to see how the AI's strength changes
BUDGET = 1000

class AI:
    # NOTE: modifying this block is not recommended
    def __init__(self, state):
        self.simulator = Game()
        self.simulator.reset(*state) #using * to unpack the state tuple
        self.root = Node(state, self.simulator.get_actions())

    def mcts_search(self):
        #TODO: Main MCTS loop


        action_win_rates = {} #store the table of actions and their ucb values

        # TODO: Delete this block ->
       # self.simulator.reset(*self.root.state)
       # for action in self.simulator.get_actions():
       #     action_win_rates[action] = 0
       # return random.choice(self.simulator.get_actions()), action_win_rates
        # <- Delete this block

        # TODO: Implement the MCTS Loop

        iters = 0
        while(iters < BUDGET):
            if ((iters + 1) % 100 == 0):
                # NOTE: if your terminal driver doesn't support carriage returns
                #   you can use: print("{}/{}".format(iters + 1, BUDGET))
                print("\riters/budget: {}/{}".format(iters + 1, BUDGET), end="")
                #pdb.set_trace()
            self.updateMCT(self.root)
            iters += 1
            # TODO: select a node, rollout, and backpropagate
        print()

        # Note: Return the best action, and the table of actions and their win values 
        #   For that we simply need to use best_child and set c=0 as return values
        _, action, action_win_rates = self.best_child(self.root, 0)
        return action, action_win_rates

    def updateMCT(self,node):

        self.simulator.reset(*self.root.state)
        node_to_simulate = self.select(self.root)
        reward = self.rollout(node_to_simulate)
        self.backpropagate(node_to_simulate,reward)




    def select(self, node):
        # TODO: select a child node

        # while node is not None: #As explained in Slack, ignore this line and follow pseudocode
        # NOTE: deterministic_test() requires using c=1 for best_child()
        #
        curr_node = node
        c = 1
        count = 0
        while curr_node.isTerminal == False : #Iterate until there is a leaf node
           if len(curr_node.untried_actions) != 0: #There are nodes that haven't been expanded yet
              new_child = self.expand(curr_node)
              return new_child
           else: #Pick the best child to traverse
               curr_node,best_action,ucb_table = self.best_child(curr_node,c) #Choose the best child
               count += 1
        return curr_node

    def expand(self, node):
        # TODO: add a new child node from an untried action and return this new node

        #child_node = None #choose a child node to grow the search tree
        # This node has been already expanded
        if len(node.untried_actions) == 0:
            return None
        else:
            action = node.untried_actions.pop(0)
            old_state = self.simulator.state()
            self.simulator.reset(node.state[PLAYER_INDEX],node.state[GRID_INDEX])
            self.simulator.place(action[ROW_INDEX],action[COL_INDEX])
            new_state = self.simulator.state()
            possible_actions = self.simulator.get_actions()
            child_node = Node(new_state,possible_actions,node)
            node.children.append((action,child_node))
            #self.simulator.reset(old_state[0],old_state[1])
            return child_node

            #Here, we reset the simulator
            # #This line is not really necessary
        # Get child that has not been expanded
        # IMPORTANT: use the following method to fetch the next untried action
        #   so that the order of action expansion is consistent with the test cases
        #action = node.untried_actions.pop(0)

        # NOTE: Make sure to add the new node to the node.children
        # NOTE: You may find the following methods useful:
        #   self.simulator.state()
        #   self.simulator.get_actions()

        #return child_node

    def best_child(self, node, c): 
        # TODO: determine the best child and action by applying the UCB formula

        best_child_node = None #store the best child node with UCB
        best_val = 0
        best_action = None #store the action that leads to the best child
        action_ucb_table = {} #store the UCB values of each child node (for testing)
        for child in node.children:
            #Compute value and append to table
            child_node = child[1]
            child_action = child[0]
            val = self.computeUCB(child_node,c)
            action_ucb_table[child_action] = val

            if best_child_node == None:
                best_child_node = child_node
                best_val = val
                best_action = child_action
            else:
                if val > best_val:
                    best_val = val
                    best_child_node = child_node
                    best_action = child_action

        return best_child_node, best_action, action_ucb_table

    def backpropagate(self, node, result):
        curr_node = node
        #print("Result: ",result)
        while (curr_node != None):
            # TODO: backpropagate the information about winner
            # IMPORTANT: each node should store the number of wins for the player of its **parent** node
            player_type = curr_node.state[PLAYER_INDEX]
            if result[player_type] == 0:
                curr_node.num_wins += 1
                curr_node.num_visits += 1
            else:
                curr_node.num_visits += 1
            curr_node = curr_node.parent


    def computeUCB(self,node,c=1):
        sum_to_return = 0
       # print("Num Wins ",node.num_wins," Num Visits: ",node.num_visits)
        if node.num_visits != 0:
            sum_to_return += node.num_wins/node.num_visits
            sum_to_return += c*sqrt(2*log(node.parent.num_visits)/node.num_visits)
        return sum_to_return


    def rollout(self, node):
        # TODO: rollout (called DefaultPolicy in the slides)

        # NOTE: you may find the following methods useful:
        #   self.simulator.reset(*node.state)
        #   self.simulator.game_over
        #   self.simulator.rand_move()
        #   self.simulator.place(r, c)

        # You have to do a deep copy because the simulator is going to change state
        starting_state = self.simulator.state()
        starting_player = starting_state[PLAYER_INDEX]
        starting_state = copy.deepcopy(starting_state[GRID_INDEX])


        curr_state = node.state
        self.simulator.reset(*curr_state)

        #The game is over at this instance
        if self.simulator.game_over == True:
            node.isTerminal = True

        #It is not over, hence keep iterating
        while self.simulator.game_over == False:
            action = self.simulator.rand_move()
            self.simulator.place(action[0],action[1])
        # Determine reward indicator from result of rollout
        reward = {}
        if self.simulator.winner == BLACK:
            reward[BLACK] = 1
            reward[WHITE] = 0
        elif self.simulator.winner == WHITE:
            reward[BLACK] = 0
            reward[WHITE] = 1
        #self.simulator.reset(starting_player,starting_state)
        return reward
