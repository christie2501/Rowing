#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

import networkx as nx
from pyvis.network import Network
import itertools

from IPython.display import display, HTML


# In[2]:


#import novice sheet as csv

#remember need to change settings so that anyone with the link can view the sheet
sheet_id = "1YCXmJnYtMeJQZFot6O1AFCMf2QE5GgoyPcpJ3M8Qxaw" #google sheets id
sheet_name = "Novice_Availabilities"
url1 = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}" #create f string of url
df = pd.read_csv(url1)
novice_df = df #make df for later
df


# In[3]:


df = df.get(df["Rowing/coxing"]=="Rowing")#get only those who want to row
df = df.drop(['crsID',"# sessions?","Rowing/coxing"], axis=1).set_index('Name') #removes unwanted columns (experience, comments), sets index as name
df = df[df.index.notnull()] #drops rows where no data entered

#df = df.get(df["Mens/Womens side?"]=="Womens")
df


# In[4]:


#import coach sheet as csv

sheet_id = "1YCXmJnYtMeJQZFot6O1AFCMf2QE5GgoyPcpJ3M8Qxaw" #google sheets id
sheet_name = "Coach_Availabilities"
url2 = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}" #create f string of url
coach_df = pd.read_csv(url2)

#repeat processing steps, same as for novice_df
coach_df = coach_df.set_index("Name") #set the index as the name column
coach_df = coach_df[coach_df.index.notnull()] #drop rows where no-one has entered data
coach_df = coach_df.drop(columns = ["# sessions?","crsID"])

coach_df


# In[5]:


available_coach_times = []

for time in coach_df.columns:
    y = coach_df.get(coach_df[time]==True)  #gets coaches who are available and makes df
    if y.empty == False : #if df is empty, then there are no coaches. we don't want that time then. if there are coaches, tell us time
        available_coach_times.append(time) #append time to list
#print(available_coach_times)


# In[6]:


df = df[available_coach_times] #only work with novices when coaches are available


# In[7]:


slots = []

for time in df.columns:
    X = df[df[time] == True].index  #if rower is available at that time
    Y = list(itertools.combinations(X,2))  #pairwise combinations of names
    Z = [y + ([time],) for y in Y] #add rowers and time to list
    slots += Z
    
slots_df = pd.DataFrame(slots, columns=['Rower 1','Rower 2','Time']) #make list into dataframe
#slots_df


# In[8]:


G = nx.from_pandas_edgelist(slots_df, 'Rower 1', 'Rower 2') #create network
net = Network(notebook=True)
net.from_nx(G)
net.show("possible slots.html") #visualise unmatched network


# In[9]:


matchings = nx.algorithms.matching.maximal_matching(G) #maximal matching
matchings_df = pd.DataFrame(matchings, columns=['Rower 1','Rower 2']) #make into dataframe


# In[10]:


G = nx.from_pandas_edgelist(matchings_df, 'Rower 1', 'Rower 2')
net = Network(notebook=True)
net.from_nx(G)
net.show("solution.html") #visualise matched network


# In[11]:


match_times = []

for match in matchings: #iterate over dict of matches
    times = []
    df3 = df.loc[match,:]
    for time in df.columns:
        if df3[time].all():
            times.append(time)
    match_times.append(times)
    
matchings_df['Time'] = match_times
#matchings_df


# In[12]:


#create list of rowers who are free when coaches available
df2 = df.apply(pd.Series.value_counts, axis=1).fillna(0)
df2.columns = ["False","True"]

for i, row in df2.iterrows():
    if df2.loc[i,"True"] == 0:
        df2.drop(i, inplace = True)
all_rowers = df2.index.to_list()
#all_rowers


# In[13]:


list_rower_matched = matchings_df["Rower 1"].to_list()
list_rower_matched += matchings_df["Rower 2"].to_list()

unmatched = [x for x in all_rowers if x not in list_rower_matched] #create list of unmatched rowers
#unmatched


# In[14]:


#give a match to unmatched people

for rower in unmatched:
    findfrancis = slots_df.get(slots_df["Rower 1"]==rower)
    if findfrancis.empty == False:
        ranfindfrancis = findfrancis.sample() #randomly pick pair from those available
        matchings_df = matchings_df.append(ranfindfrancis, ignore_index=True) #append pair and time to matchings_df
    
#matchings_df


# In[15]:


#find coaches for all

matchings_df["Coaches available"] = np.nan #empty column for coaches
for i, row in matchings_df.iterrows():
    coach_time = []
    for j in matchings_df.iloc[i,2]: #for each time
        tempcoach = coach_df.get(coach_df[j]==True) #find coaches available at time
        if tempcoach.empty == False:
            coach_time.append(tempcoach.index) #add coach to list if available
        matchings_df.loc[i,"Coaches available"] = [coach_time] #add list to dataframe

#matchings_df
display(HTML(matchings_df.to_html()))


# In[16]:


#process novice sheet
novice_df = novice_df.set_index("Name") #set the index as the name column
novice_df = novice_df[novice_df.index.notnull()] #drop rows where no-one has entered data

Rnovice_df = novice_df
#Rnovice_df = Rnovice_df.get(novice_df["Rowing/coxing"]=="Rowing")#get only rowers
Rnovice_df = Rnovice_df.drop(columns = ["crsID","Rowing/coxing"]) #get rid of the columns we don't need for simplicity
Rnovice_df

#table of available rowers
available_coach_times = []

for time in coach_df.columns:
    y = coach_df.get(coach_df[time]==True)  #gets coaches who are available and makes df
    if y.empty == False : #if df is empty, then there are no coaches. we don't want that time then. if there are coaches, tell us time
        available_coach_times.append(time) #append time to list
#print(available_coach_times)

Rnovice_df1 = novice_df[available_coach_times] #gets novice times when coaches available
#print(Rnovice_df1)

results1 = []
storage = []
index = ["Coaches","Rowers","Number of Rowers"]
overview = pd.DataFrame(index = index, columns = available_coach_times)
#overview

results1 = []
storage = []

for time in overview.columns:
    x1 = Rnovice_df1.get(Rnovice_df1[time]== True) #get rowers available at that time
    list1 = x1.index.tolist() #list of rowers available
    number = len(list1)
    tempcoach = coach_df.get(coach_df[time]==True)
    coach_time = []
    if tempcoach.empty == False:
        coach_time.append(tempcoach.index)
    overview.loc["Coaches",time] = coach_time
    overview.loc["Rowers",time] = list1
    overview.loc["Number of Rowers", time] = number
    if overview.loc["Number of Rowers", time] == 0:
        overview.drop(columns = [time], inplace = True) #drop times where there are no rowers



display(HTML(overview.to_html())) #displaying as html allows to see  all list

