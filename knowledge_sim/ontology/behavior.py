import types
import sys
import importlib

class Behavior:
    def __init__(self, reasoner):
        self.behavior = {}
        self.reasoner = reasoner
        self.behavior_class = self.reasoner.onto.Simulation.behaviorClass[0]
        self.behavior_predicate = self.reasoner.onto.Simulation.behaviorPredicate[0]

        api_path = reasoner.onto.Simulation.apiPath[0]
        sys.path.append(api_path)
    
        self.init()
        # self.sync_all()
        
    def perform(self, behavior, agent, *args, **kwargs):
        function = self.behavior.get(behavior)

        if function is None:
            return None

        return_args = function(agent, *args, **kwargs)

        if behavior.triggers:
            behavior = behavior.triggers[0]
            return [(behavior, *args) for args in return_args]

        return return_args
    
    def __get_api(self, api_string):
        api_tree = api_string.split('.')
        api_module = importlib.import_module(api_tree[0])

        for comp in api_tree[1:]:
            api_module = getattr(api_module, comp)

        return api_module

    def init(self):
        self.reasoner.sync_reasoner()
        for behavior in self.behavior_class.instances():
            if behavior.type == "api":
                api = behavior.__api__
                self.behavior[behavior] = self.__get_api(api)
                
    
    def sync_all(self):
        pass
        self.reasoner.sync_reasoner()

        for subject_, object_ in self.behavior_predicate.get_relations():
            self.sync(subject_, object_)            
        

    def sync(self, instance, behavior = None):
        behaviors = [behavior] if behavior is not None else self.behavior_predicate[instance]
        for behavior in behaviors:
            function  = behavior.name
            method_def = self.behavior.get(behavior.name, None)
                
            if method_def is not None:
                setattr(instance, function, types.MethodType(method_def, instance))

                # raise Exception(f"Method not found {behavior.name}")

            
