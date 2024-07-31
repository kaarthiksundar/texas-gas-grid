# pascal to psi
def psi(p: float):
    return p * 0.000145038

# psi to pascal
def pascal(p: float):
    return p / 0.000145038

# conversion factor for m^3/s to kg/s
def vol_to_mass(q: float): 
    return q * 0.8039