from knowledge_sim import Simulator, State

def get_next_tasks(task):
    return [State(next_task.definedBy, next_task.assignedTo, next_task, next_task.timeToComplete) for next_task in list(task.hasTask)]

@Simulator.behavior('api://collab_bot/behavior/addToContainable')
def add_to_containable(manager, task, simulator=None, *args, **kwargs):
    ontology = simulator.ontology
    entity = task.entity
    print(entity, task.params, manager.manages[0])
    setattr(entity, task.params, manager.manages[0])

    simulator.sync_reasoner()
    task.done = True

    return get_next_tasks(task)

@Simulator.behavior('api://collab_bot/behavior/createAssembly')
def create_assembly(factory_manager, task, simulator=None, *args, **kwargs):
    ontology = simulator.ontology
    
    assembly_type = ontology[task.params]
    parts = task.parts

    assembly = assembly_type()
    for part in parts:
        part.partOf = assembly
        
    simulator.sync_reasoner()
    for next_tasks in task.hasTask:
        next_tasks.entity = assembly
    task.done = True
    return get_next_tasks(task)

@Simulator.behavior('api://collab_bot/behavior/createBot')
def create_bot(factory_manager, task, simulator=None, *args, **kwargs):
    ontology = simulator.ontology
    
    bot_type = ontology[task.params]
    assemblies = task.assemblies

    bot = bot_type()
    for assembly in assemblies:
        assembly.assemblyOf = bot

    simulator.sync_reasoner()
    
    for next_tasks in task.hasTask:
        next_tasks.entity = bot
    task.done = True
    return get_next_tasks(task)


@Simulator.behavior('api://collab_bot/behavior/fetchAssemblies')    
def fetchAssemblies(inventoryManager, task, simulator=None, *args, **kwargs):
    dependent_tasks = task.taskDependsOn
    if not all(dep_task.done for dep_task in dependent_tasks):
        return State.WAIT
    
    if task.done:
        return State.NILL
    
    queries = task.query
    namespace = task.name_space
    query_result = [simulator.reasoner.run_query(query, namespace) for query in queries]
    assemblies = [result[0] for results in query_result for result in results]
    
    for next_tasks in task.hasTask:
        next_tasks.assemblies = assemblies
    task.done = True
    return get_next_tasks(task)


@Simulator.behavior('api://collab_bot/behavior/fetchParts')    
def fetchParts(inventoryManager, task, simulator=None, *args, **kwargs):
    queries = task.query
    namespace = task.name_space
    query_result = [simulator.reasoner.run_query(query, namespace) for query in queries]
    parts = [result[0] for results in query_result for result in results]
    
    for next_tasks in task.hasTask:
        next_tasks.parts = parts
    task.done = True
    return get_next_tasks(task)


def factory_manager_perform(actor, task, *args, **kwargs):
    return [State(task.definedBy, task.assignedTo, task)]

def inventory_manager_perform(actor, task, *args, **kwargs):
    return [State(task.definedBy, task.assignedTo, task)]

@Simulator.behavior('api://collab_bot/behavior/perform')    
def perform(actor, executable, *args, **kwargs):
    agent_type = actor.is_a[0].name
    agent_perform = {
        'FactoryManager': factory_manager_perform,
        'InventoryManager': inventory_manager_perform
    }

    return agent_perform[agent_type](actor, executable)

def mother_ship_execute(agent, mission):
    return get_next_tasks(mission)

@Simulator.behavior('api://collab_bot/behavior/execute')
def execute(actor, executable, *args, **kwargs):
    agent_type = actor.is_a[0].name
    agent_perform = {
        'Orchestrator': mother_ship_execute
    }
    
    return agent_perform[agent_type](actor, executable)

@Simulator.behavior('api://collab_bot/behavior/assignExecutable')    
def assignExecutable(simulator_agent, simulation, *args, **kwargs):
    return [State(mission.definedBy, mission.assignedTo, mission, mission.timeToComplete) for mission in list(simulation.hasMissions)]
    
@Simulator.behavior('api://collab_bot/behavior/simulate')
def simulate(simulator_agent,  *args, **kwargs):
    behavior = kwargs['behavior']
    return [State(behavior.triggers[0], simulator_agent, simulation) for simulation in list(simulator_agent.simulates)]

def main():
    Simulator.init(
        ontology_uri="./kb_owl_v3.owl",
        agent_class="Actor",
        behavior_class="Behavior",
        uri_property="uri",
        simulator_agent="simulator",
        simulate="simulate"
    )
    
    Simulator.run(until = 100)
    simulator = Simulator.get_instance()
    oo = simulator.ontology
    oo.save('./temp2.owl')

if __name__ == '__main__':
    main()
