import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

curr_year = 2016

SimDays = 365
SimHours = SimDays * 24
HorizonHours = 24  ##planning horizon (e.g., 24, 48, 72 hours etc.)
TransLoss = 0.07   ##transmission loss as a percent of generation
n1criterion = 0.75 ##maximum line-usage as a percent of line-capacity
res_margin = 0.1   ##minimum reserve as a percent of system demand
spin_margin = 0.50 ##minimum spinning reserve as a percent of total reserve

data_name = 'pownet_data_laos_'+str(curr_year)+''


#read thermo plant parameters into DataFrame
df_gen = pd.read_csv('data_laos_thermo_2016.csv',header=0)
df_gen_deratef = pd.read_csv('data_laos_thermo_deratef.csv',header=0)
df_gen['deratef'] = df_gen_deratef['deratef_'+str(curr_year)+'']

##hourly ts of hydropower
df_hydro = pd.read_csv('data_laos_hydro_'+str(curr_year)+'.csv',header=0)   

##hourly ts of hydropower import
df_hydro_import = pd.read_csv('data_laos_hydro_import_'+str(curr_year)+'.csv',header=0)   

##hourly ts of load and exports
df_load = pd.read_csv('data_laos_load_export_2016.csv',header=0)   

##hourly ts of reserve for national demand
df_reserves = pd.DataFrame((df_load.iloc[:,5:64].sum(axis=1)*res_margin).values,columns=['Reserve'])

#capacity and susceptence of each transmission line (one direction)
df_trans1 = pd.read_csv('data_laos_transparam_2016.csv',header=0)
#capacity and susceptence of each transmission line (both directions)
df_trans2 = pd.DataFrame([df_trans1['sink'],df_trans1['source'],df_trans1['linemva'],df_trans1['linesus']]).transpose()
df_trans2.columns = ['source','sink','linemva','linesus']
df_paths = pd.concat([df_trans1,df_trans2], axis=0)
df_paths.index = np.arange(len(df_paths))


###list nodes
all_nodes = ['BanDon','BangYo','BanHat','BanNa','BanNathone','BMet','Bountari','BPompik',
             'Donkoi','Hinheup','HouycaiMining','Jiangsai','Kasi','KCLCement','Khoksaad',
             'Khonsong','LuangNamtha1','Luangprabang1','Luangprabang2','Mahaxai','MahaxaiCement',
             'MPhin','Nahor','NakadokMinning','NaMo2','Nongbong','Nongdeun','NonHai','Oudomsay',
             'Pakbo','Paklay','Pakmong2','Paksan','Paksong','Paktang','PhoneSoung','Phonsavan',
             'Phontong','PhubiaMinning','Sapaothong','SeinSouk','SeponMinning','Taothan',
             'Thabok','Thakhek','Thalath','Thanaleng','ThaNgon','Thasala','Thavieng','Tongkhoun1',
             'Tongkhoun2','Veingkam','Viengkeo','Viengvieng','Xamneual','Xayabury','XiengNgum',
             'Nasaithong','BanVean','NabongWest','Nabong','NaMoSwitch','HouayHo','HouayLamphan',
             'NamKhan2','NamKhan3','NamLeuk','NamLik1n2','NamMang1','NamMang3','NamNgiep2',
             'NamNgiep2C','NamNgiep3A','NamNgum1','NamNgum2','NamNgum5','NamOu2','NamOu5','NamOu6',
             'NamSan3A','NamSan3B','NamSana','NamTheun2','Salabam','TheunHinboun','Xekaman1','Xekaman3',
             'Xenamnoy1','Xenamnoy6','Xeset1','Xeset2','Xeset3','HongsaLignite','HougAnh','Mitlao',
             'ChinMengLa','EGATBungkan','EGATMukdahan','EGATMaeMoh','EGATNongKhai','EGATUdon3',
             'EGATNakhouPhanom','EGATSakonNakhou','EGATRoiEt2','EGATUbon2','EGATSirindhorn',
             'VietThanhMy','VietPleiKu','CambKhampongsalao'] 

h_nodes = ['HouayHo','HouayLamphan','NamKhan2','NamKhan3','NamLeuk','NamLik1n2',
           'NamMang1','NamMang3','NamNgiep2','NamNgiep2C','NamNgiep3A',
           'NamNgum1','NamNgum2','NamNgum5','NamOu2','NamOu5','NamOu6',
           'NamSan3A','NamSan3B','NamSana','NamTheun2','Salabam','TheunHinboun',
           'Xekaman1','Xekaman3','Xenamnoy1','Xenamnoy6','Xeset1','Xeset2','Xeset3']

h_imports = ['EGATSirindhorn']


d_nodes = ['BanDon','BangYo','BanHat','BanNa','BanNathone','BMet','Bountari','BPompik',
           'Donkoi','Hinheup','HouycaiMining','Jiangsai','Kasi','KCLCement','Khoksaad',
           'Khonsong','LuangNamtha1','Luangprabang1','Luangprabang2','Mahaxai','MahaxaiCement',
           'MPhin','Nahor','NakadokMinning','NaMo2','Nongbong','Nongdeun','NonHai','Oudomsay',
           'Pakbo','Paklay','Pakmong2','Paksan','Paksong','Paktang','PhoneSoung','Phonsavan',
           'Phontong','PhubiaMinning','Sapaothong','SeinSouk','SeponMinning','Taothan',
           'Thabok','Thakhek','Thalath','Thanaleng','ThaNgon','Thasala','Thavieng','Tongkhoun1',
           'Tongkhoun2','Veingkam','Viengkeo','Viengvieng','Xamneual','Xayabury','XiengNgum',
           'Nasaithong','EGATMaeMoh','EGATNongKhai','EGATUdon3','EGATNakhouPhanom','EGATSakonNakhou',
           'EGATRoiEt2','EGATUbon2','VietThanhMy','VietPleiKu','CambKhampongsalao']


gn_nodes = ['HongsaLignite','Mitlao','HougAnh','EGATBungkan','EGATMukdahan','ChinMengLa'] ##Gen_nodes without demand

gd_nodes = ['Nasaithong','EGATRoiEt2','EGATUbon2','EGATUdon3',
            'EGATNongKhai','EGATMaeMoh','EGATNakhouPhanom','EGATSakonNakhou',
            'VietPleiKu','VietThanhMy','CambKhampongsalao'] ##Gen_nodes with demand

g_nodes = gn_nodes + gd_nodes ##All Thermoplant nodes 



td_nodes = ['BanDon','BangYo','BanHat','BanNa','BanNathone','BMet','Bountari','BPompik',
            'Donkoi','Hinheup','HouycaiMining','Jiangsai','Kasi','KCLCement','Khoksaad',
            'Khonsong','LuangNamtha1','Luangprabang1','Luangprabang2','Mahaxai','MahaxaiCement',
            'MPhin','Nahor','NakadokMinning','NaMo2','Nongbong','Nongdeun','NonHai','Oudomsay',
            'Pakbo','Paklay','Pakmong2','Paksan','Paksong','Paktang','PhoneSoung','Phonsavan',
            'Phontong','PhubiaMinning','Sapaothong','SeinSouk','SeponMinning','Taothan',
            'Thabok','Thakhek','Thalath','Thanaleng','ThaNgon','Thasala','Thavieng','Tongkhoun1',
            'Tongkhoun2','Veingkam','Viengkeo','Viengvieng','Xamneual','Xayabury','XiengNgum'] ##Transformers with demand

tn_nodes = ['BanVean','NabongWest','Nabong','NaMoSwitch'] ##Transformers without demand



#list plant types
types = ['biomass','coal','slack','imp_china','imp_egat']


######====== write data.dat file ======########
with open(''+str(data_name)+'.dat', 'w') as f:

###### generator sets by generator nodes
    for z in g_nodes:
        # node string
        z_int = g_nodes.index(z)
        f.write('set Node%dGenerators :=\n' % (z_int+1))
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'node'] == z:
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')    
    
    
####### generator sets by type
    # Biomass
    f.write('set Biomass :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'biomass':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')    
   
    # Coal
    f.write('set Coal :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'coal':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')        

    # Import from China
    f.write('set Imp_China :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'imp_china':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')  

    # Import from Thai_EGAT
    f.write('set Imp_EGAT :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'imp_egat':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')  


    # Slack
    f.write('set Slack :=\n')
    # pull relevant generators
    for gen in range(0,len(df_gen)):
        if df_gen.loc[gen,'typ'] == 'slack':
            unit_name = df_gen.loc[gen,'name']
            unit_name = unit_name.replace(' ','_')
            f.write(unit_name + ' ')
    f.write(';\n\n')  

######Set nodes, sources and sinks
    # nodes
    f.write('set nodes :=\n')
    for z in all_nodes:
        f.write(z + ' ')
    f.write(';\n\n')
    
    # sources
    f.write('set sources :=\n')
    for z in all_nodes:
        f.write(z + ' ')
    f.write(';\n\n')
    
    # sinks
    f.write('set sinks :=\n')
    for z in all_nodes:
        f.write(z + ' ')
    f.write(';\n\n')

    # hydro_nodes
    f.write('set h_nodes :=\n')
    for z in h_nodes:
        f.write(z + ' ')
    f.write(';\n\n')

    # hydro_imports nodes
    f.write('set h_imports :=\n')
    for z in h_imports:
        f.write(z + ' ')
    f.write(';\n\n')

    # all demand nodes
    f.write('set d_nodes :=\n')
    for z in d_nodes:
        f.write(z + ' ')
    f.write(';\n\n')

    # generator with demand nodes
    f.write('set gd_nodes :=\n')
    for z in gd_nodes:
        f.write(z + ' ')
    f.write(';\n\n')

    # generator without demand nodes
    f.write('set gn_nodes :=\n')
    for z in gn_nodes:
        f.write(z + ' ')
    f.write(';\n\n')

    # transformer with demand nodes
    f.write('set td_nodes :=\n')
    for z in td_nodes:
        f.write(z + ' ')
    f.write(';\n\n')

    # transformer without demand nodes
    f.write('set tn_nodes :=\n')
    for z in tn_nodes:
        f.write(z + ' ')
    f.write(';\n\n')

    
################
#  parameters  #
################
    
####### simulation period and horizon
    f.write('param SimHours := %d;' % SimHours)
    f.write('\n')
    f.write('param SimDays:= %d;' % SimDays)
    f.write('\n\n')   
    f.write('param HorizonHours := %d;' % HorizonHours)
    f.write('\n\n')
    f.write('param TransLoss := %0.3f;' % TransLoss)
    f.write('\n\n')
    f.write('param n1criterion := %0.3f;' % n1criterion)
    f.write('\n\n')
    f.write('param spin_margin := %0.3f;' % spin_margin)
    f.write('\n\n')

    
####### create parameter matrix for generators
    f.write('param:' + '\t')
    for c in df_gen.columns:
        if c != 'name':
            f.write(c + '\t')
    f.write(':=\n\n')
    for i in range(0,len(df_gen)):    
        for c in df_gen.columns:
            if c == 'name':
                unit_name = df_gen.loc[i,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + '\t')  
            else:
                f.write(str((df_gen.loc[i,c])) + '\t')               
        f.write('\n')
    f.write(';\n\n')     

####### create parameter matrix for transmission paths (source and sink connections)
    f.write('param:' + '\t' + 'linemva' + '\t' +'linesus :=' + '\n')
    for z in all_nodes:
        for x in all_nodes:           
            f.write(z + '\t' + x + '\t')
            match = 0
            for p in range(0,len(df_paths)):
                source = df_paths.loc[p,'source']
                sink = df_paths.loc[p,'sink']
                if source == z and sink == x:
                    match = 1
                    p_match = p
            if match > 0:
                f.write(str(df_paths.loc[p_match,'linemva']) + '\t' + str(df_paths.loc[p_match,'linesus']) + '\n')
            else:
                f.write('0' + '\t' + '0' + '\n')
    f.write(';\n\n')

####### Hourly load and hydro
    # load (hourly)
    f.write('param:' + '\t' + 'SimDemand:=' + '\n')      
    for z in d_nodes:
        for h in range(0,len(df_load)): 
            f.write(z + '\t' + str(h+1) + '\t' + str(df_load.loc[h,z]) + '\n')
    f.write(';\n\n')

    # hydro (hourly)
    f.write('param:' + '\t' + 'SimHydro:=' + '\n')      
    for z in h_nodes:
        for h in range(0,len(df_hydro)): 
            f.write(z + '\t' + str(h+1) + '\t' + str(df_hydro.loc[h,z]) + '\n')
    f.write(';\n\n')

    # hydro (hourly)
    f.write('param:' + '\t' + 'SimHydroImport:=' + '\n')      
    for z in h_imports:
        for h in range(0,len(df_hydro_import)): 
            f.write(z + '\t' + str(h+1) + '\t' + str(df_hydro_import.loc[h,z]) + '\n')
    f.write(';\n\n')
    
###### System wide hourly reserve
    f.write('param' + '\t' + 'SimReserves:=' + '\n')
    for h in range(0,len(df_load)):
            f.write(str(h+1) + '\t' + str(df_reserves.loc[h,'Reserve']) + '\n')
    f.write(';\n\n')
    

print ('OK',curr_year)
