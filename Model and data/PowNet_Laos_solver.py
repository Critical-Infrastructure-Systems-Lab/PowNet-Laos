from pyomo.opt import SolverFactory, SolverStatus
from pyomo.core import Var
from pyomo.core import Param
from operator import itemgetter
import pandas as pd
from datetime import datetime
import os

yr = 2016
run_no = 1
os.getcwd()

from PowNet_Laos_model import model

instance = model.create_instance('input/pownet_data_laos_'+str(yr)+'.dat')

opt = SolverFactory("gurobi")
opt.options["threads"] = 1
#opt.options["TimeLimit"] = 5 
H = instance.HorizonHours
K=range(1,H+1)
start = 1 ##1 to 364
end  = 366 ##2 to 366

#Space to store results
mwh=[]
on=[]
switch=[]
srsv=[]
nrsv=[]
hydro=[]
hydro_import=[]
vlt_angle=[]
Generator=[]


for day in range(start,end):
    for z in instance.d_nodes:
     #load Demand and Reserve time series data
        for i in K:
            instance.HorizonDemand[z,i] = instance.SimDemand[z,(day-1)*24+i]
            instance.HorizonReserves[i] = instance.SimReserves[(day-1)*24+i] 
            
    for z in instance.h_nodes:
     #load Hydropower time series data
        for i in K:
            instance.HorizonHydro[z,i] = instance.SimHydro[z,(day-1)*24+i]
            
    for z in instance.h_imports:
     #load Hydropower_import time series data
        for i in K:
            instance.HorizonHydroImport[z,i] = instance.SimHydroImport[z,(day-1)*24+i]
            
    for z in instance.Generators:
     #load Deratef time series data ##v1.3
        for i in K:
            instance.HorizonDeratef[z,i] = instance.SimDeratef[z,(day-1)*24+i]
        
    laos_result = opt.solve(instance, tee = True) ##,tee=True to check number of variables
    
    if laos_result.solver.status == SolverStatus.aborted: #max time limit reached 
        laos_result.solver.status = SolverStatus.warning #change status so that results can be loaded
        
    instance.solutions.load_from(laos_result)   
 
###The following section is for storing and sorting results
    for v in instance.component_objects(Var, active=True):
        varobject = getattr(instance, str(v))
        a=str(v)
        if a=='mwh':
            ini_mwh_ = {} 
            for index in varobject:
                if int(index[1]>0 and index[1]<25):
                    
                    if index[0] in instance.Biomass:
                        mwh.append((index[0],index[1]+((day-1)*24),varobject[index].value,'Biomass'))
                    elif index[0] in instance.Coal:
                        mwh.append((index[0],index[1]+((day-1)*24),varobject[index].value,'Coal'))                                                   
                    elif index[0] in instance.Imp_EGAT:
                        mwh.append((index[0],index[1]+((day-1)*24),varobject[index].value,'Imp_EGAT'))                          
                    elif index[0] in instance.Imp_China:
                        mwh.append((index[0],index[1]+((day-1)*24),varobject[index].value,'Imp_China'))
                    elif index[0] in instance.Slack:
                        mwh.append((index[0],index[1]+((day-1)*24),varobject[index].value,'Slack'))
                if int(index[1])==24:
                    ini_mwh_[index[0]] = varobject[index].value   

        if a=='hydro':
      
             for index in varobject:
                 if int(index[1]>0 and index[1]<25):
                    if index[0] in instance.h_nodes:
                        hydro.append((index[0],index[1]+((day-1)*24),varobject[index].value))   
                            

        if a=='hydro_import':
      
             for index in varobject:
                 if int(index[1]>0 and index[1]<25):
                    if index[0] in instance.h_imports:
                        hydro_import.append((index[0],index[1]+((day-1)*24),varobject[index].value))   

        if a=='vlt_angle':
      
             for index in varobject:
                 if int(index[1]>0 and index[1]<25):
                    if index[0] in instance.nodes:
                        vlt_angle.append((index[0],index[1]+((day-1)*24),varobject[index].value))        
    
        if a=='on':        
            ini_on_ = {} #v1.2
            for index in varobject:
                if int(index[1]>0 and index[1]<25):
                    on.append((index[0],index[1]+((day-1)*24),varobject[index].value))
                if int(index[1])==24: #v1.2
                    ini_on_[index[0]] = varobject[index].value #v1.2
            

        if a=='switch':  
            for index in varobject:
                if int(index[1]>0 and index[1]<25):
                    switch.append((index[0],index[1]+((day-1)*24),varobject[index].value))


        if a=='srsv':    
            for index in varobject:
                if int(index[1]>0 and index[1]<25):
                    srsv.append((index[0],index[1]+((day-1)*24),varobject[index].value))

                        
        if a=='nrsv':    
            for index in varobject:
                if int(index[1]>0 and index[1]<25):
                    nrsv.append((index[0],index[1]+((day-1)*24),varobject[index].value))
                    
    # Update initialization values for "on" and "mwh"
    for z in instance.Generators:
        instance.ini_on[z] = round(ini_on_[z])
        instance.ini_mwh[z] = max(round(ini_mwh_[z],2),0)   

    print(day)
    print(str(datetime.now()))

mwh_pd=pd.DataFrame(mwh,columns=('Generator','Time','Value','Type'))
hydro_pd=pd.DataFrame(hydro,columns=('Node','Time','Value'))
hydro_import_pd=pd.DataFrame(hydro_import,columns=('Node','Time','Value'))
vlt_angle_pd=pd.DataFrame(vlt_angle,columns=('Node','Time','Value'))
on_pd=pd.DataFrame(on,columns=('Generator','Time','Value'))
switch_pd=pd.DataFrame(switch,columns=('Generator','Time','Value'))
srsv_pd=pd.DataFrame(srsv,columns=('Generator','Time','Value'))
nrsv_pd=pd.DataFrame(nrsv,columns=('Generator','Time','Value'))
    
mwh_pd.to_csv('output/out_laos_'+str(yr)+'_R'+str(run_no)+'_mwh.csv')
hydro_pd.to_csv('output/out_laos_'+str(yr)+'_R'+str(run_no)+'_hydro.csv')
hydro_import_pd.to_csv('output/out_laos_'+str(yr)+'_R'+str(run_no)+'_hydro_import.csv')
vlt_angle_pd.to_csv('output/out_laos_'+str(yr)+'_R'+str(run_no)+'_vlt_angle.csv')
on_pd.to_csv('output/out_laos_'+str(yr)+'_R'+str(run_no)+'_on.csv')
switch_pd.to_csv('output/out_laos_'+str(yr)+'_R'+str(run_no)+'_switch.csv')
srsv_pd.to_csv('output/out_laos_'+str(yr)+'_R'+str(run_no)+'_srsv.csv')
nrsv_pd.to_csv('output/out_laos_'+str(yr)+'_R'+str(run_no)+'_nrsv.csv')
