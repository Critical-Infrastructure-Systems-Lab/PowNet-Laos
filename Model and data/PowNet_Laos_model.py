# coding: utf-8
from __future__ import division # convert int or long division arguments to floating point values before division
from pyomo.environ import *
from pyomo.opt import SolverFactory
import itertools

gn_nodes = ['HongsaLignite','Mitlao','HougAnh','EGATBungkan','EGATMukdahan','ChinMengLa'] ##Gen_nodes without demand

gd_nodes = ['Nasaithong','EGATRoiEt2','EGATUbon2','EGATUdon3',
            'EGATNongKhai','EGATMaeMoh','EGATNakhouPhanom','EGATSakonNakhou',
            'VietPleiKu','VietThanhMy','CambKhampongsalao'] ##Gen_nodes with demand

g_nodes = gn_nodes + gd_nodes ##All Thermoplant nodes 


model = AbstractModel()

## string indentifiers for the set of generators
model.Node1Generators =  Set()
model.Node2Generators =  Set()
model.Node3Generators =  Set()
model.Node4Generators =  Set()
model.Node5Generators =  Set()
model.Node6Generators =  Set()
model.Node7Generators =  Set()
model.Node8Generators =  Set()
model.Node9Generators =  Set()
model.Node10Generators =  Set()
model.Node11Generators =  Set()
model.Node12Generators =  Set()
model.Node13Generators =  Set()
model.Node14Generators =  Set()
model.Node15Generators =  Set()
model.Node16Generators =  Set()
model.Node17Generators =  Set()

model.Generators = model.Node1Generators | model.Node2Generators | model.Node3Generators | model.Node4Generators | \
                   model.Node5Generators | model.Node6Generators | model.Node7Generators | model.Node8Generators | \
                   model.Node9Generators | model.Node10Generators | model.Node11Generators | model.Node12Generators | \
                   model.Node13Generators | model.Node14Generators | model.Node15Generators | model.Node16Generators | \
                   model.Node17Generators

### Generators by Fuel Type
model.Biomass = Set()
model.Coal = Set()
model.Slack = Set()

model.Imp_EGAT = Set()
model.Imp_China = Set()

###Allocate generators that will ensure minimum reserves
model.ResGenerators = model.Coal | model.Biomass

### Nodal Matrix
model.nodes = Set()
model.sources = Set(within=model.nodes)
model.sinks = Set(within=model.nodes)

##model.g_nodes = Set()
model.h_nodes = Set()
model.h_imports = Set()
model.d_nodes = Set()

model.gd_nodes = Set()
model.gn_nodes = Set()
model.td_nodes = Set()
model.tn_nodes = Set()

#####==== generators parameters from model input ===####

#Generator Type
model.typ = Param(model.Generators)

#State parameters
model.node = Param(model.Generators)

#Max Generating Capacity
model.maxcap = Param(model.Generators)

#Min Generating Capacity
model.mincap = Param(model.Generators)

#cost function
model.heat_rate = Param(model.Generators)

#Variable O&M
model.var_om = Param(model.Generators)

#Fixed O&M cost
model.fix_om  = Param(model.Generators)

#Start cost
model.st_cost = Param(model.Generators)

#Ramp rate
model.ramp  = Param(model.Generators)

#Minimum up time
model.minup = Param(model.Generators)

#Minimum down time
model.mindn = Param(model.Generators)

#Transmission Path parameters
model.linemva = Param(model.sources, model.sinks)
model.linesus = Param(model.sources, model.sinks)


### parameters for model runs  
## Full range of time series information provided in .dat file (1 year)
model.SimHours = Param(within=PositiveIntegers)
model.SH_periods = RangeSet(1,model.SimHours+1)
model.SimDays = Param(within=PositiveIntegers)
model.SD_periods = RangeSet(1,model.SimDays+1)

### Transmission Loss as a % of production
model.TransLoss = Param(within=NonNegativeReals)

### Maximum line-usage as a percent of line-capacity
model.n1criterion = Param(within=NonNegativeReals)

### Minimum spinning reserve as a percent of total reserve
model.spin_margin = Param(within=NonNegativeReals)

model.m = Param(initialize = 1e5) 

# Operating horizon information 
model.HorizonHours = Param(within=PositiveIntegers)
model.HH_periods = RangeSet(0,model.HorizonHours)
model.hh_periods = RangeSet(1,model.HorizonHours)

#Demand over simulation period
model.SimDemand = Param(model.d_nodes*model.SH_periods, within=NonNegativeReals)
#Horizon demand
model.HorizonDemand = Param(model.d_nodes*model.hh_periods,within=NonNegativeReals,mutable=True)

#Reserve for the entire system
model.SimReserves = Param(model.SH_periods, within=NonNegativeReals)
model.HorizonReserves = Param(model.hh_periods, within=NonNegativeReals,mutable=True)

##Variable resources over simulation period
model.SimHydro = Param(model.h_nodes, model.SH_periods, within=NonNegativeReals)
#Variable resources over horizon
model.HorizonHydro = Param(model.h_nodes,model.hh_periods,within=NonNegativeReals,mutable=True)

##Hydro import over simulation period
model.SimHydroImport = Param(model.h_imports, model.SH_periods, within=NonNegativeReals)
#Hydro import over horizon
model.HorizonHydroImport = Param(model.h_imports,model.hh_periods,within=NonNegativeReals,mutable=True)

##Deratef over simulation period 
model.SimDeratef = Param(model.Generators*model.SH_periods, within=NonNegativeReals)
#Horizon Deratef 
model.HorizonDeratef = Param(model.Generators*model.hh_periods,within=NonNegativeReals,mutable=True)


##Initial conditions
model.ini_on = Param(model.Generators, within=NonNegativeReals, mutable=True) 
model.ini_mwh = Param(model.Generators, within=NonNegativeReals, mutable=True)


#####============= Decision variables ===============########
##Amount of day-ahead energy generated by each generator at each hour
model.mwh = Var(model.Generators,model.HH_periods, within=NonNegativeReals)

#1 if unit is on in hour i
model.on = Var(model.Generators,model.HH_periods, within=Binary)

#1 if unit is switching on in hour i
model.switch = Var(model.Generators,model.HH_periods, within=Binary)

#Amount of spining reserce offered by each unit in each hour
model.srsv = Var(model.Generators,model.HH_periods, within=NonNegativeReals)

#Amount of non-sping reserve ovvered by each unit in each hour
model.nrsv = Var(model.Generators,model.HH_periods, within=NonNegativeReals)

#Hydropower production
model.hydro = Var(model.h_nodes,model.HH_periods,within=NonNegativeReals)

#Hydropower import
model.hydro_import = Var(model.h_imports,model.HH_periods,within=NonNegativeReals)

#Voltage angles at line
model.vlt_angle = Var(model.nodes,model.HH_periods)


####========= Objective function ==================###

def SysCost(model):
    fixed = sum(model.maxcap[j]*model.fix_om[j]*model.on[j,i] for i in model.hh_periods for j in model.Generators)
    starts = sum(model.maxcap[j]*model.st_cost[j]*model.switch[j,i] for i in model.hh_periods for j in model.Generators)

    coal = sum(model.mwh[j,i]*(model.heat_rate[j]*5.0 + model.var_om[j]) for i in model.hh_periods for j in model.Coal)  
    biomass = sum(model.mwh[j,i]*(model.heat_rate[j]*1.5 + model.var_om[j]) for i in model.hh_periods for j in model.Biomass) 

    import_china = sum(model.mwh[j,i]*54.8500001 for i in model.hh_periods for j in model.Imp_China)  #54.850000109
    import_egat = sum(model.mwh[j,i]*54.8500001 for i in model.hh_periods for j in model.Imp_EGAT)  #54.8500000009

    import_hydro = sum(model.hydro_import[j,i]*40 for i in model.hh_periods for j in model.h_imports) 
    
    slack = sum(model.mwh[j,i]*model.heat_rate[j]*1000 for i in model.hh_periods for j in model.Slack)
    
    return fixed + starts + coal + biomass + slack + import_china + import_egat + import_hydro

model.SystemCost = Objective(rule=SysCost, sense=minimize)


###========= Constraints ============####
#Constraints for Max & Min Capacity of Thermoplants and Imports
def MaxC(model,j,i):
    return model.mwh[j,i]  <= model.on[j,i] * model.maxcap[j] *model.HorizonDeratef[j,i]
model.MaxCap= Constraint(model.Generators,model.hh_periods,rule=MaxC)

def MinC(model,j,i):
    return model.mwh[j,i] >= model.on[j,i] * model.mincap[j]
model.MinCap= Constraint(model.Generators,model.hh_periods,rule=MinC)

#Max capacity constraints on hydropower 
def HydroC(model,z,i):
    return model.hydro[z,i] <= model.HorizonHydro[z,i]  
model.HydroConstraint= Constraint(model.h_nodes,model.hh_periods,rule=HydroC)

#Max capacity constraints on hydropower import
def HydroImportC(model,z,i):
    return model.hydro_import[z,i] <= model.HorizonHydroImport[z,i]  
model.HydroImportConstraint= Constraint(model.h_imports,model.hh_periods,rule=HydroImportC)


####=== Reference Node =====#####
def ref_node(model,i):
    return model.vlt_angle['Nasaithong',i] == 0
model.Ref_NodeConstraint= Constraint(model.hh_periods,rule= ref_node)



######=== Power Balance =====########
################=========Hydropower Plants=============################
def HPnodes_Balance(model,z,i):
    renew = model.hydro[z,i]
    #demand = model.HorizonDemand[z,i]
    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)
    return (1 - model.TransLoss) * renew == impedance ##- demand
model.HPnodes_BalConstraint= Constraint(model.h_nodes,model.hh_periods,rule= HPnodes_Balance)

################=========Hydropower Imports=============################
def HP_Imports_Balance(model,z,i):
    hp_import = model.hydro_import[z,i]
    #demand = model.HorizonDemand[z,i]
    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)
    return (1 - model.TransLoss) * hp_import == impedance ##- demand
model.HP_Imports_BalConstraint= Constraint(model.h_imports,model.hh_periods,rule= HP_Imports_Balance)


#########======= Transformers with demand Nodes =========#######
def TDnodes_Balance(model,z,i):
    demand = model.HorizonDemand[z,i]
    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return - demand == impedance
model.TDnodes_BalConstraint= Constraint(model.td_nodes,model.hh_periods,rule= TDnodes_Balance)

#########======= Transformers without demand Nodes =========#######
def TNnodes_Balance(model,z,i):
    #demand = model.HorizonDemand[z,i]
    impedance = sum(model.linesus[z,k] * (model.vlt_angle[z,i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return 0 == impedance
model.TNnodes_BalConstraint= Constraint(model.tn_nodes,model.hh_periods,rule= TNnodes_Balance)

##########============ Thermoplants and Import Nodes without Demand ==============############
def Node1_Balance(model,i):
    nd = 1
    thermo = sum(model.mwh[j,i] for j in model.Node1Generators)    
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.Node1_BalConstraint= Constraint(model.hh_periods,rule= Node1_Balance)

def Node2_Balance(model,i):
    nd = 2
    thermo = sum(model.mwh[j,i] for j in model.Node2Generators)    
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.Node2_BalConstraint= Constraint(model.hh_periods,rule= Node2_Balance)

def Node3_Balance(model,i):
    nd = 3
    thermo = sum(model.mwh[j,i] for j in model.Node3Generators)    
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.Node3_BalConstraint= Constraint(model.hh_periods,rule= Node3_Balance)

def Node4_Balance(model,i):
    nd = 4
    thermo = sum(model.mwh[j,i] for j in model.Node4Generators)    
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.Node4_BalConstraint= Constraint(model.hh_periods,rule= Node4_Balance)

def Node5_Balance(model,i):
    nd = 5
    thermo = sum(model.mwh[j,i] for j in model.Node5Generators)    
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.Node5_BalConstraint= Constraint(model.hh_periods,rule= Node5_Balance)

def Node6_Balance(model,i):
    nd = 6
    thermo = sum(model.mwh[j,i] for j in model.Node6Generators)    
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo == impedance #- demand
model.Node6_BalConstraint= Constraint(model.hh_periods,rule= Node6_Balance)

##########============ Thermoplants and Import Nodes with Demand ==============############
def Node7_Balance(model,i):
    nd = 7
    thermo = sum(model.mwh[j,i] for j in model.Node7Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node7_BalConstraint= Constraint(model.hh_periods,rule= Node7_Balance)

def Node8_Balance(model,i):
    nd = 8
    thermo = sum(model.mwh[j,i] for j in model.Node8Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node8_BalConstraint= Constraint(model.hh_periods,rule= Node8_Balance)

def Node9_Balance(model,i):
    nd = 9
    thermo = sum(model.mwh[j,i] for j in model.Node9Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node9_BalConstraint= Constraint(model.hh_periods,rule= Node9_Balance)

def Node10_Balance(model,i):
    nd = 10
    thermo = sum(model.mwh[j,i] for j in model.Node10Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node10_BalConstraint= Constraint(model.hh_periods,rule= Node10_Balance)

def Node11_Balance(model,i):
    nd = 11
    thermo = sum(model.mwh[j,i] for j in model.Node11Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node11_BalConstraint= Constraint(model.hh_periods,rule= Node11_Balance)

def Node12_Balance(model,i):
    nd = 12
    thermo = sum(model.mwh[j,i] for j in model.Node12Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node12_BalConstraint= Constraint(model.hh_periods,rule= Node12_Balance)

def Node13_Balance(model,i):
    nd = 13
    thermo = sum(model.mwh[j,i] for j in model.Node13Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node13_BalConstraint= Constraint(model.hh_periods,rule= Node13_Balance)

def Node14_Balance(model,i):
    nd = 14
    thermo = sum(model.mwh[j,i] for j in model.Node14Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node14_BalConstraint= Constraint(model.hh_periods,rule= Node14_Balance)

def Node15_Balance(model,i):
    nd = 15
    thermo = sum(model.mwh[j,i] for j in model.Node15Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node15_BalConstraint= Constraint(model.hh_periods,rule= Node15_Balance)

def Node16_Balance(model,i):
    nd = 16
    thermo = sum(model.mwh[j,i] for j in model.Node16Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node16_BalConstraint= Constraint(model.hh_periods,rule= Node16_Balance)

def Node17_Balance(model,i):
    nd = 17
    thermo = sum(model.mwh[j,i] for j in model.Node17Generators)
    demand = model.HorizonDemand[g_nodes[nd-1],i]
    impedance = sum(model.linesus[g_nodes[nd-1],k] * (model.vlt_angle[g_nodes[nd-1],i] - model.vlt_angle[k,i]) for k in model.sinks)   
    return (1 - model.TransLoss) * thermo - demand == impedance
model.Node17_BalConstraint= Constraint(model.hh_periods,rule= Node17_Balance)



######========== Transmission Line Constraints =========#############
def MaxLine(model,s,k,i):
    if model.linemva[s,k] > 0:
        return (model.n1criterion) * model.linemva[s,k] >= model.linesus[s,k] * (model.vlt_angle[s,i] - model.vlt_angle[k,i])
    else:
        return Constraint.Skip
model.MaxLineConstraint= Constraint(model.sources,model.sinks,model.hh_periods,rule=MaxLine)

def MinLine(model,s,k,i):
    if model.linemva[s,k] > 0:
        return (-model.n1criterion) * model.linemva[s,k] <= model.linesus[s,k] * (model.vlt_angle[s,i] - model.vlt_angle[k,i])
    else:
        return Constraint.Skip
model.MinLineConstraint= Constraint(model.sources,model.sinks,model.hh_periods,rule=MinLine)


######========== Reserve Constraint =========#############
##System Reserve Requirement
def SysReserve(model,i):
    return sum(model.srsv[j,i] for j in model.ResGenerators) + sum(model.nrsv[j,i] for j in model.ResGenerators) >= model.HorizonReserves[i]
model.SystemReserve = Constraint(model.hh_periods,rule=SysReserve)

##Spinning Reserve Requirement
def SpinningReq(model,i):
    return sum(model.srsv[j,i] for j in model.ResGenerators) >= model.spin_margin * model.HorizonReserves[i] 
model.SpinReq = Constraint(model.hh_periods,rule=SpinningReq)           

##Spinning reserve can only be offered by units that are online
def SpinningReq2(model,j,i):
    return model.srsv[j,i] <= model.on[j,i]*model.maxcap[j] *model.HorizonDeratef[j,i]
model.SpinReq2= Constraint(model.Generators,model.hh_periods,rule=SpinningReq2) 

##Non-Spinning reserve can only be offered by units that are offline
def NonSpinningReq(model,j,i):
    return model.nrsv[j,i] <= (1 - model.on[j,i])*model.maxcap[j] *model.HorizonDeratef[j,i]
model.NonSpinReq= Constraint(model.Generators,model.hh_periods,rule=NonSpinningReq)


######========== Zero Sum Constraint =========#############
def ZeroSum(model,j,i):
    return model.mwh[j,i] + model.srsv[j,i] + model.nrsv[j,i] <= model.maxcap[j] * model.HorizonDeratef[j,i]
model.ZeroSumConstraint=Constraint(model.Generators,model.hh_periods,rule=ZeroSum)

######========== Logical Constraint =========#############
def MwhCon_initial(model,j,i): 
    if i == 0:
        return (model.mwh[j,i] == model.ini_mwh[j])
    else:
      return Constraint.Skip
model.initial_mwh_constr = Constraint(model.Generators,model.HH_periods, rule=MwhCon_initial)

def OnCon_initial(model,j,i): 
    if i == 0: 
        return (model.on[j,i] == model.ini_on[j])
    else:
      return Constraint.Skip
model.initial_value_constr = Constraint(model.Generators,model.HH_periods, rule=OnCon_initial)

def SwitchCon2(model,j,i):
    return model.switch[j,i] <= model.on[j,i] * model.m
model.Switch2Constraint = Constraint(model.Generators,model.hh_periods,rule = SwitchCon2)

def SwitchCon3(model,j,i):
    return  model.switch[j,i] <= (1 - model.on[j,i-1]) * model.m  
model.Switch3Constraint = Constraint(model.Generators,model.hh_periods,rule = SwitchCon3)

def SwitchCon4(model,j,i):
    return  model.on[j,i] - model.on[j,i-1] <= model.switch[j,i]
model.Switch4Constraint = Constraint(model.Generators,model.hh_periods,rule = SwitchCon4)

######========== Up/Down Time Constraint =========#############
##Min Up time
def MinUp(model,j,i,k):
    if i > 0 and k > i and k <= min(i+model.minup[j]-1,model.HorizonHours):
        return model.on[j,i] - model.on[j,i-1] <= model.on[j,k]
    else: 
        return Constraint.Skip
model.MinimumUp = Constraint(model.Generators,model.HH_periods,model.HH_periods,rule=MinUp)

##Min Down time
def MinDown(model,j,i,k):
   if i > 0 and k > i and k <= min(i+model.mindn[j]-1,model.HorizonHours):
       return model.on[j,i-1] - model.on[j,i] <= 1 - model.on[j,k]
   else:
       return Constraint.Skip
model.MinimumDown = Constraint(model.Generators,model.HH_periods,model.HH_periods,rule=MinDown)

######==========Ramp Rate Constraints =========#############
def Ramp1(model,j,i): #v1.3
    a = model.mwh[j,i]
    if i == 1:
        b = model.ini_mwh[j]
    else:
        b = model.mwh[j,i-1]
    return a - b <= model.ramp[j] 
model.RampCon1 = Constraint(model.Generators,model.hh_periods,rule=Ramp1)

def Ramp2(model,j,i): #v1.3
    a = model.mwh[j,i]
    if i == 1:
        b = model.ini_mwh[j]
    else:
        b = model.mwh[j,i-1]
    return b - a <= model.ramp[j] 
model.RampCon2 = Constraint(model.Generators,model.hh_periods,rule=Ramp2)


######======================================#############
######==========        End        =========#############
######=======================================############
