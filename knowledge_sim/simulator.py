import simpy
import sys
from .ontology import Reasoner, Behavior


class Simulator:
    """
    Manages Clock tics and state transistions

    """
    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = Simulator()

        return cls.__instance

    def __init__(self, ontology_uri=None):
        self.reasoner = Reasoner(ontology_uri)
        self.behavior = Behavior(self.reasoner)

        # self.simulations = list(self.__simulator.simulates)

        # self.env = simpy.Environment()
        # self.action = self.env.process(self.__run())
        # self.agents = simpy.FilterStore(self.env)
        # self.agent_perform = self.reasoner.onto.Simulation.agentPerform[0]
        # self.get_process_agent = self.reasoner.onto.Simulation.getProcessAgent[0]

        # agents = list(self.reasoner.onto.Simulation.agentClass[0].instances())
        # for agent in agents:
        #     self.agents.put(agent)

        # self.run = self.env.run
        
    def simulate(self):

        agents = self.reasoner.onto.simulator
        behavior = self.reasoner.onto.simulate

        args = (behavior, agents)
        call_stack = [args]
        prev_calls = []

        while len(call_stack):
            next_call = call_stack[0]
            prev_calls += [next_call]
            call_stack = call_stack[1:]
            return_value = self.behavior.perform(*next_call)

            if return_value is None:
                return prev_calls, call_stack

            call_stack += return_value
            
        return prev_calls
                
    def __run(self):
        for process in self.entrypoint:
            try:
                get_agent = getattr(process, self.get_process_agent)
            except AttributeError:
                print(f"{self.get_process_agent} not defined")
            
            agent = yield self.agents.get(lambda t: t == get_agent(self))
            
            print(f"Recieved process {process.name}, starting tasks")
            try:
                perform = getattr(agent, self.agent_perform)
            except AttributeError:
                print(f"{self.agent_perform} not defined")
                
            yield self.env.process(perform(process, self))
