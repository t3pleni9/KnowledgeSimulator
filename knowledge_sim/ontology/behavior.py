class Behavior:
    __behaviors = {}

    @classmethod
    def add(cls, api, function):
        cls.__behaviors[api] = Behavior(function)
    
    @classmethod
    def sync(cls, simulator):
        reasoner = simulator.reasoner
        reasoner.sync_reasoner()
        behavior_class = reasoner.onto.Simulation.behaviorClass[0]
        for behavior in behavior_class.instances():
            if behavior.type == "api":
                api = behavior.__api__
                
                api_behavior = cls.__behaviors.get(api, None)
                if api_behavior is not None:
                    api_behavior.behavior = behavior
                    api_behavior.simulator = simulator
                    cls.__behaviors[behavior] = api_behavior

    @classmethod
    def perform(cls, behavior, agent, task):
        api_behavior = cls.__behaviors.get(behavior)
        if api_behavior is None:
            return None

        return api_behavior(agent, task)

    def __init__(self, function):
        self.function = function
        self.behavior = None
        self.simulator = None

    def __call__(self, *args, **kwargs):
        return self.function(
            simulator=self.simulator,
            behavior=self.behavior,
            *args, **kwargs
        )

