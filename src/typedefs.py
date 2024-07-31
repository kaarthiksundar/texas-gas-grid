from dataclasses import dataclass
from typing import List, Dict

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
    
    def to_json(self):
        pass