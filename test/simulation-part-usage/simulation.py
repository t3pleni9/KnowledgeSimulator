from knowledge_sim import Simulator, State

def get_next_tasks(task):
    return [State(next_task.definedBy, next_task.assignedTo, next_task, next_task.time_to_complete) for next_task in list(task.hasNextTask)]

@Simulator.behavior('api://collab_bot/behavior/addToContainable')
def add_to_containable(manager, task, simulator=None, *args, **kwargs):
    behavior = kwargs['behavior']
    triggeredState = []
    
    ontology = simulator.ontology
    entity = task.entity
    
    setattr(entity, task.params, manager.manages[0])
    oo = simulator.ontology


    simulator.sync_reasoner()
    task.done = True
    if behavior.triggers:
        triggeredState = [State(behavior.triggers, manager, task, 2)]
    return triggeredState +  get_next_tasks(task)

@Simulator.behavior('api://collab_bot/behavior/createAssembly')
def create_assembly(factory_manager, task, simulator=None, *args, **kwargs):
    ontology = simulator.ontology
    
    assembly_type = ontology[task.params]
    parts = task.parts

    assembly = assembly_type()
    for part in parts:
        part.partOf = assembly

    oo = simulator.ontology

    simulator.sync_reasoner()
    for next_tasks in task.hasNextTask:
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

    oo = simulator.ontology

    simulator.sync_reasoner()
    
    for next_tasks in task.hasNextTask:
        next_tasks.entity = bot
    task.done = True
    return get_next_tasks(task)


@Simulator.behavior('api://collab_bot/behavior/diagnose_health')
def diagnose_health(parking_lot_manager, task, simulator=None, *args, **kwargs):
    entity = task.entity
    ontology = simulator.ontology
    if ontology.BadBot in entity.is_a:
        behavior = kwargs['behavior']
        return [State(behavior.triggers, task.assignedTo, task)]
        
    simulator.agents.put(entity)
    return []

def get_part(part_type, simulator):
    query = 'SELECT * WHERE {?part a kb:%s. ?part kb:partOf kb:inventory.} LIMIT 1' % part_type
    namespace = 'kb'
    query_result = simulator.reasoner.run_query(query, namespace)
    return query_result[0][0]

@Simulator.behavior('api://collab_bot/behavior/repair_bot')
def repair_bot(parking_lot_manager, task, simulator=None, *args, **kwargs):
    entity = task.entity
    onto = simulator.ontology
    bad_assemblies = {assembly: [part for part in assembly.hasPart if onto.BadPart in part.is_a] for assembly in entity.hasAssembly if onto.BadAssembly in assembly.is_a}
    for assembly in bad_assemblies:
        for part in bad_assemblies[assembly]:
            
            new_part = get_part(part.is_a[0].name, simulator)
            part.partOf = None
            new_part.partOf = assembly

        assembly.is_a = [a_type for a_type in assembly.is_a if a_type != onto.BadAssembly]

    entity.is_a = [a_type for a_type in entity.is_a if a_type != onto.BadBot]
    simulator.sync_reasoner()
    task.done = True
    return get_next_tasks(task)

@Simulator.behavior('api://collab_bot/behavior/fetchAssemblies')    
def fetchAssemblies(inventoryManager, task, simulator=None, *args, **kwargs):
    dependent_tasks = task.hasPreviousTask
    if not all(dep_task.done for dep_task in dependent_tasks):
        return State.WAIT
    
    if task.done:
        return State.NILL
    
    queries = task.query
    namespace = task.name_space
    query_result = [simulator.reasoner.run_query(query, namespace) for query in queries]
    assemblies = [result[0] for results in query_result for result in results]
    
    for next_tasks in task.hasNextTask:
        next_tasks.assemblies = assemblies
    task.done = True
    return get_next_tasks(task)


@Simulator.behavior('api://collab_bot/behavior/fetchParts')    
def fetchParts(inventoryManager, task, simulator=None, *args, **kwargs):
    queries = task.query
    namespace = task.name_space
    query_result = [simulator.reasoner.run_query(query, namespace) for query in queries]
    parts = [result[0] for results in query_result for result in results]
    
    for next_tasks in task.hasNextTask:
        next_tasks.parts = parts
    task.done = True
    return get_next_tasks(task)


def factory_manager_perform(actor, task, *args, **kwargs):
    return [State(task.definedBy, task.assignedTo, task)]

def inventory_manager_perform(actor, task, *args, **kwargs):
    return [State(task.definedBy, task.assignedTo, task)]

@Simulator.behavior('api://collab_bot/behavior/allocate_to_agent')
def allocate_to_agent(parking_lot_manager, task, simulator=None, *args, **kwargs):    
    behavior = kwargs['behavior']
    queries = task.query
    namespace = task.name_space
    
    query_result = [simulator.reasoner.run_query(query, namespace) for query in queries]
    
    bots = [result[0] for results in query_result for result in results]

    if bots == []:
        return State.WAIT

    bot = bots[0]
    
    for next_tasks in task.hasNextTask:
        next_tasks.assignedTo = bot
        next_tasks.definedBy = behavior.triggers
        
    task.done = True
    return get_next_tasks(task)


@Simulator.behavior('api://collab_bot/behavior/perform_task')
def perform_task(agent, task, simulator=None, *args, **kwargs):
    behavior = kwargs['behavior']
    agent.isAvailableIn = None
    for assembly in agent.hasAssembly:
        for part in assembly.hasPart:
            new_life = part.part_life - task.time_to_complete
            part.part_life = new_life if new_life > 0 else 0

    for next_tasks in task.hasNextTask:
        next_tasks.entity = agent

    task.done = True
    simulator.sync_reasoner()
    
    return get_next_tasks(task)


@Simulator.behavior('api://collab_bot/behavior/perform')    
def perform(actor, executable, *args, **kwargs):
    agent_type = actor.is_a[0].name
    agent_perform = {
        'FactoryManager': factory_manager_perform,
        'InventoryManager': inventory_manager_perform
    }

    return agent_perform[agent_type](actor, executable)

def mother_ship_execute(agent, mission):
    mission.done = True
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
    return [State(mission.definedBy, mission.assignedTo, mission, mission.time_to_complete) for mission in list(simulation.hasMissions)]
    
@Simulator.behavior('api://collab_bot/behavior/simulate')
def simulate(simulator_agent,  *args, **kwargs):
    behavior = kwargs['behavior']
    return [State(simulation.definedBy, simulator_agent, simulation) for simulation in list(simulator_agent.simulates)]

def main():
    Simulator.init(
        ontology_uri="./kb_owl.owl",
        agent_class="Agent",
        behavior_class="Behavior",
        uri_property="uri",
        simulator="simulator",
        simulate="simulate"
    )
    
    Simulator.run(until = 100)
    simulator = Simulator.get_instance()
    oo = simulator.ontology
    oo.save('./output.owl')
    print("Simulation Done...")


if __name__ == '__main__':
    main()
