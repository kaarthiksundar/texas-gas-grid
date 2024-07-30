import json

from pathlib import Path
from typing import List, Dict
from typedefs import Params, Node, Pipe, Compressor


def parse(args, log): 
    file = args.datafolder + args.datafile
    if (Path(file).is_file() == False): 
        log.error(f'File {file} does not exist')
        return 
    
    with open(file) as input_file: 
        data = json.load(input_file)
        
    params = to_params(data.get('gas', {}), log)
    nodes = to_nodes(data.get('nodes', []), log)
    branches = data.get('branches', [])
    pipes = to_pipes(filter(lambda x: x['dev_type'] == 'pipe', branches), log)
    compressors = to_compressors(filter(lambda x: x['dev_type'] == 'compressor', branches), log)
    log.info(f'parsed {len(nodes)} nodes')
    log.info(f'parsed {len(branches)} edge elements')
    log.info(f'parsed {len(pipes)} pipes')
    log.info(f'parsed {len(compressors)} compressors')
    # log.debug(nodes)
    
def to_params(data, log):
    # default pressure unit is in kPa; multiply by 1000 to make it to Pa 
    # default temperature units is K 
    return Params(
        gas_constant = data.get('gas_constant', float('nan')),
        z_nominal = data.get('z_nom', float('nan')),
        temp_nominal = data.get('temp_nom', float('nan')),
        pressure_nominal = data.get('pressure_nom', float('nan')) * 1000.0, 
        temp_stp = data.get('temp_stp', float('nan')),
        pressure_stp = data.get('pressure_stp', float('nan')) * 1000.0,  
        z_b1 = data.get('z_b1', float('nan')), 
        z_b2 = data.get('z_b2', float('nan'))
    )
    
def to_nodes(data, log): 
    # default pressure unit is in kPa; multiply by 1000 to make it to Pa 
    # default unit of qf is in m^3/hr; divide by 3600.0 to make it m^3/s
    return [
        Node(
            id_ = node['number'], 
            x_coord = node['lat'], 
            y_coord = node['lon'],
            min_pressure = node.get('min_pressure', float('nan')) * 1000.0, 
            max_pressure = node.get('max_pressure', float('nan')) * 1000.0, 
            slack_bool = node['slack'],
            name = node['name'] + '-' + str(node['number']), 
            qf = node['qf'] / 3600.0, 
            p = node['p'] * 1000.0, 
            sub = node['sub'], 
            qf_min = node['qf_min'] / 3600.0, 
            qf_max = node['qf_max'] / 3600.0
        )
        for node in data
    ]
    
def to_pipes(data, log): 
    # default q unit is m^3/hr; divide by 3600.0 to make it m^3/s
    # default diameter and length unit is m 
    # friction factor is dimensionless - should be approx 0.01
    return [
        Pipe(
            id_ = i, 
            fr_node = pipe['n1'], 
            to_node = pipe['n2'], 
            length = pipe['length'], 
            diameter = pipe['diameter'],
            friction_factor = pipe['friction_factor'], 
            name = pipe['dev_type'] + '-' + str(i), 
            uid = pipe['uid'], 
            q = pipe['q'] / 3600.0 
        )
        for (i, pipe) in enumerate(data)
    ]
    
def to_compressors(data, log): 
    # default q unit is m^3/hr; divide by 3600.0 to make it m^3/s
    return [
        Compressor(
            id_ = i,
            fr_node = compressor['n1'], 
            to_node = compressor['n2'], 
            name = compressor['dev_type'] + '-' + str(i),
            q = compressor['q'] / 3600.0, 
            c_ratio = compressor['r']
        )
        for (i, compressor) in enumerate(data)
    ]
