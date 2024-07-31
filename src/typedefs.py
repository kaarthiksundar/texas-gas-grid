from dataclasses import dataclass
from typing import List, Dict
from converters import vol_to_mass
import json

@dataclass 
class Params: 
    gas_constant: float 
    z_nominal: float 
    temp_nominal: float 
    pressure_nominal: float 
    temp_stp: float 
    pressure_stp: float 
    z_b1: float 
    z_b2: float 

@dataclass 
class Node: 
    id_: int 
    x_coord: float 
    y_coord: float
    min_pressure: float 
    max_pressure: float 
    slack_bool: bool 
    slack_pressure: float
    name: str 
    qf: float 
    min_qf: float 
    max_qf: float
    substation_id: int

@dataclass 
class Pipe: 
    id_: int 
    fr_node: int 
    to_node: int 
    length: float 
    friction_factor: float 
    diameter: float 
    name: str 
    q: float 
    
@dataclass 
class Compressor: 
    id_: int 
    fr_node: int 
    to_node: int 
    name: str 
    q: float 
    c_ratio: float 
    
class SteadyStateData: 
    params: Params 
    nodes: List[Node]
    pipes: List[Pipe]
    compressors: List[Compressor]
    slack_node_indices: List[int]
    
    def __init__(self, params, nodes, pipes, compressors, slack_node_indices):
        self.params = params
        self.nodes = nodes
        self.pipes = pipes
        self.compressors = compressors
        self.slack_node_indices = slack_node_indices
        
    def to_params_json(self, folder):
        params_data = {
            "params": {
                "Specific heat capacity ratio": 1.4,
                "Temperature (K):": 288.70599999999996,
                "Gas specific gravity (G):": 0.6,
                "units (SI = 0, standard = 1)": 0.0
            }
        }
        
        with open(folder + '/params.json', 'w') as fp:
            json.dump(params_data, fp, indent=2)
        return 
    
    def to_network_json(self, args, folder):
        network_data = {
            'nodes': {}, 
            'pipes': {}, 
            'compressors': {}}
        for (i, node) in enumerate(self.nodes):
            network_data['nodes'][str(node.id_)] = {
                'id': node.id_, 
                'name': node.name, 
                'x_coord': node.x_coord, 
                'y_coord': node.y_coord, 
                'min_pressure': node.min_pressure, 
                'max_pressure': node.max_pressure, 
                'slack_bool': node.slack_bool,
                'min_withdrawal': vol_to_mass(node.min_qf), # conversion factor for m^3/s to kg/s
                'max_withdrawal': vol_to_mass(node.max_qf), 
                'electric_substation_id': node.substation_id
            }
        for (i, pipe) in enumerate(self.pipes): 
            network_data['pipes'][str(pipe.id_)] = {
                'id': pipe.id_, 
                'name': pipe.name, 
                'fr_node': pipe.fr_node, 
                'to_node': pipe.to_node, 
                'diameter': pipe.diameter, 
                'length': pipe.length, 
                'friction_factor': pipe.friction_factor
            }
        for (i, compressor) in enumerate(self.compressors):
            network_data['compressors'][str(compressor.id_)] = {
                'id': compressor.id_,
                'name': compressor.name, 
                'fr_node': compressor.fr_node, 
                'to_node': compressor.to_node, 
                'min_c_ratio': 1.0, 
                'max_c_ratio': args.maxcratio
            }
        
        with open(folder + '/network.json', 'w') as fp:
            json.dump(network_data, fp, indent=2)
        return 
    
    def to_boundary_conditions_json(self, folder): 
        bc_data = {
            'boundary_pslack': {}, 
            'boundary_nonslack_flow' : {}
        }
        if len(self.compressors) > 0: 
            bc_data['boundary_compressor'] = {} 
        assert len(self.slack_node_indices) > 0
        assert (len(self.nodes) - len(self.slack_node_indices)) > 0
        # slack pressures
        for i in self.slack_node_indices:
            n = self.nodes[i]
            id_ = n.id_
            bc_data['boundary_pslack'][str(id_)] = n.slack_pressure
        # compressor ratios
        for c in self.compressors: 
            id_ = c.id_ 
            bc_data['boundary_compressor'][str(id_)] = {
                "control_type": 0,
                "value": c.c_ratio
            }
        # nonslack withdrawals 
        for n in self.nodes: 
            id_ = n.id_
            qf = n.qf 
            if n.slack_bool == True: 
                continue 
            if abs(qf) < 1E-4:
                continue 
            bc_data['boundary_nonslack_flow'][str(id_)] = vol_to_mass(qf)
        
        with open(folder + '/bc.json', 'w') as fp:
            json.dump(bc_data, fp, indent=2)
        return 
            