#!/usr/bin/python
# Phillip Chu
# Programming Assignment 1 - nfa2dfa converter
# COSC 461 - Compilers Fall 2020
# September 1st, 2020
# Dr. Michael Jantz

import sys
import copy

class NFA:
    def __init__(self):
        self.init_state = 0
        self.final_states = []
        self.total_states = 0
        self.input_list = []
        self.states = []

    # Reads in the NFA information from stdin and stores it into the NFA class
    def build_nfa(self, lines):
        self.init_state = lines[0].split(':')[1].strip()
        self.init_state = int(self.init_state)
        self.init_state -= 1

        self.final_states = lines[1].split(':')[1].replace('{', '').replace('}', '')
        self.final_states = self.final_states.split(',')
        self.final_states = map(int, self.final_states)
        self.final_states = [x - 1 for x in self.final_states]

        self.total_states = lines[2].split(':')[1].strip()

        self.input_list = lines[3].split()
        self.input_list.remove("State")

        for i in range(int(self.total_states)):
            self.states.append({})

        for i in range(4, len(lines)):
            line = lines[i].split()
            index = int(line[0])
            del line[0]
            for j in range(len(line)):
                if line[j] != "{}":
                    target_states = line[j]
                    target_states = target_states.replace('{', '')
                    target_states = target_states.replace('}', '')
                    target_states = target_states.split(',')
                    target_states = map(int, target_states)
                    target_states = [x - 1 for x in target_states]
                    self.states[index - 1].update({self.input_list[j] : target_states})

        print("reading NFA ... done.\n")

class DFA:
    def __init__(self):
        self.init_state = 0
        self.input_list = []
        self.Dtransitions = []
        self.Dtable = []
        self.final_states = []

    # Returns all states that are reachable from s on input E
    def e_closure(self, states, s):
        stack = []
        e = []

        # Checks if s is a single state or list of states
        if type(s) == list:
            for i in range(len(s)):
                e.append(s[i])
                stack.append(s[i])
        else:
                e.append(s)
                stack.append(s)

        # Loops while there are still states reachable on input E
        while stack:
            cur_state = stack.pop()
            if type(cur_state) != int:
                cur_state = int(cur_state)
            if states[cur_state].has_key('E'):
                for target in states[cur_state]['E']:
                    if not e.count(target):
                        e.append(target)
                        stack.append(target)
        return e

    # Takes a list of states and returns a set of states that can be reached on a certain input
    def move(self, states, T, input):
        stack = []
        move_set = []

        for i in range(len(T)):
            stack.append(T[i])


        # While there states that haven't been checked
        while stack:
            cur_state = stack.pop()
            if not isinstance(cur_state, int):
                cur_state = int(cur_state)
            # Check for states reachable on input and if they have not been visited, and them to the stack
            if input in states[cur_state]:
                for target in states[cur_state][input]:
                    if not move_set.count(target):
                        move_set.append(target)
        return move_set

    # Traverses the NFA states and builds the DFA states and their transitions
    def build_dfa_from_nfa(self, nfa):
        print("creating corresponding DFA ...")

        self.init_state = nfa.init_state 
        self.input_list = nfa.input_list
        self.input_list.remove('E')
        self.nfa_states = nfa.states

        visited = []
        queue = []

        # Initialize queue with first DFA state
        init = self.e_closure(nfa.states, nfa.init_state)
        queue.append(init)
        visited.append(init)
        self.Dtransitions.append({})
        self.Dtable.append({})
        self.final_states.append([])

        # Loops while there are still states DFA states to visit
        while queue:
            T = queue.pop(0) 
            for state in T:
                for input in self.input_list:
                    if input in nfa.states[int(state)]:
                        # Generate set of all states reachable by an episilon and the specified input
                        U = self.e_closure(nfa.states, self.move(nfa.states, T, input))
                        U.sort()
                        # Store U on the stack if has not been visited before
                        if not visited.count(U):
                            queue.append(U)
                            visited.append(U)
                            self.Dtransitions.append({})
                            self.Dtable.append({})
                            self.final_states.append([])

                        # Set transition for current state
                        self.Dtransitions[visited.index(T)][input] = U
                        self.Dtable[visited.index(T)][input] = visited.index(U)

        # Store a list of the final states
        for i in range(len(visited)):
            for fstate in nfa.final_states:
                if fstate in visited[i]:
                    self.final_states[i] = visited[i]

        return visited
    
    # Prints out the new DFA states generated from the old NFA states
    def print_corresponding_states(self, visited):
        for i in range(len(visited)):
            temp_list = [x + 1 for x in visited[i]]
            temp_list.sort()
            string = str(temp_list).replace('[', '{').replace(']', '}')
            print "new DFA state: ", i + 1, "  --> ", string
        print("done.\n")

    # Prints the full DFA
    def print_DFA(self, visited):
        index_list = []
        for i in range(len(self.final_states)):
            if self.final_states[i]:
                index_list.append(i)
        index_list = [x + 1 for x in index_list]

        print "final DFA:"
        print "Initial State: ", self.init_state + 1

        string = str(index_list).replace('[', '{').replace(']', '}')
        print "Final States: ", string 

        print "Total States: ", len(visited)

        state_list = copy.deepcopy(self.input_list)
        state_list.insert(0, "State")
        for element in state_list:
            print "{:<8}".format(element), 
        print '\n',

        for i in range(len(visited)):
            temp_list = [i + 1]
            for input in self.input_list:
                if input in self.Dtable[i]:
                    temp_list.append(self.Dtable[i][input] + 1)
                else:
                    temp_list.append(' ')
            for element in temp_list:
                print "{:<8}".format(element),
            print '\n',

def main():
    nfa = NFA()
    dfa = DFA()

    # Read in nfa from stdin
    lines = sys.stdin.readlines()
    nfa.build_nfa(lines)
    
    # Construct and print dfa
    visited = dfa.build_dfa_from_nfa(nfa)
    dfa.print_corresponding_states(visited)
    dfa.print_DFA(visited)
    
if __name__ == "__main__":
    main()
            
