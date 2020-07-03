import simpy
import sys
from functools import wraps
from .ontology import Reasoner, Behavior, State


class Simulator:
    __instance = None

    @classmethod
    def get_instance(cls, ontology_uri=None):
        if cls.__instance is None:
            cls.__instance = Simulator(ontology_uri)

        return cls.__instance

    @classmethod
    def behavior(cls, api):
        def behavior_wrapper(func):
            Behavior.add(api, func)
            
            @wraps(func)
            def decorator_method(*args, **kwargs):
                if cls.__instance is None:
                    raise Exception('Simulator not initialized')
                
                kwargs['simulator'] = cls.__instance

                return_value = func(*args, **kwargs)

                return return_value
            return decorator_method

        return behavior_wrapper

    
    def __init__(self, ontology_uri=None):
        self.reasoner = Reasoner(ontology_uri)
        self.call_stack = []
        self.env = simpy.Environment()
        self.action = self.env.process(self.__run())
        self.agents = simpy.FilterStore(self.env)

        agents = list(self.reasoner.onto.Simulation.agentClass[0].instances())
        for agent in agents:
            self.agents.put(agent)

        self.agents.put(self.reasoner.onto.simulator)

    def run(self, until=100):
        Behavior.sync(self)
        self.env.run(until=until)
        
    def push(self, states):
        self.call_stack += states

    def sync_reasoner(self):
        self.reasoner.sync_reasoner()

    @property
    def ontology(self):
        return self.reasoner.onto
                
    def __run(self):
        agent = self.reasoner.onto.simulator
        behavior = self.reasoner.onto.simulate

        initial_state = State(behavior, agent)
        self.push([initial_state])

        while len(self.call_stack):
            next_state = self.call_stack[0]
            self.call_stack = self.call_stack[1:]
            yield self.env.process(next_state(self))

