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
    name: str 
    qf: float 
    p: float 
    sub: int 
    qf_min: float 
    qf_max: float 

@dataclass 
class Pipe: 
    id_: int 
    fr_node: int 
    to_node: int 
    length: float 
    friction_factor: float 
    diameter: float 
    name: str 
    uid: int 
    q: float 
    
@dataclass 
class Compressor: 
    id_: int 
    fr_node: int 
    to_node: int 
    name: str 
    q: float 
    c_ratio: float 