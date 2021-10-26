# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 13:13:27 2021

@author: tangh
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import datetime
import warnings
import os
import copy
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus']=False

GZ_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
GZ_data.sort_values(by=['date'],inplace = True)

#原表格构建
#定义参数
rf_1y = 0.0305 #投标的证金债
gz_1y = 0.0235
gz_6m = 0.021
gz_1d = 0.02

diff_gz_1y =rf_1y - gz_1y
diff_gz_6m = diff_gz_1y+0.0025
diff_gz_1d = diff_gz_1y

rf_6m = diff_gz_6m +gz_6m
rf_1d = gz_1d + diff_gz_1d

date_now1 = '2021/9/7'
date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
date_end = date_now+datetime.timedelta(days=365)

# date_mid = date_now + datetime.timedelta(days=int(365/2))
date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")

zj_data = pd.date_range(date_now,periods=366,freq ='D')
zj_data = pd.DataFrame(zj_data,columns = {'date'})
zj_data.set_index('date',inplace = True)

df_1 = 1/(1+rf_1y)
value_new = df_1*100*(1+rf_1y)
value_ty_1 = 100
error = 0

zj_data.loc[date_now,'rf'] = rf_1y
zj_data.loc[date_now,'DF'] = df_1
zj_data.loc[date_now,'value_new'] = value_new
zj_data.loc[date_now,'value_ty'] = value_ty_1
zj_data.loc[date_now,'rf_adj'] = rf_1y
zj_data.loc[date_now,'DF_adj'] = rf_1y
zj_data.loc[date_now,'value_adj'] = rf_1y

for i in range(len(zj_data)):
    date11 = zj_data.index[i]
    zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
    zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
    zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
    zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
    zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
    # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
    if date11 <= date_mid:
        zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid-date_now).days)*(rf_1y-rf_6m)
    
    if date11 > date_mid:
        zj_data.loc[date11,'rf_adj'] = rf_6m - ((date11 - date_mid).days)/((date_end-date_mid).days)*(rf_6m-rf_1d)
    
    zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
    zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
    zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2

zj_data['diff_new'] = zj_data['value_new'].diff()
zj_data['diff_ty'] = zj_data['value_ty'].diff()
zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']

total_error_new_ty = zj_data['error_new_ty'].sum()
total_error_adj_ty = zj_data['error_adj_ty'].sum()






#递推验证


####国债基准插点
#定义参数
#插点法，六个月
TB_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\投标利率.xlsx')
TB_data.sort_values(by=['date'],inplace = True)
TB_data.set_index('date',inplace=True)


GZ_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
GZ_data.sort_values(by=['date'],inplace = True)
GZ_data['gz_ytm_1d'] = GZ_data['DR001'].rolling(10).mean()

GZ_data.set_index('date',inplace=True)

GZ_data['tb_ytm'] = TB_data['tb_ytm']
GZ_data['tb_ytm'] = GZ_data['tb_ytm'].fillna(method='ffill')

# date_start = datetime.datetime.strptime('2019/9/7', "%Y/%m/%d")
date_start = datetime.datetime.strptime('2020/7/20', "%Y/%m/%d")
GZ_data1 = GZ_data.loc[date_start:,]

dict_error_new_ty = []
dict_error_adj_ty = []
for j in range(len(GZ_data1)):

    rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
    # gz_1y = 0.0235
    # gz_6m = 0.021
    # gz_1d = 0.02
    gz_1y = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1Y']/100
    gz_6m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_6m']/100
    gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
    
    
    diff_gz_1y =rf_1y - gz_1y
    diff_gz_6m = diff_gz_1y+0.0025
    diff_gz_1d = diff_gz_1y
    
    rf_6m = diff_gz_6m +gz_6m
    rf_1d = gz_1d + diff_gz_1d
    
    # date_now1 = '2021/9/7'
    # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
    date_now = GZ_data1.index[j]
    date_end = date_now+datetime.timedelta(days=365)
    
    date_mid = date_now + datetime.timedelta(days=int(365/2))
    # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
    
    zj_data = pd.date_range(date_now,periods=366,freq ='D')
    zj_data = pd.DataFrame(zj_data,columns = {'date'})
    zj_data.set_index('date',inplace = True)
    
    df_1 = 1/(1+rf_1y)
    value_new = df_1*100*(1+rf_1y)
    value_ty_1 = 100
    error = 0
    
    zj_data.loc[date_now,'rf'] = rf_1y
    zj_data.loc[date_now,'DF'] = df_1
    zj_data.loc[date_now,'value_new'] = value_new
    zj_data.loc[date_now,'value_ty'] = value_ty_1
    zj_data.loc[date_now,'rf_adj'] = rf_1y
    zj_data.loc[date_now,'DF_adj'] = rf_1y
    zj_data.loc[date_now,'value_adj'] = rf_1y
    
    for i in range(len(zj_data)):
        date11 = zj_data.index[i]
        zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
        zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
        zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
        zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
        zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
        # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
        if date11 <= date_mid:
            zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid-date_now).days)*(rf_1y-rf_6m)
        
        if date11 > date_mid:
            zj_data.loc[date11,'rf_adj'] = rf_6m - ((date11 - date_mid).days)/((date_end-date_mid).days)*(rf_6m-rf_1d)
        
        zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
        zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
        zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
    
    zj_data['diff_new'] = zj_data['value_new'].diff()
    zj_data['diff_ty'] = zj_data['value_ty'].diff()
    zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
    
    total_error_new_ty = zj_data['error_new_ty'].sum()
    total_error_adj_ty = zj_data['error_adj_ty'].sum()
    dict_error_new_ty.append(total_error_new_ty)
    dict_error_adj_ty.append(total_error_adj_ty)
    print(GZ_data1.index[j].date())
GZ_data2 = GZ_data1.copy()
GZ_data2['error_new_ty'] = dict_error_new_ty
GZ_data2['error_adj_6m_ty'] = dict_error_adj_ty
 
# GZ_data1[['error_new_ty','error_adj_ty','gz_ytm_1Y']].plot(secondary_y ='gz_ytm_1Y')

# writer = pd.ExcelWriter(r'C:\Users\tangh\Desktop\量化\ZJZ_model3.xlsx')
# GZ_data1[['error_new_ty','error_adj_ty','gz_ytm_1Y']].to_excel(writer,sheet_name= 'latest_signal')
# writer.save()
# writer.close() 



#递推验证
#定义参数
#插点法，三个月
TB_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\投标利率.xlsx')
TB_data.sort_values(by=['date'],inplace = True)
TB_data.set_index('date',inplace=True)


GZ_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
GZ_data.sort_values(by=['date'],inplace = True)
GZ_data['gz_ytm_1d'] = GZ_data['DR001'].rolling(10).mean()

GZ_data.set_index('date',inplace=True)

GZ_data['tb_ytm'] = TB_data['tb_ytm']
GZ_data['tb_ytm'] = GZ_data['tb_ytm'].fillna(method='ffill')

# date_start = datetime.datetime.strptime('2019/9/7', "%Y/%m/%d")
date_start = datetime.datetime.strptime('2020/7/20', "%Y/%m/%d")
GZ_data1 = GZ_data.loc[date_start:,]

dict_error_new_ty = []
dict_error_adj_ty = []
for j in range(len(GZ_data1)):

    rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
    # gz_1y = 0.0235
    # gz_3m = 0.021
    # gz_1d = 0.02
    gz_1y = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1Y']/100
    gz_3m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_3m']/100
    gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
    
    
    diff_gz_1y =rf_1y - gz_1y
    diff_gz_3m = diff_gz_1y
    diff_gz_1d = diff_gz_1y
    
    rf_3m = diff_gz_3m +gz_3m
    rf_1d = gz_1d + diff_gz_1d
    
    # date_now1 = '2021/9/7'
    # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
    date_now = GZ_data1.index[j]
    date_end = date_now+datetime.timedelta(days=365)
    
    date_mid = date_now + datetime.timedelta(days=int(365*3/4))
    # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
    
    zj_data = pd.date_range(date_now,periods=366,freq ='D')
    zj_data = pd.DataFrame(zj_data,columns = {'date'})
    zj_data.set_index('date',inplace = True)
    
    df_1 = 1/(1+rf_1y)
    value_new = df_1*100*(1+rf_1y)
    value_ty_1 = 100
    error = 0
    
    zj_data.loc[date_now,'rf'] = rf_1y
    zj_data.loc[date_now,'DF'] = df_1
    zj_data.loc[date_now,'value_new'] = value_new
    zj_data.loc[date_now,'value_ty'] = value_ty_1
    zj_data.loc[date_now,'rf_adj'] = rf_1y
    zj_data.loc[date_now,'DF_adj'] = rf_1y
    zj_data.loc[date_now,'value_adj'] = rf_1y
    
    for i in range(len(zj_data)):
        date11 = zj_data.index[i]
        zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
        zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
        zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
        zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
        zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
        # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
        if date11 <= date_mid:
            zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid-date_now).days)*(rf_1y-rf_3m)
        
        if date11 > date_mid:
            zj_data.loc[date11,'rf_adj'] = rf_3m - ((date11 - date_mid).days)/((date_end-date_mid).days)*(rf_3m-rf_1d)
        
        zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
        zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
        zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
    
    zj_data['diff_new'] = zj_data['value_new'].diff()
    zj_data['diff_ty'] = zj_data['value_ty'].diff()
    zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
    
    total_error_new_ty = zj_data['error_new_ty'].sum()
    total_error_adj_ty = zj_data['error_adj_ty'].sum()
    dict_error_new_ty.append(total_error_new_ty)
    dict_error_adj_ty.append(total_error_adj_ty)
    print(GZ_data1.index[j].date())
GZ_data2['error_new_ty'] = dict_error_new_ty
GZ_data2['error_adj_3m_ty'] = dict_error_adj_ty

#递推验证
#定义参数
#插点法，九个月
TB_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\投标利率.xlsx')
TB_data.sort_values(by=['date'],inplace = True)
TB_data.set_index('date',inplace=True)


GZ_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
GZ_data.sort_values(by=['date'],inplace = True)
GZ_data['gz_ytm_1d'] = GZ_data['DR001'].rolling(10).mean()

GZ_data.set_index('date',inplace=True)

GZ_data['tb_ytm'] = TB_data['tb_ytm']
GZ_data['tb_ytm'] = GZ_data['tb_ytm'].fillna(method='ffill')

# date_start = datetime.datetime.strptime('2019/9/7', "%Y/%m/%d")
date_start = datetime.datetime.strptime('2020/7/20', "%Y/%m/%d")
GZ_data1 = GZ_data.loc[date_start:,]

dict_error_new_ty = []
dict_error_adj_ty = []
for j in range(len(GZ_data1)):

    rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
    # gz_1y = 0.0235
    # gz_9m = 0.021
    # gz_1d = 0.02
    gz_1y = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1Y']/100
    gz_9m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_9m']/100
    gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
    
    
    diff_gz_1y =rf_1y - gz_1y
    diff_gz_9m = diff_gz_1y
    diff_gz_1d = diff_gz_1y
    
    rf_9m = diff_gz_9m +gz_9m
    rf_1d = gz_1d + diff_gz_1d
    
    # date_now1 = '2021/9/7'
    # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
    date_now = GZ_data1.index[j]
    date_end = date_now+datetime.timedelta(days=365)
    
    date_mid = date_now + datetime.timedelta(days=int(365/4))
    # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
    
    zj_data = pd.date_range(date_now,periods=366,freq ='D')
    zj_data = pd.DataFrame(zj_data,columns = {'date'})
    zj_data.set_index('date',inplace = True)
    
    df_1 = 1/(1+rf_1y)
    value_new = df_1*100*(1+rf_1y)
    value_ty_1 = 100
    error = 0
    
    zj_data.loc[date_now,'rf'] = rf_1y
    zj_data.loc[date_now,'DF'] = df_1
    zj_data.loc[date_now,'value_new'] = value_new
    zj_data.loc[date_now,'value_ty'] = value_ty_1
    zj_data.loc[date_now,'rf_adj'] = rf_1y
    zj_data.loc[date_now,'DF_adj'] = rf_1y
    zj_data.loc[date_now,'value_adj'] = rf_1y
    
    for i in range(len(zj_data)):
        date11 = zj_data.index[i]
        zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
        zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
        zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
        zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
        zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
        # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
        if date11 <= date_mid:
            zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid-date_now).days)*(rf_1y-rf_9m)
        
        if date11 > date_mid:
            zj_data.loc[date11,'rf_adj'] = rf_9m - ((date11 - date_mid).days)/((date_end-date_mid).days)*(rf_9m-rf_1d)
        
        zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
        zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
        zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
    
    zj_data['diff_new'] = zj_data['value_new'].diff()
    zj_data['diff_ty'] = zj_data['value_ty'].diff()
    zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
    
    total_error_new_ty = zj_data['error_new_ty'].sum()
    total_error_adj_ty = zj_data['error_adj_ty'].sum()
    dict_error_new_ty.append(total_error_new_ty)
    dict_error_adj_ty.append(total_error_adj_ty)
    print(GZ_data1.index[j].date())
GZ_data2['error_new_ty'] = dict_error_new_ty
GZ_data2['error_adj_9m_ty'] = dict_error_adj_ty

#递推验证
#定义参数
#插点法，3,6,9的点
TB_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\投标利率.xlsx')
TB_data.sort_values(by=['date'],inplace = True)
TB_data.set_index('date',inplace=True)


GZ_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
GZ_data.sort_values(by=['date'],inplace = True)
GZ_data['gz_ytm_1d'] = GZ_data['DR001'].rolling(10).mean()

GZ_data.set_index('date',inplace=True)

GZ_data['tb_ytm'] = TB_data['tb_ytm']
GZ_data['tb_ytm'] = GZ_data['tb_ytm'].fillna(method='ffill')

# date_start = datetime.datetime.strptime('2019/9/7', "%Y/%m/%d")
date_start = datetime.datetime.strptime('2020/7/20', "%Y/%m/%d")
GZ_data1 = GZ_data.loc[date_start:,]

dict_error_new_ty = []
dict_error_adj_ty = []
for j in range(len(GZ_data1)):

    rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
    # gz_1y = 0.0235
    # gz_9m = 0.021
    # gz_1d = 0.02
    gz_1y = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1Y']/100
    gz_3m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_3m']/100    
    gz_6m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_6m']/100    
    gz_9m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_9m']/100
    gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
    
    
    diff_gz_1y =rf_1y - gz_1y
    diff_gz_3m = diff_gz_1y+0.0025    
    diff_gz_6m = diff_gz_1y+0.0025    
    diff_gz_9m = diff_gz_1y+0.0025
    diff_gz_1d = diff_gz_1y
    
    rf_3m = diff_gz_3m +gz_3m    
    rf_6m = diff_gz_6m +gz_6m    
    rf_9m = diff_gz_9m +gz_9m
    rf_1d = gz_1d + diff_gz_1d
    
    # date_now1 = '2021/9/7'
    # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
    date_now = GZ_data1.index[j]
    date_end = date_now+datetime.timedelta(days=365)
    
    date_mid_3m = date_now + datetime.timedelta(days=int(365/4))    
    date_mid_6m = date_now + datetime.timedelta(days=int(365/2))    
    date_mid_9m = date_now + datetime.timedelta(days=int(365*3/4))
    # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
    
    zj_data = pd.date_range(date_now,periods=366,freq ='D')
    zj_data = pd.DataFrame(zj_data,columns = {'date'})
    zj_data.set_index('date',inplace = True)
    
    df_1 = 1/(1+rf_1y)
    value_new = df_1*100*(1+rf_1y)
    value_ty_1 = 100
    error = 0
    
    zj_data.loc[date_now,'rf'] = rf_1y
    zj_data.loc[date_now,'DF'] = df_1
    zj_data.loc[date_now,'value_new'] = value_new
    zj_data.loc[date_now,'value_ty'] = value_ty_1
    zj_data.loc[date_now,'rf_adj'] = rf_1y
    zj_data.loc[date_now,'DF_adj'] = rf_1y
    zj_data.loc[date_now,'value_adj'] = rf_1y
    
    for i in range(len(zj_data)):
        date11 = zj_data.index[i]
        zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
        zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
        zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
        zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
        zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
        # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
        if date11 <= date_mid_3m:
            zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid_3m-date_now).days)*(rf_1y-rf_9m)
        
        elif (date11 > date_mid_3m)&(date11 <= date_mid_6m):
            zj_data.loc[date11,'rf_adj'] = rf_9m - ((date11 - date_mid_3m).days)/((date_mid_6m-date_mid_3m).days)*(rf_9m-rf_6m)

        elif (date11 > date_mid_6m)&(date11 <= date_mid_9m):
            zj_data.loc[date11,'rf_adj'] = rf_6m - ((date11 - date_mid_6m).days)/((date_mid_9m-date_mid_6m).days)*(rf_6m-rf_3m)  
        else:
            zj_data.loc[date11,'rf_adj'] = rf_3m - ((date11 - date_mid_9m).days)/((date_end-date_mid_9m).days)*(rf_3m-rf_1d)              
            
        zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
        zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
        zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
    
    zj_data['diff_new'] = zj_data['value_new'].diff()
    zj_data['diff_ty'] = zj_data['value_ty'].diff()
    zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
    
    total_error_new_ty = zj_data['error_new_ty'].sum()
    total_error_adj_ty = zj_data['error_adj_ty'].sum()
    dict_error_new_ty.append(total_error_new_ty)
    dict_error_adj_ty.append(total_error_adj_ty)
    print(GZ_data1.index[j].date())
GZ_data2['error_new_ty'] = dict_error_new_ty
GZ_data2['error_adj_3_6_9_ty'] = dict_error_adj_ty

#递推验证
#定义参数
#插点法，六个月与九个月的点
TB_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\投标利率.xlsx')
TB_data.sort_values(by=['date'],inplace = True)
TB_data.set_index('date',inplace=True)


GZ_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
GZ_data.sort_values(by=['date'],inplace = True)
GZ_data['gz_ytm_1d'] = GZ_data['DR001'].rolling(10).mean()

GZ_data.set_index('date',inplace=True)

GZ_data['tb_ytm'] = TB_data['tb_ytm']
GZ_data['tb_ytm'] = GZ_data['tb_ytm'].fillna(method='ffill')

# date_start = datetime.datetime.strptime('2019/9/7', "%Y/%m/%d")
date_start = datetime.datetime.strptime('2020/7/20', "%Y/%m/%d")
GZ_data1 = GZ_data.loc[date_start:,]

dict_error_new_ty = []
dict_error_adj_ty = []
for j in range(len(GZ_data1)):

    rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
    # gz_1y = 0.0235
    # gz_9m = 0.021
    # gz_1d = 0.02
    gz_1y = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1Y']/100
    gz_3m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_3m']/100    
    gz_6m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_6m']/100    
    gz_9m = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_9m']/100
    gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
    
    
    diff_gz_1y =rf_1y - gz_1y
    diff_gz_3m = diff_gz_1y+0.0025    
    diff_gz_6m = diff_gz_1y+0.0025    
    diff_gz_9m = diff_gz_1y+0.0025
    diff_gz_1d = diff_gz_1y
    
    rf_3m = diff_gz_3m +gz_3m    
    rf_6m = diff_gz_6m +gz_6m    
    rf_9m = diff_gz_9m +gz_9m
    rf_1d = gz_1d + diff_gz_1d
    
    # date_now1 = '2021/9/7'
    # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
    date_now = GZ_data1.index[j]
    date_end = date_now+datetime.timedelta(days=365)
    
    date_mid_3m = date_now + datetime.timedelta(days=int(365/4))    
    date_mid_6m = date_now + datetime.timedelta(days=int(365/2))    
    date_mid_9m = date_now + datetime.timedelta(days=int(365*3/4))
    # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
    
    zj_data = pd.date_range(date_now,periods=366,freq ='D')
    zj_data = pd.DataFrame(zj_data,columns = {'date'})
    zj_data.set_index('date',inplace = True)
    
    df_1 = 1/(1+rf_1y)
    value_new = df_1*100*(1+rf_1y)
    value_ty_1 = 100
    error = 0
    
    zj_data.loc[date_now,'rf'] = rf_1y
    zj_data.loc[date_now,'DF'] = df_1
    zj_data.loc[date_now,'value_new'] = value_new
    zj_data.loc[date_now,'value_ty'] = value_ty_1
    zj_data.loc[date_now,'rf_adj'] = rf_1y
    zj_data.loc[date_now,'DF_adj'] = rf_1y
    zj_data.loc[date_now,'value_adj'] = rf_1y
    
    for i in range(len(zj_data)):
        date11 = zj_data.index[i]
        zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
        zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
        zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
        zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
        zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
        # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
        if date11 <= date_mid_3m:
            zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid_3m-date_now).days)*(rf_1y-rf_9m)

        elif (date11 > date_mid_3m)&(date11 <= date_mid_6m):
            zj_data.loc[date11,'rf_adj'] = rf_9m - ((date11 - date_mid_3m).days)/((date_mid_6m-date_mid_3m).days)*(rf_9m-rf_6m)  
        else:
            zj_data.loc[date11,'rf_adj'] = rf_6m - ((date11 - date_mid_6m).days)/((date_end-date_mid_6m).days)*(rf_6m-rf_1d)              
            
        zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
        zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
        zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
    
    zj_data['diff_new'] = zj_data['value_new'].diff()
    zj_data['diff_ty'] = zj_data['value_ty'].diff()
    zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
    
    total_error_new_ty = zj_data['error_new_ty'].sum()
    total_error_adj_ty = zj_data['error_adj_ty'].sum()
    dict_error_new_ty.append(total_error_new_ty)
    dict_error_adj_ty.append(total_error_adj_ty)
    print(GZ_data1.index[j].date())
GZ_data2['error_new_ty'] = dict_error_new_ty
GZ_data2['error_adj_6_9_ty'] = dict_error_adj_ty





####遍历回归验证
####国开债基准插点
#定义参数
#调整点差
#导入数据
TB_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\投标利率.xlsx')
TB_data.sort_values(by=['date'],inplace = True)
TB_data.set_index('date',inplace=True)


GZ_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
GZ_data.sort_values(by=['date'],inplace = True)
GZ_data['gz_ytm_1d'] = GZ_data['DR001'].rolling(10).mean()

GZ_data.set_index('date',inplace=True)

GZ_data['tb_ytm'] = TB_data['tb_ytm']
GZ_data.loc['2020-06-1','tb_ytm'] = 3.3
GZ_data['tb_ytm'] = GZ_data['tb_ytm'].fillna(method='ffill')
GZ_data['mlf_ytm_1Y'] = GZ_data['mlf_ytm_1Y'].fillna(method='ffill')



#划定范围
# date_start = datetime.datetime.strptime('2019/9/7', "%Y/%m/%d")
date_start = datetime.datetime.strptime('2020/6/1', "%Y/%m/%d")
GZ_data1 = GZ_data.loc[date_start:,]

#权重设置
weight_gz = 0.2
weight_gy = 0.2
weight_mlf = 0.2




#逐月调整方法
# origin_data = GZ_data1.copy()
# origin_data['date1'] = origin_data.index
# origin_data['date2'] = origin_data.index
# origin_data['date2'] = origin_data['date2'].dt.strftime("%Y-%m")
# # origin_data['date2'] = origin_data['date2'].apply(lambda x:x.month)
# month_mean_data = origin_data.groupby(origin_data['date2']).mean()
# month_mean_data =month_mean_data.shift(1)

# month_mean_data.columns = month_mean_data.columns + '_rol1m'

# origin_data = origin_data.merge(month_mean_data,on='date2')
# origin_data.set_index('date1',inplace=True)

# bond_dict =['gk','nf','jck','ncd','gz']
bond_dict =['gz']

# #滚动优化方法
origin_data = GZ_data1.copy()
for data_ in origin_data.columns:
    # origin_data[data_+'_rol5'] = origin_data[data_].rolling(5).mean().shift(1)
    origin_data[data_+'_rol1m'] = origin_data[data_]
# for data_ in origin_data.columns:
#     origin_data[data_+'_rol5'] = origin_data[data_].rolling(30).mean().shift(1)
#     origin_data[data_+'_rol5'] = origin_data[data_]
#计算加点值
for kind in bond_dict:
     origin_data[kind+'_add_1Y'] = origin_data['tb_ytm']-origin_data[kind+'_ytm_1Y_rol1m']
     origin_data[kind+'_add_9m'] = origin_data['tb_ytm']-origin_data[kind+'_ytm_9m_rol1m']-origin_data[kind+'_add_1Y']
     origin_data[kind+'_add_6m'] = origin_data['tb_ytm']-origin_data[kind+'_ytm_6m_rol1m']-origin_data[kind+'_add_1Y']
     origin_data[kind+'_add_3m'] = origin_data['tb_ytm']-origin_data[kind+'_ytm_3m_rol1m']-origin_data[kind+'_add_1Y']

#时间跨度
ff_data = pd.date_range('2020-07-01','2021-09-30',freq ='D')
ff_data = pd.DataFrame(ff_data,columns = {'date'})
ff_data.set_index('date',inplace = True)


#回测区间
ee_data = pd.date_range('2020-07-01','2020-09-01',freq ='D')
ee_data = pd.DataFrame(ee_data,columns = {'date'})
ee_data.set_index('date',inplace = True)
back_test_span = len(ee_data)


origin_data = ff_data.merge(origin_data,left_index=True,right_index=True,how = 'left')
origin_data = origin_data.fillna(method = 'ffill')

#重置各种数据
TB_data_origin = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\投标利率.xlsx')
TB_data_origin.sort_values(by=['date'],inplace = True)
TB_data_origin.set_index('date',inplace=True)


GZ_data_origin = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
GZ_data_origin.sort_values(by=['date'],inplace = True)
GZ_data_origin['gz_ytm_1d'] = GZ_data_origin['DR001'].rolling(10).mean()

GZ_data_origin.set_index('date',inplace=True)
GZ_data_origin['mlf_ytm_1Y'] = GZ_data_origin['mlf_ytm_1Y'].fillna(method='ffill')

#填充国债利率，非工作日
GZ_data_origin = ff_data.merge(GZ_data_origin,left_index=True,right_index=True,how = 'left')
GZ_data_origin = GZ_data_origin.fillna(method = 'ffill')


GZ_data_origin['tb_ytm'] = TB_data_origin['tb_ytm']
GZ_data_origin['tb_ytm'] = GZ_data_origin['tb_ytm'].fillna(method='ffill')

# date_start = datetime.datetime.strptime('2019/9/7', "%Y/%m/%d")
date_start = datetime.datetime.strptime('2020/7/1', "%Y/%m/%d")
GZ_data1_origin = GZ_data_origin.loc[date_start:,]



#开始计算六个月的插值
# bond_dict =['gk','nf','jck','ncd','gz']
bond_dict =['gz']
bond_list = []
for bond_name in bond_dict:
    
    # TB_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\投标利率.xlsx')
    # TB_data.sort_values(by=['date'],inplace = True)
    # TB_data.set_index('date',inplace=True)
    
    
    # GZ_data = pd.read_excel(r'C:\Users\tangh\Desktop\量化\证金债估值测试\中债国债收益率曲线.xlsx')
    # GZ_data.sort_values(by=['date'],inplace = True)
    # GZ_data['gz_ytm_1d'] = GZ_data['DR001'].rolling(10).mean()
    
    # GZ_data.set_index('date',inplace=True)
    
    # #填充国债利率，非工作日
    # GZ_data = ff_data.merge(GZ_data,left_index=True,right_index=True,how = 'left')
    # GZ_data = GZ_data.fillna(method = 'ffill')
    
    
    # GZ_data['tb_ytm'] = TB_data['tb_ytm']
    # GZ_data['tb_ytm'] = GZ_data['tb_ytm'].fillna(method='ffill')
    
    # # date_start = datetime.datetime.strptime('2019/9/7', "%Y/%m/%d")
    # date_start = datetime.datetime.strptime('2020/7/1', "%Y/%m/%d")
    # GZ_data1 = GZ_data.loc[date_start:,]
    

    
    
    dict_error_new_ty = []
    dict_error_adj_ty = []
    dict_maxdrawdown_adj = []
    for j in range(back_test_span):
        GZ_data1 = GZ_data1_origin.copy()
    
        rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
        # gz_1y = 0.0235
        # gz_6m = 0.021
        # gz_1d = 0.02
        gz_1y = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_1Y']/100
        gz_6m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_6m']/100
        gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
        
        
        diff_gz_1y =rf_1y - gz_1y
        diff_gz_6m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_6m'])/100
        diff_gz_1d = diff_gz_1y
        
        rf_6m = diff_gz_6m +gz_6m
        rf_1d = gz_1d + diff_gz_1d
        
        # date_now1 = '2021/9/7'
        # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
        date_now = GZ_data1.index[j]
        date_end = date_now+datetime.timedelta(days=365)
        
        date_mid = date_now + datetime.timedelta(days=int(365/2))
        # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
        
        zj_data = pd.date_range(date_now,periods=366,freq ='D')
        zj_data = pd.DataFrame(zj_data,columns = {'date'})
        zj_data.set_index('date',inplace = True)
        
        df_1 = 1/(1+rf_1y)
        value_new = df_1*100*(1+rf_1y)
        value_ty_1 = 100
        error = 0
        
        zj_data.loc[date_now,'rf'] = rf_1y
        zj_data.loc[date_now,'DF'] = df_1
        zj_data.loc[date_now,'value_new'] = value_new
        zj_data.loc[date_now,'value_ty'] = value_ty_1
        zj_data.loc[date_now,'rf_adj'] = rf_1y
        zj_data.loc[date_now,'DF_adj'] = rf_1y
        zj_data.loc[date_now,'value_adj'] = rf_1y
  
        #加权mlf利率
        GZ_data1['gz_ytm_1d_new'] = GZ_data1['gz_ytm_1d']        
        GZ_data1['gz_ytm_3m_new'] = GZ_data1['gz_ytm_3m']
        GZ_data1['gz_ytm_6m_new'] = GZ_data1['gz_ytm_6m']
        GZ_data1['gz_ytm_9m_new'] = GZ_data1['gz_ytm_9m']
        GZ_data1['gz_ytm_1Y_new'] = GZ_data1['gz_ytm_1Y']

        gz_zj_diff_1d = GZ_data1.loc[date_now,'gz_ytm_1d'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_3m = GZ_data1.loc[date_now,'gz_ytm_3m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_6m = GZ_data1.loc[date_now,'gz_ytm_6m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']        
        gz_zj_diff_9m = GZ_data1.loc[date_now,'gz_ytm_9m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_1Y = GZ_data1.loc[date_now,'gz_ytm_1Y'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        

        GZ_data1['gz_ytm_1d'] = (1-weight_gy)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1d) +weight_gy*GZ_data1['gz_ytm_1d_new']
        GZ_data1['gz_ytm_3m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_3m) +weight_gz*GZ_data1['gz_ytm_3m_new']        
        GZ_data1['gz_ytm_6m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_6m) +weight_gz*GZ_data1['gz_ytm_6m_new']
        GZ_data1['gz_ytm_9m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_9m) +weight_gz*GZ_data1['gz_ytm_9m_new']        
        GZ_data1['gz_ytm_1Y'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1Y) +weight_gz*GZ_data1['gz_ytm_1Y_new']

        
        
        for i in range(len(zj_data)):
            #导入动态利率
            # rf_1y = GZ_data1.loc[zj_data.index[i],'tb_ytm']/100 #投标的证金债
            # gz_1y = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_1Y']/100
            gz_3m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_3m']/100    
            gz_6m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_6m']/100    
            gz_9m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_9m']/100
            gz_1d = GZ_data1.loc[zj_data.index[i],'gz_ytm_1d']/100
            
            
            # diff_gz_1y =rf_1y - gz_1y
            diff_gz_3m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_3m'])/100   
            diff_gz_6m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_6m'])/100    
            diff_gz_9m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_9m'])/100
            diff_gz_1d = diff_gz_1y
            
            rf_3m = diff_gz_3m +gz_3m    
            rf_6m = diff_gz_6m +gz_6m    
            rf_9m = diff_gz_9m +gz_9m
            rf_1d = gz_1d + diff_gz_1d            
            
        
            date11 = zj_data.index[i]
            zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
            zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
            zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
            zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
            zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
            # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
            if date11 <= date_mid:
                zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid-date_now).days)*(rf_1y-rf_6m)
            
            if date11 > date_mid:
                zj_data.loc[date11,'rf_adj'] = rf_6m - ((date11 - date_mid).days)/((date_end-date_mid).days)*(rf_6m-rf_1d)
            
            zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
            zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
            zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
        
        zj_data['diff_new'] = zj_data['value_new'].diff()
        zj_data['diff_ty'] = zj_data['value_ty'].diff()
        zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
        #计算最大回撤
        for k in range(len(zj_data)-1):       
            zj_data.loc[zj_data.index[k+1],'value_adj_drawdown'] = zj_data.loc[zj_data.index[0:k],'value_adj'].max()-zj_data.loc[zj_data.index[k+1],'value_adj']
        
        
        maxdrawdown_adj = zj_data['value_adj_drawdown'].max()             
        total_error_new_ty = zj_data['error_new_ty'].sum()
        total_error_adj_ty = zj_data['error_adj_ty'].sum()
        
        
        dict_error_new_ty.append(total_error_new_ty)
        dict_error_adj_ty.append(total_error_adj_ty)
        dict_maxdrawdown_adj.append(maxdrawdown_adj)
        
        
        print(GZ_data1.index[j].date())
    # GZ_data2 = GZ_data1.copy()
    ee_data['error_new_ty'] = dict_error_new_ty
    ee_data['error_adj_6m_ty'] = dict_error_adj_ty
    ee_data['maxdrawdown_adj_6m'] = dict_maxdrawdown_adj
     
    # GZ_data1[['error_new_ty','error_adj_ty','gz_ytm_1Y']].plot(secondary_y ='gz_ytm_1Y')
    
    # writer = pd.ExcelWriter(r'C:\Users\tangh\Desktop\量化\ZJZ_model3.xlsx')
    # GZ_data1[['error_new_ty','error_adj_ty','gz_ytm_1Y']].to_excel(writer,sheet_name= 'latest_signal')
    # writer.save()
    # writer.close() 
    
    
    
    #递推验证
    #定义参数
    #插点法，三个月
    
    
    dict_error_new_ty = []
    dict_error_adj_ty = []
    dict_maxdrawdown_adj = []
    for j in range(back_test_span):
        
        GZ_data1 = GZ_data1_origin.copy()
    
        rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
        # gz_1y = 0.0235
        # gz_3m = 0.021
        # gz_1d = 0.02
        gz_1y = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_1Y']/100
        gz_3m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_3m']/100
        gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
        
        
        diff_gz_1y =rf_1y - gz_1y
        diff_gz_3m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_3m'])/100
        diff_gz_1d = diff_gz_1y
        
        rf_3m = diff_gz_3m +gz_3m
        rf_1d = gz_1d + diff_gz_1d
        
        # date_now1 = '2021/9/7'
        # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
        date_now = GZ_data1.index[j]
        date_end = date_now+datetime.timedelta(days=365)
        
        date_mid = date_now + datetime.timedelta(days=int(365*3/4))
        # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
        
        zj_data = pd.date_range(date_now,periods=366,freq ='D')
        zj_data = pd.DataFrame(zj_data,columns = {'date'})
        zj_data.set_index('date',inplace = True)
        
        df_1 = 1/(1+rf_1y)
        value_new = df_1*100*(1+rf_1y)
        value_ty_1 = 100
        error = 0
        
        zj_data.loc[date_now,'rf'] = rf_1y
        zj_data.loc[date_now,'DF'] = df_1
        zj_data.loc[date_now,'value_new'] = value_new
        zj_data.loc[date_now,'value_ty'] = value_ty_1
        zj_data.loc[date_now,'rf_adj'] = rf_1y
        zj_data.loc[date_now,'DF_adj'] = rf_1y
        zj_data.loc[date_now,'value_adj'] = rf_1y
        
    
        #加权mlf利率
        GZ_data1['gz_ytm_1d_new'] = GZ_data1['gz_ytm_1d']        
        GZ_data1['gz_ytm_3m_new'] = GZ_data1['gz_ytm_3m']
        GZ_data1['gz_ytm_6m_new'] = GZ_data1['gz_ytm_6m']
        GZ_data1['gz_ytm_9m_new'] = GZ_data1['gz_ytm_9m']
        GZ_data1['gz_ytm_1Y_new'] = GZ_data1['gz_ytm_1Y']

        gz_zj_diff_1d = GZ_data1.loc[date_now,'gz_ytm_1d'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_3m = GZ_data1.loc[date_now,'gz_ytm_3m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_6m = GZ_data1.loc[date_now,'gz_ytm_6m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']        
        gz_zj_diff_9m = GZ_data1.loc[date_now,'gz_ytm_9m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_1Y = GZ_data1.loc[date_now,'gz_ytm_1Y'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        

        GZ_data1['gz_ytm_1d'] = (1-weight_gy)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1d) +weight_gy*GZ_data1['gz_ytm_1d_new']
        GZ_data1['gz_ytm_3m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_3m) +weight_gz*GZ_data1['gz_ytm_3m_new']        
        GZ_data1['gz_ytm_6m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_6m) +weight_gz*GZ_data1['gz_ytm_6m_new']
        GZ_data1['gz_ytm_9m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_9m) +weight_gz*GZ_data1['gz_ytm_9m_new']        
        GZ_data1['gz_ytm_1Y'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1Y) +weight_gz*GZ_data1['gz_ytm_1Y_new']
        
        for i in range(len(zj_data)):
            # rf_1y = GZ_data1.loc[zj_data.index[i],'tb_ytm']/100 #投标的证金债
            # gz_1y = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_1Y']/100
            gz_3m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_3m']/100    
            gz_6m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_6m']/100    
            gz_9m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_9m']/100
            gz_1d = GZ_data1.loc[zj_data.index[i],'gz_ytm_1d']/100
            
            
            # diff_gz_1y =rf_1y - gz_1y
            diff_gz_3m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_3m'])/100   
            diff_gz_6m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_6m'])/100    
            diff_gz_9m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_9m'])/100
            diff_gz_1d = diff_gz_1y
            
            rf_3m = diff_gz_3m +gz_3m    
            rf_6m = diff_gz_6m +gz_6m    
            rf_9m = diff_gz_9m +gz_9m
            rf_1d = gz_1d + diff_gz_1d            
                      
            
            date11 = zj_data.index[i]
            zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
            zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
            zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
            zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
            zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
            # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
            if date11 <= date_mid:
                zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid-date_now).days)*(rf_1y-rf_3m)
            
            if date11 > date_mid:
                zj_data.loc[date11,'rf_adj'] = rf_3m - ((date11 - date_mid).days)/((date_end-date_mid).days)*(rf_3m-rf_1d)
            
            zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
            zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
            zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
        
        zj_data['diff_new'] = zj_data['value_new'].diff()
        zj_data['diff_ty'] = zj_data['value_ty'].diff()
        zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
        
        #计算最大回撤
        for k in range(len(zj_data)-1):       
            zj_data.loc[zj_data.index[k+1],'value_adj_drawdown'] = zj_data.loc[zj_data.index[0:k],'value_adj'].max()-zj_data.loc[zj_data.index[k+1],'value_adj']
        
        
        maxdrawdown_adj = zj_data['value_adj_drawdown'].max()             
        total_error_new_ty = zj_data['error_new_ty'].sum()
        total_error_adj_ty = zj_data['error_adj_ty'].sum()
        
        
        dict_error_new_ty.append(total_error_new_ty)
        dict_error_adj_ty.append(total_error_adj_ty)
        dict_maxdrawdown_adj.append(maxdrawdown_adj)
        print(GZ_data1.index[j].date())
    ee_data['error_new_ty'] = dict_error_new_ty
    ee_data['error_adj_3m_ty'] = dict_error_adj_ty
    ee_data['maxdrawdown_adj_3m'] = dict_maxdrawdown_adj
    
    #递推验证
    #定义参数
    #插点法，九个月
    
    dict_error_new_ty = []
    dict_error_adj_ty = []
    dict_maxdrawdown_adj = []
    for j in range(back_test_span):
        GZ_data1 = GZ_data1_origin.copy()
    
        rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
        # gz_1y = 0.0235
        # gz_9m = 0.021
        # gz_1d = 0.02
        gz_1y = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_1Y']/100
        gz_9m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_9m']/100
        gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
        
        
        diff_gz_1y =rf_1y - gz_1y
        diff_gz_9m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_9m'])/100
        diff_gz_1d = diff_gz_1y
        
        rf_9m = diff_gz_9m +gz_9m
        rf_1d = gz_1d + diff_gz_1d
        
        # date_now1 = '2021/9/7'
        # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
        date_now = GZ_data1.index[j]
        date_end = date_now+datetime.timedelta(days=365)
        
        date_mid = date_now + datetime.timedelta(days=int(365/4))
        # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
        
        zj_data = pd.date_range(date_now,periods=366,freq ='D')
        zj_data = pd.DataFrame(zj_data,columns = {'date'})
        zj_data.set_index('date',inplace = True)
        
        df_1 = 1/(1+rf_1y)
        value_new = df_1*100*(1+rf_1y)
        value_ty_1 = 100
        error = 0
        
        zj_data.loc[date_now,'rf'] = rf_1y
        zj_data.loc[date_now,'DF'] = df_1
        zj_data.loc[date_now,'value_new'] = value_new
        zj_data.loc[date_now,'value_ty'] = value_ty_1
        zj_data.loc[date_now,'rf_adj'] = rf_1y
        zj_data.loc[date_now,'DF_adj'] = rf_1y
        zj_data.loc[date_now,'value_adj'] = rf_1y
        
        
        #加权mlf利率
        GZ_data1['gz_ytm_1d_new'] = GZ_data1['gz_ytm_1d']        
        GZ_data1['gz_ytm_3m_new'] = GZ_data1['gz_ytm_3m']
        GZ_data1['gz_ytm_6m_new'] = GZ_data1['gz_ytm_6m']
        GZ_data1['gz_ytm_9m_new'] = GZ_data1['gz_ytm_9m']
        GZ_data1['gz_ytm_1Y_new'] = GZ_data1['gz_ytm_1Y']

        gz_zj_diff_1d = GZ_data1.loc[date_now,'gz_ytm_1d'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_3m = GZ_data1.loc[date_now,'gz_ytm_3m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_6m = GZ_data1.loc[date_now,'gz_ytm_6m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']        
        gz_zj_diff_9m = GZ_data1.loc[date_now,'gz_ytm_9m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_1Y = GZ_data1.loc[date_now,'gz_ytm_1Y'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        

        GZ_data1['gz_ytm_1d'] = (1-weight_gy)*(GZ_data1.loc[date_now,'mlf_ytm_1Y'] + gz_zj_diff_1d) +weight_gy*GZ_data1['gz_ytm_1d_new']
        GZ_data1['gz_ytm_3m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_3m) +weight_gz*GZ_data1['gz_ytm_3m_new']        
        GZ_data1['gz_ytm_6m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_6m) +weight_gz*GZ_data1['gz_ytm_6m_new']
        GZ_data1['gz_ytm_9m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_9m) +weight_gz*GZ_data1['gz_ytm_9m_new']        
        GZ_data1['gz_ytm_1Y'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1Y) +weight_gz*GZ_data1['gz_ytm_1Y_new']
        
        for i in range(len(zj_data)):
            # rf_1y = GZ_data1.loc[zj_data.index[i],'tb_ytm']/100 #投标的证金债
            # gz_1y = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_1Y']/100
            gz_3m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_3m']/100    
            gz_6m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_6m']/100    
            gz_9m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_9m']/100
            gz_1d = GZ_data1.loc[zj_data.index[i],'gz_ytm_1d']/100
            
            
            # diff_gz_1y =rf_1y - gz_1y
            diff_gz_3m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_3m'])/100   
            diff_gz_6m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_6m'])/100    
            diff_gz_9m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_9m'])/100
            diff_gz_1d = diff_gz_1y
            
            rf_3m = diff_gz_3m +gz_3m    
            rf_6m = diff_gz_6m +gz_6m    
            rf_9m = diff_gz_9m +gz_9m
            rf_1d = gz_1d + diff_gz_1d                  
            
            
            date11 = zj_data.index[i]
            zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
            zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
            zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
            zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
            zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
            # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
            if date11 <= date_mid:
                zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid-date_now).days)*(rf_1y-rf_9m)
            
            if date11 > date_mid:
                zj_data.loc[date11,'rf_adj'] = rf_9m - ((date11 - date_mid).days)/((date_end-date_mid).days)*(rf_9m-rf_1d)
            
            zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
            zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
            zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
        
        zj_data['diff_new'] = zj_data['value_new'].diff()
        zj_data['diff_ty'] = zj_data['value_ty'].diff()
        zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
        
        #计算最大回撤
        for k in range(len(zj_data)-1):       
            zj_data.loc[zj_data.index[k+1],'value_adj_drawdown'] = zj_data.loc[zj_data.index[0:k],'value_adj'].max()-zj_data.loc[zj_data.index[k+1],'value_adj']
        
        
        maxdrawdown_adj = zj_data['value_adj_drawdown'].max()             
        total_error_new_ty = zj_data['error_new_ty'].sum()
        total_error_adj_ty = zj_data['error_adj_ty'].sum()
        
        
        dict_error_new_ty.append(total_error_new_ty)
        dict_error_adj_ty.append(total_error_adj_ty)
        dict_maxdrawdown_adj.append(maxdrawdown_adj)
        print(GZ_data1.index[j].date())
    ee_data['error_new_ty'] = dict_error_new_ty
    ee_data['error_adj_9m_ty'] = dict_error_adj_ty
    ee_data['maxdrawdown_adj_9m'] = dict_maxdrawdown_adj
    
    #递推验证
    #定义参数
    #插点法，3,6,9的点
    
    dict_error_new_ty = []
    dict_error_adj_ty = []
    dict_maxdrawdown_adj = []
    for j in range(back_test_span):
        GZ_data1 = GZ_data1_origin.copy()
            
        rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
        # gz_1y = 0.0235
        # gz_9m = 0.021
        # gz_1d = 0.02
        gz_1y = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_1Y']/100
        gz_3m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_3m']/100    
        gz_6m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_6m']/100    
        gz_9m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_9m']/100
        gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
        
        
        diff_gz_1y =rf_1y - gz_1y
        diff_gz_3m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_3m'])/100   
        diff_gz_6m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_6m'])/100    
        diff_gz_9m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_9m'])/100
        diff_gz_1d = diff_gz_1y
        
        rf_3m = diff_gz_3m +gz_3m    
        rf_6m = diff_gz_6m +gz_6m    
        rf_9m = diff_gz_9m +gz_9m
        rf_1d = gz_1d + diff_gz_1d
        
        # date_now1 = '2021/9/7'
        # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
        date_now = GZ_data1.index[j]
        date_end = date_now+datetime.timedelta(days=365)
        
        date_mid_3m = date_now + datetime.timedelta(days=int(365/4))    
        date_mid_6m = date_now + datetime.timedelta(days=int(365/2))    
        date_mid_9m = date_now + datetime.timedelta(days=int(365*3/4))
        # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
        
        zj_data = pd.date_range(date_now,periods=366,freq ='D')
        zj_data = pd.DataFrame(zj_data,columns = {'date'})
        zj_data.set_index('date',inplace = True)
        
        df_1 = 1/(1+rf_1y)
        value_new = df_1*100*(1+rf_1y)
        value_ty_1 = 100
        error = 0
        
        zj_data.loc[date_now,'rf'] = rf_1y
        zj_data.loc[date_now,'DF'] = df_1
        zj_data.loc[date_now,'value_new'] = value_new
        zj_data.loc[date_now,'value_ty'] = value_ty_1
        zj_data.loc[date_now,'rf_adj'] = rf_1y
        zj_data.loc[date_now,'DF_adj'] = rf_1y
        zj_data.loc[date_now,'value_adj'] = rf_1y
        
        #加权mlf利率
        GZ_data1['gz_ytm_1d_new'] = GZ_data1['gz_ytm_1d']        
        GZ_data1['gz_ytm_3m_new'] = GZ_data1['gz_ytm_3m']
        GZ_data1['gz_ytm_6m_new'] = GZ_data1['gz_ytm_6m']
        GZ_data1['gz_ytm_9m_new'] = GZ_data1['gz_ytm_9m']
        GZ_data1['gz_ytm_1Y_new'] = GZ_data1['gz_ytm_1Y']

        gz_zj_diff_1d = GZ_data1.loc[date_now,'gz_ytm_1d'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_3m = GZ_data1.loc[date_now,'gz_ytm_3m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_6m = GZ_data1.loc[date_now,'gz_ytm_6m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']        
        gz_zj_diff_9m = GZ_data1.loc[date_now,'gz_ytm_9m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_1Y = GZ_data1.loc[date_now,'gz_ytm_1Y'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        

        GZ_data1['gz_ytm_1d'] = (1-weight_gy)*(GZ_data1.loc[date_now,'mlf_ytm_1Y'] + gz_zj_diff_1d) +weight_gy*GZ_data1['gz_ytm_1d_new']
        GZ_data1['gz_ytm_3m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_3m) +weight_gz*GZ_data1['gz_ytm_3m_new']        
        GZ_data1['gz_ytm_6m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_6m) +weight_gz*GZ_data1['gz_ytm_6m_new']
        GZ_data1['gz_ytm_9m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_9m) +weight_gz*GZ_data1['gz_ytm_9m_new']        
        GZ_data1['gz_ytm_1Y'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1Y) +weight_gz*GZ_data1['gz_ytm_1Y_new']
        
        for i in range(len(zj_data)):            
  
            # rf_1y = GZ_data1.loc[zj_data.index[i],'tb_ytm']/100 #投标的证金债
            # gz_1y = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_1Y']/100
            gz_3m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_3m']/100    
            gz_6m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_6m']/100    
            gz_9m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_9m']/100
            gz_1d = GZ_data1.loc[zj_data.index[i],'gz_ytm_1d']/100
            
            
            # diff_gz_1y =rf_1y - gz_1y
            diff_gz_3m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_3m'])/100   
            diff_gz_6m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_6m'])/100    
            diff_gz_9m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_9m'])/100
            diff_gz_1d = diff_gz_1y
            
            rf_3m = diff_gz_3m +gz_3m    
            rf_6m = diff_gz_6m +gz_6m    
            rf_9m = diff_gz_9m +gz_9m
            rf_1d = gz_1d + diff_gz_1d            
  
            
            
            date11 = zj_data.index[i]
            zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
            zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
            zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
            zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
            zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
            # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
            if date11 <= date_mid_3m:
                zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid_3m-date_now).days)*(rf_1y-rf_9m)
            
            elif (date11 > date_mid_3m)&(date11 <= date_mid_6m):
                zj_data.loc[date11,'rf_adj'] = rf_9m - ((date11 - date_mid_3m).days)/((date_mid_6m-date_mid_3m).days)*(rf_9m-rf_6m)
    
            elif (date11 > date_mid_6m)&(date11 <= date_mid_9m):
                zj_data.loc[date11,'rf_adj'] = rf_6m - ((date11 - date_mid_6m).days)/((date_mid_9m-date_mid_6m).days)*(rf_6m-rf_3m)  
            else:
                zj_data.loc[date11,'rf_adj'] = rf_3m - ((date11 - date_mid_9m).days)/((date_end-date_mid_9m).days)*(rf_3m-rf_1d)              
                
            zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
            zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
            zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
        
        zj_data['diff_new'] = zj_data['value_new'].diff()
        zj_data['diff_ty'] = zj_data['value_ty'].diff()
        zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
        
         #计算最大回撤
        for k in range(len(zj_data)-1):       
            zj_data.loc[zj_data.index[k+1],'value_adj_drawdown'] = zj_data.loc[zj_data.index[0:k],'value_adj'].max()-zj_data.loc[zj_data.index[k+1],'value_adj']
        
        
        maxdrawdown_adj = zj_data['value_adj_drawdown'].max()             
        total_error_new_ty = zj_data['error_new_ty'].sum()
        total_error_adj_ty = zj_data['error_adj_ty'].sum()
        
        
        dict_error_new_ty.append(total_error_new_ty)
        dict_error_adj_ty.append(total_error_adj_ty)
        dict_maxdrawdown_adj.append(maxdrawdown_adj)
        print(GZ_data1.index[j].date())
    ee_data['error_new_ty'] = dict_error_new_ty
    ee_data['error_adj_3_6_9_ty'] = dict_error_adj_ty
    ee_data['maxdrawdown_adj_3_6_9'] = dict_maxdrawdown_adj
    
    #递推验证
    #定义参数
    #插点法，六个月与九个月的点
    
    dict_error_new_ty = []
    dict_error_adj_ty = []
    dict_maxdrawdown_adj = []
    for j in range(back_test_span):
        GZ_data1 = GZ_data1_origin.copy()
    
        rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
        # gz_1y = 0.0235
        # gz_9m = 0.021
        # gz_1d = 0.02
        gz_1y = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_1Y']/100
        gz_3m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_3m']/100    
        gz_6m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_6m']/100    
        gz_9m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_9m']/100
        gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
        
        
        diff_gz_1y =rf_1y - gz_1y
        diff_gz_3m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_3m'])/100   
        diff_gz_6m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_6m'])/100    
        diff_gz_9m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_9m'])/100
        diff_gz_1d = diff_gz_1y
        
        rf_3m = diff_gz_3m +gz_3m    
        rf_6m = diff_gz_6m +gz_6m    
        rf_9m = diff_gz_9m +gz_9m
        rf_1d = gz_1d + diff_gz_1d
        
        # date_now1 = '2021/9/7'
        # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
        date_now = GZ_data1.index[j]
        date_end = date_now+datetime.timedelta(days=365)
        
        date_mid_3m = date_now + datetime.timedelta(days=int(365/4))    
        date_mid_6m = date_now + datetime.timedelta(days=int(365/2))    
        date_mid_9m = date_now + datetime.timedelta(days=int(365*3/4))
        # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
        
        zj_data = pd.date_range(date_now,periods=366,freq ='D')
        zj_data = pd.DataFrame(zj_data,columns = {'date'})
        zj_data.set_index('date',inplace = True)
        
        df_1 = 1/(1+rf_1y)
        value_new = df_1*100*(1+rf_1y)
        value_ty_1 = 100
        error = 0
        
        zj_data.loc[date_now,'rf'] = rf_1y
        zj_data.loc[date_now,'DF'] = df_1
        zj_data.loc[date_now,'value_new'] = value_new
        zj_data.loc[date_now,'value_ty'] = value_ty_1
        zj_data.loc[date_now,'rf_adj'] = rf_1y
        zj_data.loc[date_now,'DF_adj'] = rf_1y
        zj_data.loc[date_now,'value_adj'] = rf_1y
        
        
        #加权mlf利率
        GZ_data1['gz_ytm_1d_new'] = GZ_data1['gz_ytm_1d']        
        GZ_data1['gz_ytm_3m_new'] = GZ_data1['gz_ytm_3m']
        GZ_data1['gz_ytm_6m_new'] = GZ_data1['gz_ytm_6m']
        GZ_data1['gz_ytm_9m_new'] = GZ_data1['gz_ytm_9m']
        GZ_data1['gz_ytm_1Y_new'] = GZ_data1['gz_ytm_1Y']

        gz_zj_diff_1d = GZ_data1.loc[date_now,'gz_ytm_1d'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_3m = GZ_data1.loc[date_now,'gz_ytm_3m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_6m = GZ_data1.loc[date_now,'gz_ytm_6m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']        
        gz_zj_diff_9m = GZ_data1.loc[date_now,'gz_ytm_9m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_1Y = GZ_data1.loc[date_now,'gz_ytm_1Y'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        

        GZ_data1['gz_ytm_1d'] = (1-weight_gy)*(GZ_data1.loc[date_now,'mlf_ytm_1Y'] + gz_zj_diff_1d) +weight_gy*GZ_data1['gz_ytm_1d_new']
        GZ_data1['gz_ytm_3m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_3m) +weight_gz*GZ_data1['gz_ytm_3m_new']        
        GZ_data1['gz_ytm_6m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_6m) +weight_gz*GZ_data1['gz_ytm_6m_new']
        GZ_data1['gz_ytm_9m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_9m) +weight_gz*GZ_data1['gz_ytm_9m_new']        
        GZ_data1['gz_ytm_1Y'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1Y) +weight_gz*GZ_data1['gz_ytm_1Y_new']
        
        for i in range(len(zj_data)):
            
            # rf_1y = GZ_data1.loc[zj_data.index[i],'tb_ytm']/100 #投标的证金债
            # gz_1y = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_1Y']/100
            gz_3m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_3m']/100    
            gz_6m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_6m']/100    
            gz_9m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_9m']/100
            gz_1d = GZ_data1.loc[zj_data.index[i],'gz_ytm_1d']/100
            
            
            # diff_gz_1y =rf_1y - gz_1y
            diff_gz_3m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_3m'])/100   
            diff_gz_6m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_6m'])/100    
            diff_gz_9m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_9m'])/100
            diff_gz_1d = diff_gz_1y
            
            rf_3m = diff_gz_3m +gz_3m    
            rf_6m = diff_gz_6m +gz_6m    
            rf_9m = diff_gz_9m +gz_9m
            rf_1d = gz_1d + diff_gz_1d            
            
            date11 = zj_data.index[i]
            zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
            zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
            zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
            zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
            zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
            # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
            if date11 <= date_mid_3m:
                zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid_3m-date_now).days)*(rf_1y-rf_9m)
    
            elif (date11 > date_mid_3m)&(date11 <= date_mid_6m):
                zj_data.loc[date11,'rf_adj'] = rf_9m - ((date11 - date_mid_3m).days)/((date_mid_6m-date_mid_3m).days)*(rf_9m-rf_6m)  
            else:
                zj_data.loc[date11,'rf_adj'] = rf_6m - ((date11 - date_mid_6m).days)/((date_end-date_mid_6m).days)*(rf_6m-rf_1d)              
                
            zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
            zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
            zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
        
        zj_data['diff_new'] = zj_data['value_new'].diff()
        zj_data['diff_ty'] = zj_data['value_ty'].diff()
        zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
        
        #计算最大回撤
        for k in range(len(zj_data)-1):       
            zj_data.loc[zj_data.index[k+1],'value_adj_drawdown'] = zj_data.loc[zj_data.index[0:k],'value_adj'].max()-zj_data.loc[zj_data.index[k+1],'value_adj']
        
        
        maxdrawdown_adj = zj_data['value_adj_drawdown'].max()             
        total_error_new_ty = zj_data['error_new_ty'].sum()
        total_error_adj_ty = zj_data['error_adj_ty'].sum()
        
        
        dict_error_new_ty.append(total_error_new_ty)
        dict_error_adj_ty.append(total_error_adj_ty)
        dict_maxdrawdown_adj.append(maxdrawdown_adj)
        print(GZ_data1.index[j].date())
    ee_data['error_new_ty'] = dict_error_new_ty
    ee_data['error_adj_6_9_ty'] = dict_error_adj_ty
    ee_data['maxdrawdown_adj_6_9'] = dict_maxdrawdown_adj
    

    #递推验证
    #定义参数
    #插点法，3,6的点
    
    dict_error_new_ty = []
    dict_error_adj_ty = []
    dict_maxdrawdown_adj = []
    for j in range(back_test_span):
        GZ_data1 = GZ_data1_origin.copy()
    
        rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
        # gz_1y = 0.0235
        # gz_9m = 0.021
        # gz_1d = 0.02
        gz_1y = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_1Y']/100
        gz_3m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_3m']/100    
        gz_6m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_6m']/100    
        gz_9m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_9m']/100
        gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
        
        
        diff_gz_1y =rf_1y - gz_1y
        diff_gz_3m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_3m'])/100   
        diff_gz_6m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_6m'])/100    
        diff_gz_9m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_9m'])/100
        diff_gz_1d = diff_gz_1y
        
        rf_3m = diff_gz_3m +gz_3m    
        rf_6m = diff_gz_6m +gz_6m    
        rf_9m = diff_gz_9m +gz_9m
        rf_1d = gz_1d + diff_gz_1d
        
        # date_now1 = '2021/9/7'
        # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
        date_now = GZ_data1.index[j]
        date_end = date_now+datetime.timedelta(days=365)
        
        date_mid_3m = date_now + datetime.timedelta(days=int(365/4))    
        date_mid_6m = date_now + datetime.timedelta(days=int(365/2))    
        date_mid_9m = date_now + datetime.timedelta(days=int(365*3/4))
        # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
        
        zj_data = pd.date_range(date_now,periods=366,freq ='D')
        zj_data = pd.DataFrame(zj_data,columns = {'date'})
        zj_data.set_index('date',inplace = True)
        
        df_1 = 1/(1+rf_1y)
        value_new = df_1*100*(1+rf_1y)
        value_ty_1 = 100
        error = 0
        
        zj_data.loc[date_now,'rf'] = rf_1y
        zj_data.loc[date_now,'DF'] = df_1
        zj_data.loc[date_now,'value_new'] = value_new
        zj_data.loc[date_now,'value_ty'] = value_ty_1
        zj_data.loc[date_now,'rf_adj'] = rf_1y
        zj_data.loc[date_now,'DF_adj'] = rf_1y
        zj_data.loc[date_now,'value_adj'] = rf_1y
        
        #加权mlf利率
        GZ_data1['gz_ytm_1d_new'] = GZ_data1['gz_ytm_1d']        
        GZ_data1['gz_ytm_3m_new'] = GZ_data1['gz_ytm_3m']
        GZ_data1['gz_ytm_6m_new'] = GZ_data1['gz_ytm_6m']
        GZ_data1['gz_ytm_9m_new'] = GZ_data1['gz_ytm_9m']
        GZ_data1['gz_ytm_1Y_new'] = GZ_data1['gz_ytm_1Y']

        gz_zj_diff_1d = GZ_data1.loc[date_now,'gz_ytm_1d'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_3m = GZ_data1.loc[date_now,'gz_ytm_3m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_6m = GZ_data1.loc[date_now,'gz_ytm_6m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']        
        gz_zj_diff_9m = GZ_data1.loc[date_now,'gz_ytm_9m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_1Y = GZ_data1.loc[date_now,'gz_ytm_1Y'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        

        GZ_data1['gz_ytm_1d'] = (1-weight_gy)*(GZ_data1.loc[date_now,'mlf_ytm_1Y'] + gz_zj_diff_1d) +weight_gy*GZ_data1['gz_ytm_1d_new']
        GZ_data1['gz_ytm_3m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_3m) +weight_gz*GZ_data1['gz_ytm_3m_new']        
        GZ_data1['gz_ytm_6m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_6m) +weight_gz*GZ_data1['gz_ytm_6m_new']
        GZ_data1['gz_ytm_9m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_9m) +weight_gz*GZ_data1['gz_ytm_9m_new']        
        GZ_data1['gz_ytm_1Y'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1Y) +weight_gz*GZ_data1['gz_ytm_1Y_new']
        
        for i in range(len(zj_data)):
            
            # rf_1y = GZ_data1.loc[zj_data.index[i],'tb_ytm']/100 #投标的证金债
            # gz_1y = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_1Y']/100
            gz_3m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_3m']/100    
            gz_6m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_6m']/100    
            gz_9m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_9m']/100
            gz_1d = GZ_data1.loc[zj_data.index[i],'gz_ytm_1d']/100
            
            
            # diff_gz_1y =rf_1y - gz_1y
            diff_gz_3m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_3m'])/100   
            diff_gz_6m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_6m'])/100    
            diff_gz_9m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_9m'])/100
            diff_gz_1d = diff_gz_1y
            
            rf_3m = diff_gz_3m +gz_3m    
            rf_6m = diff_gz_6m +gz_6m    
            rf_9m = diff_gz_9m +gz_9m
            rf_1d = gz_1d + diff_gz_1d              
            
            date11 = zj_data.index[i]
            zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
            zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
            zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
            zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
            zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
            # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
            if date11 <= date_mid_6m:
                zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid_6m-date_now).days)*(rf_1y-rf_6m)           
    
            elif (date11 > date_mid_6m)&(date11 <= date_mid_9m):
                zj_data.loc[date11,'rf_adj'] = rf_6m - ((date11 - date_mid_6m).days)/((date_mid_9m-date_mid_6m).days)*(rf_6m-rf_3m)  
            else:
                zj_data.loc[date11,'rf_adj'] = rf_3m - ((date11 - date_mid_9m).days)/((date_end-date_mid_9m).days)*(rf_3m-rf_1d)              
                
            zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
            zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
            zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
        
        zj_data['diff_new'] = zj_data['value_new'].diff()
        zj_data['diff_ty'] = zj_data['value_ty'].diff()
        zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
        #计算最大回撤
        for k in range(len(zj_data)-1):       
            zj_data.loc[zj_data.index[k+1],'value_adj_drawdown'] = zj_data.loc[zj_data.index[0:k],'value_adj'].max()-zj_data.loc[zj_data.index[k+1],'value_adj']
        
        
        maxdrawdown_adj = zj_data['value_adj_drawdown'].max()             
        total_error_new_ty = zj_data['error_new_ty'].sum()
        total_error_adj_ty = zj_data['error_adj_ty'].sum()
        
        
        dict_error_new_ty.append(total_error_new_ty)
        dict_error_adj_ty.append(total_error_adj_ty)
        dict_maxdrawdown_adj.append(maxdrawdown_adj)
        print(GZ_data1.index[j].date())
    ee_data['error_new_ty'] = dict_error_new_ty
    ee_data['error_adj_3_6_ty'] = dict_error_adj_ty
    ee_data['maxdrawdown_adj_3_6'] = dict_maxdrawdown_adj


    #递推验证
    #定义参数
    #插点法，3,9的点
    
    dict_error_new_ty = []
    dict_error_adj_ty = []
    dict_maxdrawdown_adj = []
    for j in range(back_test_span):
        GZ_data1 = GZ_data1_origin.copy()
    
        rf_1y = GZ_data1.loc[GZ_data1.index[j],'tb_ytm']/100 #投标的证金债
        # gz_1y = 0.0235
        # gz_9m = 0.021
        # gz_1d = 0.02
        gz_1y = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_1Y']/100
        gz_3m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_3m']/100    
        gz_6m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_6m']/100    
        gz_9m = GZ_data1.loc[GZ_data1.index[j],bond_name+'_ytm_9m']/100
        gz_1d = GZ_data1.loc[GZ_data1.index[j],'gz_ytm_1d']/100
        
        
        diff_gz_1y =rf_1y - gz_1y
        diff_gz_3m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_3m'])/100   
        diff_gz_6m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_6m'])/100    
        diff_gz_9m = diff_gz_1y+(origin_data.loc[GZ_data1.index[j],bond_name+'_add_9m'])/100
        diff_gz_1d = diff_gz_1y
        
        rf_3m = diff_gz_3m +gz_3m    
        rf_6m = diff_gz_6m +gz_6m    
        rf_9m = diff_gz_9m +gz_9m
        rf_1d = gz_1d + diff_gz_1d
        
        # date_now1 = '2021/9/7'
        # date_now = datetime.datetime.strptime(date_now1, "%Y/%m/%d")
        date_now = GZ_data1.index[j]
        date_end = date_now+datetime.timedelta(days=365)
        
        date_mid_3m = date_now + datetime.timedelta(days=int(365/4))    
        date_mid_6m = date_now + datetime.timedelta(days=int(365/2))    
        date_mid_9m = date_now + datetime.timedelta(days=int(365*3/4))
        # date_mid = datetime.datetime.strptime('2022/3/16', "%Y/%m/%d")
        
        zj_data = pd.date_range(date_now,periods=366,freq ='D')
        zj_data = pd.DataFrame(zj_data,columns = {'date'})
        zj_data.set_index('date',inplace = True)
        
        df_1 = 1/(1+rf_1y)
        value_new = df_1*100*(1+rf_1y)
        value_ty_1 = 100
        error = 0
        
        zj_data.loc[date_now,'rf'] = rf_1y
        zj_data.loc[date_now,'DF'] = df_1
        zj_data.loc[date_now,'value_new'] = value_new
        zj_data.loc[date_now,'value_ty'] = value_ty_1
        zj_data.loc[date_now,'rf_adj'] = rf_1y
        zj_data.loc[date_now,'DF_adj'] = rf_1y
        zj_data.loc[date_now,'value_adj'] = rf_1y
        
        
        #加权mlf利率
        GZ_data1['gz_ytm_1d_new'] = GZ_data1['gz_ytm_1d']        
        GZ_data1['gz_ytm_3m_new'] = GZ_data1['gz_ytm_3m']
        GZ_data1['gz_ytm_6m_new'] = GZ_data1['gz_ytm_6m']
        GZ_data1['gz_ytm_9m_new'] = GZ_data1['gz_ytm_9m']
        GZ_data1['gz_ytm_1Y_new'] = GZ_data1['gz_ytm_1Y']

        gz_zj_diff_1d = GZ_data1.loc[date_now,'gz_ytm_1d'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_3m = GZ_data1.loc[date_now,'gz_ytm_3m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_6m = GZ_data1.loc[date_now,'gz_ytm_6m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']        
        gz_zj_diff_9m = GZ_data1.loc[date_now,'gz_ytm_9m'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        gz_zj_diff_1Y = GZ_data1.loc[date_now,'gz_ytm_1Y'] - GZ_data1.loc[date_now,'mlf_ytm_1Y']
        

        GZ_data1['gz_ytm_1d'] = (1-weight_gy)*(GZ_data1.loc[date_now,'mlf_ytm_1Y'] + gz_zj_diff_1d) +weight_gy*GZ_data1['gz_ytm_1d_new']
        GZ_data1['gz_ytm_3m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_3m) +weight_gz*GZ_data1['gz_ytm_3m_new']        
        GZ_data1['gz_ytm_6m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_6m) +weight_gz*GZ_data1['gz_ytm_6m_new']
        GZ_data1['gz_ytm_9m'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_9m) +weight_gz*GZ_data1['gz_ytm_9m_new']        
        GZ_data1['gz_ytm_1Y'] = (1-weight_gz)*(((1-weight_mlf)*GZ_data1.loc[date_now,'mlf_ytm_1Y']+weight_mlf*GZ_data1['mlf_ytm_1Y']) + gz_zj_diff_1Y) +weight_gz*GZ_data1['gz_ytm_1Y_new']
        
        for i in range(len(zj_data)):
            
            # rf_1y = GZ_data1.loc[zj_data.index[i],'tb_ytm']/100 #投标的证金债
            # gz_1y = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_1Y']/100
            gz_3m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_3m']/100    
            gz_6m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_6m']/100    
            gz_9m = GZ_data1.loc[zj_data.index[i],bond_name+'_ytm_9m']/100
            gz_1d = GZ_data1.loc[zj_data.index[i],'gz_ytm_1d']/100
            
            
            # diff_gz_1y =rf_1y - gz_1y
            diff_gz_3m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_3m'])/100   
            diff_gz_6m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_6m'])/100    
            diff_gz_9m = diff_gz_1y+(origin_data.loc[date_now,bond_name+'_add_9m'])/100
            diff_gz_1d = diff_gz_1y
            
            rf_3m = diff_gz_3m +gz_3m    
            rf_6m = diff_gz_6m +gz_6m    
            rf_9m = diff_gz_9m +gz_9m
            rf_1d = gz_1d + diff_gz_1d              
            
            
            date11 = zj_data.index[i]
            zj_data.loc[date11,'rf'] = rf_1y - (date11-date_now).days/365*(rf_1y - rf_1d)
            zj_data.loc[date11,'DF'] = 1/(1+zj_data.loc[date11,'rf'])**(((date_end-date11).days)/365)
            zj_data.loc[date11,'value_new'] = zj_data.loc[date11,'DF']*100*(1+rf_1y)
            zj_data.loc[date11,'value_ty'] = 100+rf_1y*(date11 - date_now).days/365*100
            zj_data.loc[date11,'error_new_ty'] = (zj_data.loc[date11,'value_ty']-zj_data.loc[date11,'value_new'])**2
            # zj_data.loc[date11,'diff_new'] = zj_data.loc[date11,'value_new'] - zj_data.loc[date11-datetime.timedelta(days=1),'value_new']
            if date11 <= date_mid_3m:
                zj_data.loc[date11,'rf_adj'] = rf_1y - ((date11 - date_now).days)/((date_mid_3m-date_now).days)*(rf_1y-rf_9m)
            
            elif (date11 > date_mid_3m)&(date11 <= date_mid_9m):
                zj_data.loc[date11,'rf_adj'] = rf_9m - ((date11 - date_mid_3m).days)/((date_mid_9m-date_mid_3m).days)*(rf_9m-rf_3m)
    
            else:
                zj_data.loc[date11,'rf_adj'] = rf_3m - ((date11 - date_mid_9m).days)/((date_end-date_mid_9m).days)*(rf_3m-rf_1d)              
                
            zj_data.loc[date11,'DF_adj'] = 1/(1+zj_data.loc[date11,'rf_adj'])**((date_end-date11).days/365)
            zj_data.loc[date11,'value_adj'] = 100*(1+rf_1y)*zj_data.loc[date11,'DF_adj']
            zj_data.loc[date11,'error_adj_ty'] = (zj_data.loc[date11,'value_adj']-zj_data.loc[date11,'value_ty'])**2
        
        zj_data['diff_new'] = zj_data['value_new'].diff()
        zj_data['diff_ty'] = zj_data['value_ty'].diff()
        zj_data['diff_diff_new_ty'] = zj_data['diff_new']-zj_data['diff_ty']
        
        #计算最大回撤
        for k in range(len(zj_data)-1):       
            zj_data.loc[zj_data.index[k+1],'value_adj_drawdown'] = zj_data.loc[zj_data.index[0:k],'value_adj'].max()-zj_data.loc[zj_data.index[k+1],'value_adj']
        
        
        maxdrawdown_adj = zj_data['value_adj_drawdown'].max()             
        total_error_new_ty = zj_data['error_new_ty'].sum()
        total_error_adj_ty = zj_data['error_adj_ty'].sum()
        
        
        dict_error_new_ty.append(total_error_new_ty)
        dict_error_adj_ty.append(total_error_adj_ty)
        dict_maxdrawdown_adj.append(maxdrawdown_adj)
        print(GZ_data1.index[j].date())
    ee_data['error_new_ty'] = dict_error_new_ty
    ee_data['error_adj_3_9_ty'] = dict_error_adj_ty
    ee_data['maxdrawdown_adj_3_9'] = dict_maxdrawdown_adj
    bond_list.append(ee_data)

# ee_data = ee_data.merge(GZ_data1_origin['gz_ytm_1Y'],left_index=True,right_index=True,how = 'left')
ee_data['gz_ytm_1Y'] = GZ_data1_origin['gz_ytm_1Y']
# ee_data = ee_data.loc['2020-07-02':,:]
#画图
ax = ee_data[['error_new_ty','error_adj_3m_ty','error_adj_6m_ty','error_adj_9m_ty','error_adj_3_6_9_ty','gz_ytm_1Y']].plot(secondary_y ='gz_ytm_1Y')
ax.legend(loc=1)
ax.right_ax.legend(loc=2)

ax2 = ee_data[['error_new_ty','error_adj_6m_ty','error_adj_9m_ty','error_adj_6_9_ty','gz_ytm_1Y']].plot(secondary_y ='gz_ytm_1Y')
ax2.legend(loc=1)
ax2.right_ax.legend(loc=2)

writer = pd.ExcelWriter(r'C:\Users\tangh\Desktop\量化\ZJZ_model4.xlsx')
ee_data[['error_new_ty','error_adj_3m_ty','error_adj_6m_ty','error_adj_9m_ty','error_adj_3_6_9_ty','error_adj_6_9_ty','gz_ytm_1Y']].to_excel(writer,sheet_name= 'latest_signal')
writer.save()
writer.close() 


#画图
bond_list = []
bond_list.append(ee_data)

#画出不同债基的图
# bond_dict = ['gk','nf','jck','ncd','gz']

# bond_name_dict = dict(zip(bond_dict,['国开债','农发债','进出口债','NCD存单','国债']))
bond_dict = ['gz']
bond_name_dict = dict(zip(bond_dict,['国债']))
bond_data_dict = dict(zip(bond_dict,bond_list))
error_sum = pd.DataFrame()


writer = pd.ExcelWriter(r'C:\Users\tangh\Desktop\量化\证金债估值测试\ZJZ_model_滚动加点——新修改5555.xlsx')
for key,value in bond_data_dict.items():
    ax = value[['error_new_ty','error_adj_3m_ty','error_adj_6m_ty','error_adj_9m_ty',key+'_ytm_1Y']].plot(secondary_y =key+'_ytm_1Y',title = '以'+bond_name_dict[key]+'为基础的误差回测曲线')
    ax.legend(loc=1)
    ax.right_ax.legend(loc=2)
    
    ax2 = value[['error_new_ty','error_adj_3_6_ty','error_adj_6_9_ty',key+'_ytm_1Y','error_adj_3_9_ty','error_adj_3_6_9_ty']].plot(secondary_y =key+'_ytm_1Y',title = '以'+bond_name_dict[key]+'为基础的误差回测曲线')
    ax2.legend(loc=1)
    ax2.right_ax.legend(loc=2)

    
    sum_value = value[['error_new_ty','error_adj_3m_ty','error_adj_6m_ty','error_adj_9m_ty','error_adj_3_6_ty','error_adj_6_9_ty','error_adj_3_9_ty','error_adj_3_6_9_ty']].sum()
    sum_value.name = key
    sum_value = pd.DataFrame(sum_value)
    error_sum = error_sum.join(sum_value,how = 'outer')
    # error_sum = pd.DataFrame(sum_value)
    
    # writer = pd.ExcelWriter(r'C:\Users\tangh\Desktop\量化\证金债估值测试\ZJZ_model4_{}.xlsx'.format(key))
    value[['error_new_ty','error_adj_3m_ty','error_adj_6m_ty','error_adj_9m_ty','error_adj_3_6_ty','error_adj_6_9_ty','error_adj_3_9_ty','error_adj_3_6_9_ty',key+'_ytm_1Y']].to_excel(writer,sheet_name= key)

writer.save()
writer.close()

zj_data['value_adj'].plot()
plt.title('动态跟踪条件下证金债估值曲线')


#拟合证金债曲线
origin_data2 = origin_data.loc['2020-09-01':'2021-09-01',:]
origin_data2.loc['2020-09-01':'2020-12-01','zjz_gz'] = origin_data2.loc['2020-09-01':'2020-12-01','gz_add_1Y']/100+ origin_data2.loc['2020-09-01':'2020-12-01','gz_ytm_9m']/100+origin_data2.loc['2020-09-01':'2020-12-01','gz_add_9m']/100
origin_data2.loc['2020-12-01':'2021-06-01','zjz_gz'] = origin_data2.loc['2020-12-01':'2021-06-01','gz_add_1Y']/100+ origin_data2.loc['2020-12-01':'2021-06-01','gz_ytm_6m']/100+origin_data2.loc['2020-12-01':'2021-06-01','gz_add_6m']/100
origin_data2.loc['2021-06-01':'2021-09-01','zjz_gz'] = origin_data2.loc['2021-06-01':'2021-09-01','gz_add_1Y']/100+ origin_data2.loc['2021-06-01':'2021-09-01','gz_ytm_3m']/100+origin_data2.loc['2021-06-01':'2021-09-01','gz_add_3m']/100

# origin_data2.loc['2021-06-01':'2021-09-01','zjz_gz'] = origin_data2['gz_add_1Y']/100+ origin_data2['gz_ytm_3m']/100+origin_data2['gz_add_3m']/100


# origin_data2['zjz_gz'] = origin_data2['zjz_gz'].apply(lambda x:format(x,'.2%'))#百分比显示
origin_data2['zjz_gz'].plot()
plt.title('动态跟踪条件下证金债利率拟合曲线')

ee_data.max()
