from owlready2 import *
from functools import reduce
import os
import rdflib

class Reasoner:
    """
    Class used to obtain the type of bot for the specified type of activity
    """
    path = os.path.dirname(os.path.abspath(__file__))
    ontology_file = 'kb_owl.owl'

    __instance = None
    rule_chains = {
        'Bot': ['hasAssembly', 'hasSkill'],
        'Assembly': ['hasSkill']
    }

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = Reasoner()

        return cls.__instance
    
    def __init__(self, ontology_uri=None):
        ontology_uri = ontology_uri if ontology_uri is not None else f'file://{self.path}/{self.ontology_file}'
        self.onto = get_ontology(ontology_uri)
        self.onto.load()

        self.graph = default_world.as_rdflib_graph()


    def dl_chain_rule(self, predicate, rules):
        if len(rules):
            current_predicate = self.onto[rules[0]].some
            return lambda prop, entity: predicate(
                self.dl_chain_rule(current_predicate, rules[1:])(prop, entity)
            )

        return lambda prop, entity: predicate(self.onto[prop].value(self.onto[entity]))

    def chained_equivalent_to(self, parent, rule_chain, **args):
        predicate = self.dl_chain_rule(
            lambda x: x, rule_chain
        )
        
        return [reduce(
            lambda acc, val: acc & predicate(val[0], val[1]),
            args.items(),
            self.onto[parent]
        )]
                
    def types(self, parent, rule_chain=None, map_transform=None, **args):
        if rule_chain is None:
            rule_chain = self.rule_chains.get(parent, [])

        restrictions = self.chained_equivalent_to(parent, rule_chain, **args)

        return self.get_schema(restrictions, map_transform)

    def add_rule(self, rules):
        if type(rules) != list:
            raise Exception(f"List expected, got {type(rules)}")

        with self.onto:
            for rule in rules:
                swrl_rule = Imp()
                swrl_rule.set_as_rule(rule)

            sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)

    def get_schema(self, restrictions, map_transform):
        with self.onto:
            class TypeTemplate(owl.Thing):
                equivalent_to = restrictions
                
            sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)

        types = list(self.onto.TypeTemplate.subclasses()) + self.onto.TypeTemplate.equivalent_to[1:]
        
        try:
            destroy_entity(self.onto.TypeTemplate)
        except:
            pass

        return map(map_transform, types) if map_transform else types

    def sync_reasoner(self):

        with self.onto:
            sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)


    def run_query(self, query, namespace):
        return  list(self.graph.query_owlready(query, initNs={namespace: rdflib.URIRef(self.onto.base_iri)}))
