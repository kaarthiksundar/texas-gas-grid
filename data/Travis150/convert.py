import xlwings as xw
import json

wb = xw.Book('Travis150_Gas_Data.xlsx')

nodes = wb.sheets[0].range('A1:F48').value
electric_demand = wb.sheets[1].range('A1:E8').value
gas_demand = wb.sheets[2].range('A1:C17').value 
sources = wb.sheets[3].range('A1:C2').value 
pipes = wb.sheets[4].range('A1:F47').value 

json_dict = { "gas": {
    "gas_constant": 473.92,
    "z_nom": 0.8361480902140113,
    "temp_nom": 288.706,
    "pressure_nom": 6500,
    "temp_stp": 273.15,
    "pressure_stp": 101.32,
    "z_b1": 1.00300865,
    "z_b2": 2.96848838e-08
    }, 
    "nodes": [],
    "branches": []}

for node_data in nodes[1:]:
    number = int(node_data[0])
    type_data = int(node_data[4])
    node_data_name = node_data[1]
    name = ''
    slack = False
    sub = None
    qf = 0.0
    qf_min = 0.0 
    qf_max = 0.0
    if (type_data == 0): 
        name = 'Processing Plant - Slack'
        match = next(filter(lambda x: int(x[0]) == number, sources[1:]))
        qf_min = match[2]
        qf_min = qf_min * 10**6 * 0.3**3 / 30.0/ 24.0 # conversion to m^3/hr
        slack = True
    elif (type_data == 1):
        name = 'Electric Load'
        # the qf in data is MMSCF/month
        match = next(filter(lambda x: x[3].strip() == node_data_name, electric_demand[1:]))
        sub = int(match[2])
        qf = match[1]
        qf = qf * 10**6 * 0.3**3 / 30.0/ 24.0 # conversion to m^3/hr
        qf_min = qf 
        qf_max = qf
    elif (type_data == 2):
        name = 'Gas Load'
        # the qf in data is MMSCF/month
        match = next(filter(lambda x: x[2].strip() == node_data_name, gas_demand[1:]))
        qf = match[1]
        qf = qf * 10**6 * 0.3**3 / 30.0/ 24.0 # conversion to m^3/hr
        qf_min = qf 
        qf_max = qf
    else: 
        name = 'Junction'        
    p = node_data[5]
    lat = node_data[2]
    lon = node_data[3]

    node = {
        "number": number,
        "name": name,
        "slack": slack,
        "qf": qf,
        "p": p,
        "sub": sub,
        "lat": lat,
        "lon": lon,
        "qf_min": qf_min,
        "qf_max": qf_max
    }
    json_dict["nodes"].append(node)

counter = 1
for pipe_data in pipes[1:]:
    pipe = {
        "dev_type": "pipe",
        "n1": int(pipe_data[0]),
        "n2": int(pipe_data[1]),
        "uid": counter,
        "q": pipe_data[5],
        "length": pipe_data[3] * 1000.0,
        "diameter": pipe_data[2]/1000.0,
        "friction_factor": 0.9407/pipe_data[2]**(1/3),
        "k": pipe_data[4]
    }
    counter += 1
    json_dict["branches"].append(pipe)
    
json_object = json.dumps(json_dict, indent = 4) 
with open('./data/Travis150/Travis150_Gas.json', 'w') as text_file:
    print(json_object, file=text_file)