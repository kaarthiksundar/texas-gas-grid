import xlwings as xw

wb = xw.Book('Travis150_Gas_Data.xlsx')

nodes = wb.sheets[0].range('A1:F48').value
electric_demand = wb.sheets[1].range('A1:E8').value
gas_demand = wb.sheets[2].range('A1:C17').value 
sources = wb.sheets[3].range('A1:C2').value 
pipes = wb.sheets[4].range('A1:F47').value 


print(nodes)
print(electric_demand)
print(gas_demand)
print(sources) 
print(pipes)