import json

from pathlib import Path
from typing import List, Dict
from typedefs import Params, Node, Pipe, Compressor, SteadyStateData
from converters import psi, pascal
from math import isnan


def parse(args, log): 
    file = args.datafolder + args.datafile
    if (Path(file).is_file() == False): 
        log.error(f'File {file} does not exist')
        return 
    
    with open(file) as input_file: 
        data = json.load(input_file)
        
    params = to_params(data.get('gas', {}), log)
    nodes, slack_node_indices = to_nodes(data.get('nodes', []), args, log)
    branches = data.get('branches', [])
    pipes = to_pipes(filter(lambda x: x['dev_type'] == 'pipe', branches), log)
    compressors = to_compressors(filter(lambda x: x['dev_type'] == 'compressor', branches), args, log)
    log.info(f'parsed {len(nodes)} nodes')
    nodal_injections = [node.qf for node in nodes]
    log.info(f'parsed {len(branches)} edge elements')
    log.info(f'parsed {len(pipes)} pipes')
    log.info(f'parsed {len(compressors)} compressors')
    log.warning(f'net injection = {sum(nodal_injections)} (+ve means withdrawal)')
    ss_data = SteadyStateData(params, nodes, pipes, compressors, slack_node_indices)
    output_folder = args.outputfolder + args.datafile.split('.')[0]
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    log.info(f'output folder {output_folder} created')
    ss_data.to_params_json(output_folder) 
    ss_data.to_network_json(args, output_folder)
    ss_data.to_boundary_conditions_json(output_folder)
    log.info(f'data written to files: params.json, network.json, bc.json')
    
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
    
def to_nodes(data, args, log): 
    log.info('node parsing started')
    log.info('default pressure unit is in kPa; converting to Pa')
    log.info('default unit of qf, min, max (volumetric flow rate) is in m^3/hr; converting to m^3/s')
    log.info('ignored fields: p')
    log.info('for missing nodal pressure limits, defaulting to [500, args.maxpressurepsi] psi')
    num_negative_p_values = 0
    num_slack_nodes = 0
    slack_node_indices = []
    nodes = []
    for node in data: 
        id_ = node['number']
        x_coord = node['lat']
        y_coord = node['lon']
        min_pressure = node.get('min_pressure', 3447.378) * 1000.0 
        max_pressure = node.get('max_pressure', pascal(args.maxpressurepsi))
        slack_bool = node['slack']
        p = node['p'] * 1000.0
        if p < 0.0: 
            num_negative_p_values += 1
        if slack_bool == True: 
            num_slack_nodes += 1
            if p < 0.0: 
                log.warn('slack pressure is negative, defaulting to 800 psi')
                p = 5515.805 * 1000.0
        else: 
            p = float('nan')
        name = node['name'] + '-' + str(id_)
        qf = node['qf'] / 3600.0 
        min_qf = node['qf_min'] / 3600.0
        max_qf = node['qf_max'] / 3600.0
        n = Node(
            id_ = id_,  
            x_coord = x_coord, 
            y_coord = y_coord, 
            min_pressure = min_pressure, 
            max_pressure = max_pressure, 
            slack_bool = slack_bool, 
            slack_pressure = p,
            name = name, 
            qf = qf,
            min_qf = min_qf, 
            max_qf = max_qf, 
            substation_id = node['sub']
        )
        if (slack_bool == True):
            log.info(f'slack node {id_} pressure: {psi(p)} psi')
            slack_node_indices.append(len(nodes))
        nodes.append(n)
    log.info(f'num slack nodes: {num_slack_nodes}')
    log.warn(f'negative solution pressure values found for {num_negative_p_values} nodes')
    log.info('node parsing completed')
    return nodes, slack_node_indices 
    
def to_pipes(data, log): 
    log.info('pipe parsing started')
    log.info('default length and diameter unit is m')
    log.info('friction factor is dimensionless (approx 0.01)')
    log.info('default unit of qf (volumetric flow rate) is in m^3/hr; converting to m^3/s')
    log.info('ignored fields: uid')
    pipes = []
    for (i, pipe) in enumerate(data): 
        fr_node = pipe['n1']
        to_node = pipe['n2']
        length = pipe['length']
        diameter = pipe['diameter']
        friction_factor = pipe['friction_factor'] 
        name = pipe['dev_type'] + '-' + str(i)
        q = pipe['q'] / 3600.0 
        p = Pipe(
            id_ = i, 
            fr_node = fr_node, 
            to_node = to_node, 
            length = length, 
            diameter = diameter,
            friction_factor = friction_factor, 
            name = name, 
            q = q
        )
        pipes.append(p)
    log.info('pipe parsing completed')
    return pipes
    
def to_compressors(data, args, log): 
    log.info('compressor parsing started')
    log.info('default unit of qf (volumetric flow rate) is in m^3/hr; converting to m^3/s')
    compressors = [
        Compressor(
            id_ = i,
            fr_node = compressor['n1'], 
            to_node = compressor['n2'], 
            name = compressor['dev_type'] + '-' + str(i),
            q = compressor['q'] / 3600.0, 
            c_ratio = compressor['r'] if isnan(args.cratiosetpoint) else args.cratiosetpoint
        )
        for (i, compressor) in enumerate(data)
    ]
    log.info('compressor parsing completed')
    return compressors
