from pysat.formula import CNF
from pysat.solvers import Solver

class KnowledgeBase:
    entity = {
            'W': 1,     #Wumpus 
            'P': 2,     #Pit
            'P_G': 3,   #Poisonous Gas
            'H_P': 4,   #Healing Potion
            'B': 5,     #Breeze
            'S': 6,     #Stench
            'W_H': 7,   #Whiff
            'G_L': 8,   #Glow
            'G': 9      #Gold
        }
    def __init__(self, map_size):
        self.KB = CNF()
        self.size = map_size
        self.initialize_kb_relations()
        
    @staticmethod
    def symbol(entity, x, y):
        if x == 10:
            x = 0
        if y == 10:
            y = 0
        return KnowledgeBase.entity[entity] * 100 + x * 10 + y
        
    def initialize_kb_relations(self):
        # No Wumpus, Pit, Poisonous Gas, or Healing Potion at the beginning
        self.KB.append([-KnowledgeBase.symbol('W', 1, 1)])
        self.KB.append([-KnowledgeBase.symbol('P', 1, 1)])
        self.KB.append([-KnowledgeBase.symbol('P_G', 1, 1)])
        self.KB.append([-KnowledgeBase.symbol('H_P', 1, 1)])
        
        # Pit-Breeze, Wumpus-Stench, Poisonous Gas-Whiff, Healing Potion-Glow rules for each cell
        percepts = {
            'W': 'S',
            'P': 'B',
            'P_G': 'W_H',
            'H_P': 'G_L'
        }
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                for trigger, percept in percepts.items():
                    percept_symbol = KnowledgeBase.symbol(percept, i, j)
                    adjacent_trigger = []
                    if i > 1:  # Up
                        adjacent_trigger.append(KnowledgeBase.symbol(trigger, i-1, j))
                    if i < self.size:  # Down
                        adjacent_trigger.append(KnowledgeBase.symbol(trigger, i+1, j))
                    if j < self.size:  # Right
                        adjacent_trigger.append(KnowledgeBase.symbol(trigger, i, j+1))
                    if j > 1:  # Left
                        adjacent_trigger.append(KnowledgeBase.symbol(trigger, i, j-1))

                    # Px,y => (Tx+1,y v Tx-1,y v Tx,y+1 v Tx,y-1)
                    self.KB.append([-percept_symbol] + adjacent_trigger)
                    
                    # (Tx,y+1 v Tx,y-1 v Tx+1,y v Tx-1,y) => Px,y
                    for trigger_symbol in adjacent_trigger:
                        self.KB.append([percept_symbol, -trigger_symbol])


    def add_clause(self, clause):
        self.KB.append(clause)
    
    def query(self, entity, x, y):
        with Solver(bootstrap_with=self.KB) as solver:
            entity_symbol = self.symbol(entity, x, y)
            
            solver.solve(assumptions=[entity_symbol])
            entity_possible = solver.get_model() is not None
            
            solver.solve(assumptions=[-entity_symbol])
            no_pit_possible = solver.get_model() is not None
            
            if entity_possible and not no_pit_possible:
                return 'exists'
            if not entity_possible and no_pit_possible:
                return 'not exists'
            if entity_possible and no_pit_possible:
                return 'unknown'
            
        return 'inconsistent'
    
    def removeall_clause(self, clause):
        new_kb = CNF()
        for cl in self.KB:
            if cl != clause:
                new_kb.append(cl)
        self.KB = new_kb
    
    def remove_clause(self, clause):
        new_kb = CNF()
        removed = False
        for cl in self.KB:
            if cl == clause and not removed:
                removed = True
            else:
                new_kb.append(cl)
        self.KB = new_kb