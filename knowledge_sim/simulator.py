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
    def init(cls, ontology_uri=None, agent_class=None, behavior_class=None, simulator_agent=None, simulate=None):
        cls.__instance = Simulator(
            ontology_uri,
            agent_class,
            behavior_class,
            simulator_agent,
            simulate
        )

    @classmethod
    def behavior(cls, uri):
        def behavior_wrapper(func):
            Behavior.add(uri, func)
            @wraps(func)
            def decorator_method(*args, **kwargs):
                if cls.__instance is None:
                    raise Exception('Simulator not initialized')
                
                kwargs['simulator'] = cls.__instance
                return_value = func(*args, **kwargs)
                return return_value
            
            return decorator_method

        return behavior_wrapper

    @classmethod
    def run(cls, until=100):
        Behavior.sync(cls.__instance)
        cls.__instance.env.run(until=until)

    
    def __init__(self, ontology_uri=None, agent_class=None, behavior_class=None, simulator_agent=None, simulate=None):
        self.reasoner = Reasoner(ontology_uri)
        self.call_stack = []

        self.behavior_class = self.reasoner.onto[behavior_class]
        self.simulator = self.reasoner.onto[simulator_agent]
        self.simulate = self.reasoner.onto[simulate]

        self.env = simpy.Environment()        
        self.action = self.env.process(self.__run())
        self.agents = simpy.FilterStore(self.env)

        agents = list(self.reasoner.onto[agent_class].instances())
        for agent in agents:
            self.agents.put(agent)

        self.agents.put(self.simulator)
        
    def push(self, states):
        self.call_stack += states

    def sync_reasoner(self):
        self.reasoner.sync_reasoner()

    @property
    def ontology(self):
        return self.reasoner.onto
                
    def __run(self):
        initial_state = State(self.simulate, self.simulator)
        self.push([initial_state])
        yield self.env.process(initial_state(self))

