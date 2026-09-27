# -*- coding: utf-8 -*-
"""Originally created in 2026 for Final Year Engineering Project @author: kkako"""
print(".........................................................................................")
print("Home Appliance Scheduling Tool (HAST) for Residential Demand Management"), print("Created by Karl Kakoschke, with commits from: N/A")
import time #for performance benchmarking
import pandas as pd #needed for csv import
import matplotlib.pyplot as plt #matplotlib for graphs
import numpy as np #numpy for graphs, calculations, etc
from pathlib import Path #this is needed for reading files project folder structure
#import glob #not needed in Spyder IDE
import os
import math #for always rounding up to whole number
'''##############################################################################################################import csv files start
This is reading tariff data, household demand data, household local generation data'''
##### Import Tariff Data:
folder_path = "tariff data" #Define the folder and file names
file_name = "tariff.csv" #Define the folder and file names
full_path = os.path.join(folder_path, file_name) #Combine them into a full file path
df = pd.read_csv(full_path) #Read the CSV file
rates = df["Cost"] #Extract the target column name into a Python list, rates and 'rates'
##### Import Household Data:
folder_path = "household data" #Define the folder and file names
file_name = "dataframe.csv" #Define the folder and file names
full_path = os.path.join(folder_path, file_name) #Combine them into a full file path
df = pd.read_csv(full_path) #Read the CSV file
df_time = df["Time Start"]  #used for plotting and for optimisation....
df_generation = df["Generation"] #generation data
df_demand = df["Demand"] #demand data
kwhr = 1000 #for w to kw conversion
blackzeroes = np.zeros((48,)) #creating an array of correct shape, filled with 0, this is a cheat/hack for all 0 values in graphs appear black
df_demandapp = 0 #this is for creating initial graph and cost!!!
#### Import Appliance Data:
folder_path = Path("appliance data") #set the path to the appliance data
for file in sorted(folder_path.glob("*.csv")):
    appliance_data = pd.read_csv(file)
    appliance_name = file.stem
    print("Loading the {} schedule for optimisation...".format(appliance_name))
    appliance_data_wh = appliance_data["Wh"]
    appliance_data_kwh = appliance_data_wh / kwhr
    appliance_data_time = appliance_data["Time Start"]
    df_demandapp = df_demandapp + appliance_data_kwh #Pass schedule to demand-appliance-profile
print(".........................................................................................")
df_demandapp = df_demandapp + df_demand #update df_demandapp to include appliance demand data and household demand
df_overall = df_demandapp - df_generation #KK for calculation
df_overall.loc[df_overall < 0] = 0 #All negative values become 0 (if in a timeslot, generation is greater than appliance demand)
#df_demandapp.to_csv('outputs/output_pandas_pre_sched.csv', index=False) # index=False prevents saving row numbers, this outputs to a .csv file in outputs folder --KK old check
excludedts = [] # Set up empty excluded time slot list #this could be included in simple linear solver section (but not in the function)
#This is needed to set time slots that can't be used for each calculation, this could be used via user input e.g. Do you want this scheduled in the AM or PM? then use half tslots as excludedts  
'''############################################################################################################## Is there solar/local generation check'''  
gensum = df_generation.sum()
if gensum > 0:
    generation_available = 1
    print("Total Generation Available = {:.2f}kWh".format(gensum))
'''############################################################################################################## If solar need to calculate total energy usage from grid''' 
demandsum = df_demand.sum()
print("Total Base Demand = {:.2f}kWh".format(demandsum))
demandappsum = df_demandapp.sum()
print("Total Base Demand and Appliance Power Budget = {:.2f}kWh".format(demandappsum))
energyusage = df_demandapp - df_generation
energyusage[energyusage<0] = 0
energyusage_total = energyusage.sum()
print("Energy imported from the grid per day = {:.2f}kWh".format(energyusage_total))
'''############################################################################################################## Cost Calculator'''
#Find Cost
def calculate_cost(df_demandapp, rates):
    grand_total = df_demandapp * rates
    grand_total = grand_total.sum()
    grand_total_permonth = grand_total * 30.42 #this is average number of days in a month for a non-leap year
    return grand_total, grand_total_permonth
#grand_total, grand_total_permonth = calculate_cost(df_demand, rates) # Find original cost: This is cost of base demand only
#print("The starting cost per day is ${:.2f} prior to adding appliances to be scheduled.".format(grand_total))
#print("This equates to approximately ${:.2f} per month.".format(grand_total_permonth))
grand_total, grand_total_permonth = calculate_cost(df_overall, rates) # Find new cost
print("The starting cost for base demand and appliances after generation to be scheduled per day is ${:.2f} prior to any scheduling optimisations.".format(grand_total))
print("This equates to approximately ${:.2f} per month.".format(grand_total_permonth))
pre_opt_gt = grand_total
pre_opt_gtm = grand_total_permonth
'''############################################################################################################## Graphing -- '''
#########################This is working plot with time slots on x axis
fig, ax = plt.subplots(figsize=(50, 15)) #50 is width, 15 is height of graph
plt.rcParams.update({'font.size': 18})  
plt.title('Household Demand Data Pre Optimisation')
plt.ylabel('kW')
plt.plot(df_time, df_generation, color='g', linestyle='-.',marker='') ##1 is x, 2 is y
plt.plot(df_time, df_demand, color='r', linestyle='--',marker='') ##1 is x, 2 is y
plt.plot(df_time, df_demandapp, '-k') ##1 is x, 2 is y
#Settings for secondary x axis:
sec = ax.secondary_xaxis(location=-0.025)
sec.set_xticks(df.iloc[:, 0])
sec.set_xticklabels(df.iloc[:, 2]) #not used: , rotation=45, ha="left")
sec.spines['bottom'].set_linewidth(0)
sec.set_xlabel('Time Slot Start/Finish Times') #this is label for secondary xaxis, can't use label on primary x axis
#plt.ylim(0,5) #min to max y values
plt.setp(plt.gca().get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the x axis to false
plt.setp(sec.get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the secondary x axis to false
plt.legend(['Generation','Demand', 'Demand w/Appliances']) #show the legend
plt.grid(True)
plt.show()
'''############################################################################################################## Cost Structure Graph:'''
'''This works but only need to enable for user to check if the cost structure is correct (say if we manually input cost structure)'''  
##This is using values in .csv files and graphing them,  THIS IS FOR GRAPHING Tariff Structure
folder_path = Path("tariff data") #set the path to the tariff data
fig, ax = plt.subplots(figsize=(50, 15)) #Setup the figure and axis before loading files, 50 is width, 15 is height of graph   
for file_path in sorted(folder_path.glob("*.csv")): #Loop through every detected filename
    file_name = os.path.basename(file_path) #Extract only the file name to use as a clean legend label
    df = pd.read_csv(file_path) #Read the data file
    ax.step(df.iloc[:, 1], df.iloc[:, 3], label="Tariff Data") #iloc[:, 1] targets column 2, and iloc[:, 3] targets column 4, --Step Plot
    #ax.plot(df.iloc[:, 1], df.iloc[:, 3], label=file_name) --line plot instead of step plot
ax.set_title("Electricity Price Structure From File") #Finalise and display the graph after the loop completes
ax.set_ylabel("$ per kwh") 
#ax.step(appliance_data_time, blackzeroes, '-k', label=None) #this makes all 0 values appear black, not needed for tariff as we set y value to 0
# label/set the secondary x axis settings:
sec = ax.secondary_xaxis(location=-0.025)
sec.set_xticks(df.iloc[:, 0])
sec.set_xticklabels(df.iloc[:, 2]) #unused: rotation=45, ha="left")
sec.spines['bottom'].set_linewidth(0)
sec.set_xlabel('Time Slot Start/Finish Times') #this is label for secondary xaxis, first xaxis label needs to be removed when using secondary xaxis
plt.ylim(0,math.ceil(max(df.iloc[:, 3]))) #min to max y values, max y value is the rounded up whole number of the highest value in the 'Cost' column of tariff data
ax.legend()  # Automatically displays labels for all files
ax.grid(True)
plt.setp(plt.gca().get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the x axis to false
plt.setp(sec.get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the secondary x axis to false
plt.show()
'''##############################################################################################################  Simple linear Solver Start:'''
df_resulting = np.where(df_generation > 0, np.where(df_generation - df_demand > 0, df_generation - df_demand, 0), 0) #calculates leftover generation
generation = df_resulting #'''THIS WORKS use this''' #this is for simple linear solver, with SOLAR
'''############################################################################################################## Optimise for cost if no local generation:'''
'''DEMAND & GENERATION ARE ROLLING VALUES AND NEED TO BE UPDATED -- CHECK KK'''
############################################Need to add earliest start, latest finish, etc
##This is based on cost only while keeping with constraints
def calculate_best_start(rates, profile, excludedts, earliest_start, latest_finish):
    best_cost = float('inf') #infinity value
    best_tslot = 0 #This will automatically put appliance at 'time slot 0' if all tslots are excluded - this is error handling and can signify the user an constraint is wrong
    exclude = excludedts
    print(f"Earliest Starting Time Slot: {earliest_start}")
    print(f"Latest Finishing Time Slot: {latest_finish}")
    latest_start = latest_finish - len(profile) - 1 #calculate latest starting timeslot
    print(f"Latest Starting Time Slot: {latest_start}")
    for tslot in range(earliest_start, latest_start + 1): #Test every possible start hour within constraints
        if tslot not in exclude:
                if any(tslot <= x <= (tslot + len(profile)) for x in exclude): #Check if any of the tslots that are potentially to be scheduled are taken
                    pass #empty if statement             
                else:
                    cost = np.sum(rates[tslot:tslot+len(profile)] * profile)
#            print(f"Time Slot: {tslot}, Total Cost: {cost}") #for debugging purposes only - see what it's calculating
#Check and save if best scheduling timeslot
                if cost < best_cost:
                    best_cost = cost
                    best_tslot = tslot
    return best_tslot, best_cost
###########################How to use:
#start_tslot, total_cost = calculate_best_start(rates, appliance_profile, excludedts)
'''############################################################################################################## Optimise to minimise grid usage if local generation available:'''
##This is based on using the least amount of energy from the utility
def calculate_bestgen_start(generation, profile, excludedts, earliest_start, latest_finish):
    best_gen = -999 #
    best_tslot = 0 #This will automatically put appliance at 'time slot 0' if all tslots are excluded - this is error handling and can signify the user an constraint is wrong
    exclude = excludedts
    print(f"Earliest Starting Time Slot: {earliest_start}")
    print(f"Latest Finishing Time Slot: {latest_finish}")
    latest_start = latest_finish - len(profile) - 1 #calculate latest starting timeslot
    print(f"Latest Starting Time Slot: {latest_start}")
    for tslot in range(earliest_start, latest_start + 1): #Test every possible start hour within constraints
            if tslot not in exclude:
                if any(tslot <= x <= (tslot + len(profile)) for x in exclude): #Check if any of the tslots that are potentially to be scheduled are taken
                    pass #empty if statement             
                else:
                    gen = np.sum(generation[tslot:tslot+len(profile)] - profile)
#                    print(f"Time Slot: {tslot}, Total Energy Used from the Grid: {gen}kW") #for debugging purposes only - see at which starting tslot the least amount of energy is used from the grid
#Check and save if best scheduling timeslot
                if gen > best_gen:
                    best_gen = gen
                    best_tslot = tslot
    return best_tslot, best_gen
###########################How to use:
#start_tslot, total_grid = calculate_bestgen_start(generation, appliance_profile, excludedts)
'''############################################################################################################## Exclude time slots if already used:'''
#need to pass/add best tslot and length of appliance schedule to taken timeslots -- done KK
def excluded_tslots(appliance_profile, start_tslot, excludedts):
    for x in range(len(appliance_profile)): #range to stop value, 14-4+1 = for x in 11 this is a dev note and can be deleted
        excludedts.extend(list([start_tslot + x]))
    print(f"Excluded time slots: {excludedts}")
    return excludedts
###########################How to use:
    #excludedts = excluded_tslots(appliance_profile, start_tslot, excludedts)
'''############################################################################################################## Appliance Schedule Graph Start Pre Optimisation'''
##This is using values in .csv files and graphing them. Define the directory and look for all CSV files:
folder_path = Path("appliance data") #set the path to the appliance data
fig, ax = plt.subplots(figsize=(50, 15)) # Setup the figure and axis once before loading files: 50 is width, 15 is height of graph   
# Loop through every detected filename:
for file_path in sorted(folder_path.glob("*.csv")):
    file_name = os.path.basename(file_path) # Extract only the file name to use as a clean legend label
    df = pd.read_csv(file_path) # Read the data file
    # Plot the data line or step:
    ax.step(df.iloc[:, 1], df.iloc[:, 3], label=file_name) # -- Step Plot, iloc[:, 1] targets column 2
    #ax.plot(df.iloc[:, 1], df.iloc[:, 3], label=file_name) --Line plot
#Finalise and display the graph after the for loop completes:
ax.set_title("Appliance Schedule Pre Optimisation (from data files)")
ax.set_ylabel("Watts") #might change this to kW later KK
ax.step(appliance_data_time, blackzeroes, '-k', label=None) #this makes all 0 values appear black
sec = ax.secondary_xaxis(location=-0.025)
sec.set_xticks(df.iloc[:, 0])
sec.set_xticklabels(df.iloc[:, 2]) #, rotation=45, ha="left")
sec.spines['bottom'].set_linewidth(0)
sec.set_xlabel('Time Slot Start/Finish Times') #this is label for secondary xaxis, first xaxis label needs to be removed when using secondary xaxis
#plt.ylim(0,5) #min to max y values
ax.legend()  # Automatically displays labels for all files
ax.grid(True)
plt.setp(plt.gca().get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the x axis to false
plt.setp(sec.get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the secondary x axis to false
plt.show()
'''##############################################################################################################'''
'''Optimise all appliances - this is the main script that iterates overall schedule through the appliance data folder'''
#################################################################### '''Optimise all appliances'''
start = time.perf_counter() # Benchmarking computation time: Start
''''#generation_available = 0 #This is only needed if you don't want generation to be considered - comment/uncomment as needed'''
fig, ax = plt.subplots(figsize=(50, 15)) # Setup the figure and axis once before loading files, 50 is width, 15 is height of graph   
df_demand_app = 0 #define this variable for use in for loop -- might change to empty value later
folder_path = Path("appliance data") #set the path to the appliance data
for file in sorted(folder_path.glob("*.csv")): #iterate through all appliance data .csv files in the appliance data folder
    appliance_data = pd.read_csv(file) #read .csv file, create dataframe
    appliance_name = file.stem #read appliance name from filename
    print(".........................................................................................")
    print("Optimising the '{}' Schedule:".format(appliance_name)) #Uses the filename as the name of the appliance to be scheduled
    appliance_data_wh = appliance_data["Wh"]
    appliance_data_kwh = appliance_data_wh / kwhr #convert Wh to kWh
    appliance_data_time = appliance_data["Time Start"]
    earliest_start = int(appliance_data.at[0, 'Earliest Start']) #convert first value in column to an integer
    latest_finish = int(appliance_data.at[0, 'Latest Finish']) #convert first value in column to an integer
    appliance_pu = np.array([appliance_data_kwh])#pu = power usage in kWh
    if generation_available == 1:#check if local generation.
        # Calculate Cost of running appliance pre-optimisation (appliance profile - generation)
        appprof_gen = appliance_data_kwh - generation #Only consider the energy that needs to be imported from the grid
        appprof_gen[appprof_gen < 0] = 0 #All negative values become 0 (if in a timeslot, generation is greater than appliance demand)
        grand_total, grand_total_permonth = calculate_cost(appprof_gen, rates)
        print("The starting cost per day is ${:.2f} prior to any scheduling optimisations.".format(grand_total))
        print("This equates to approximately ${:.2f} per month.".format(grand_total_permonth)) 
        appliance_profile = appliance_pu[appliance_pu != 0] #this removes all 0 numbers from profile (leading and lagging)
        print(f"Appliance Profile: {appliance_profile}") #Shows the appliance profiles timeslots length and energy usage
        start_tslot, total_grid = calculate_bestgen_start(generation, appliance_profile, excludedts, earliest_start, latest_finish) #optimise for local generation usage / minimise import
        start_time = df_time[start_tslot]
        total_grid = total_grid * -1
        print(f"Optimal Start Time Slot: {start_tslot}, Optimal Start Time: {start_time}, Total Energy Used from the Grid: {total_grid}kW") #need to check total_grid KK
        excludedts = excluded_tslots(appliance_profile, start_tslot, excludedts) #Exluded time slots function
        # Add start_tslot leading zeros (space 0 needs to be padded with a 0), & add 48 (total tslots) - (start_tslot+length of appliance runtime) lagging zeros:
        appliance_profile = np.pad(appliance_profile, (start_tslot, 48 - (start_tslot + len(appliance_profile))), mode='constant')
        # Calculate Cost of running appliance post-optimisation
        appprof_gen = appliance_profile - generation #Only consider the energy that needs to be imported from the grid
        appprof_gen[appprof_gen < 0] = 0 #All negative values become 0 (if in a timeslot, generation is greater than appliance demand)
        grand_total, grand_total_permonth = calculate_cost(appprof_gen, rates)
        print("The starting cost per day is ${:.2f} post scheduling optimisation.".format(grand_total))
        print("This equates to approximately ${:.2f} per month.".format(grand_total_permonth))
        generation = generation - appliance_profile # Update rolling generation
        generation[generation < 0] = 0
    else:
        #Modified generation available, need to check this
        appliance_profile = appliance_pu[appliance_pu != 0] #this removes all 0 numbers from profile (leading and lagging)
        print(f"Appliance Profile: {appliance_profile}") #Shows the appliance profiles timeslots length and energy usage
        start_tslot, total_cost = calculate_best_start(rates, appliance_profile, excludedts, earliest_start, latest_finish)#optimise for cost if no local generation usage available
        start_time = df_time[start_tslot]
        print(f"Optimal Start Time Slot: {start_tslot}, Optimal Start Time: {start_time}, Total Cost: ${total_cost}") #need to check total_cost KK
        excludedts = excluded_tslots(appliance_profile, start_tslot, excludedts) #Exluded time slots function
        # Add start_tslot leading zeros (space 0 needs to be padded with a 0), & add 48 (total tslots) - (start_tslot+length of appliance runtime) lagging zeros:
        appliance_profile = np.pad(appliance_profile, (start_tslot, 48 - (start_tslot + len(appliance_profile))), mode='constant')
    ax.step(appliance_data_time, appliance_profile, label=appliance_name) #add step plot of optimised appliance profile to Optimised Appliance Schedule Graph
    df_demand_app = df_demand_app + appliance_profile # Pass new schedule to demand profile
    df_demand_app[df_demand_app < 0] = 0 # Modify negative numbers to zero
#this needs to go into if/else statement or make new if/else statement    Check KK
    grand_total, grand_total_permonth = calculate_cost(df_demand_app, rates) # Find new cost - KK need to check
print(".........................................................................................")
end = time.perf_counter() #Benchmarking computation time: End
print(f"Execution time: {end - start:.6f} seconds") #Print execution time
'''############################################################################################################## Plot the Optimised Appliance Schedule Graph'''
#Finalise and display the graph after the for loop completes:
ax.set_title("Optimised Appliance Schedule")
ax.set_ylabel("kW")
#plt.ylim(0,5) #min to max y values
ax.step(appliance_data_time, blackzeroes, '-k', label=None) #this makes all 0 values appear black, for aesthetics only
#Settings for secondary x axis:
sec = ax.secondary_xaxis(location=-0.025)
sec.set_xticks(df.iloc[:, 0])
sec.set_xticklabels(df.iloc[:, 2]) #not used: , rotation=45, ha="left")
sec.spines['bottom'].set_linewidth(0)
sec.set_xlabel('Time Slot Start/Finish Times') #this is label for secondary xaxis, can't use label on primary x axis
ax.legend()  # Automatically displays labels for all files
ax.grid(True)
plt.setp(plt.gca().get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the x axis to false
plt.setp(sec.get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the secondary x axis to false
plt.show()
'''############################################################################################################## Post Optimisation Cost and Comparison'''
#This then calculates final cost after all optimisations:
df_demand_app = df_demand_app + df_demand
df_over_all = df_demand_app - df_generation #KK for calculation
df_over_all.loc[df_over_all < 0] = 0 #All negative values become 0 (if in a timeslot, generation is greater than appliance demand)
grand_total, grand_total_permonth = calculate_cost(df_over_all, rates)
print("The starting cost per day is ${:.2f} after scheduling optimisations.".format(grand_total))
print("This equates to approximately ${:.2f} per month.".format(grand_total_permonth))
print(".........................................................................................")
post_opt_gt = grand_total
post_opt_gtm = grand_total_permonth
saving_gt = pre_opt_gt - post_opt_gt
saving_gtm = pre_opt_gtm - post_opt_gtm
print("The cost saving per day pre vs post optimisation of the appliance schedules is ${:.2f}.".format(saving_gt))
print("This equates to approximately ${:.2f} per month.".format(saving_gtm))
print(".........................................................................................")
'''############################################################################################################## Graphing -- '''
generation = generation - df_demand
generation.loc[generation < 0] = 0 #All negative values become 0 (if in a timeslot, generation is greater than appliance demand)
fig, ax = plt.subplots(figsize=(50, 15)) #50 is width, 15 is height of grap
plt.rcParams.update({'font.size': 18})  
plt.title('Household Demand Data Post Optimisation')
plt.ylabel('kW')
plt.plot(df_time, generation, color='g', linestyle='-.',marker='') ##1 is x, 2 is y
#plt.plot(df_time, df_demand, color='r', linestyle='--',marker='') ##1 is x, 2 is y
#plt.plot(df_time, df_demand_app, '-k') ##1 is x, 2 is y
plt.plot(df_time, df_over_all, '-k') ##1 is x, 2 is y
#Settings for secondary x axis:
sec = ax.secondary_xaxis(location=-0.025)
sec.set_xticks(df.iloc[:, 0])
sec.set_xticklabels(df.iloc[:, 2]) #not used: , rotation=45, ha="left")
sec.spines['bottom'].set_linewidth(0)
sec.set_xlabel('Time Slot Start/Finish Times') #this is label for secondary xaxis, can't use label on primary x axis
#plt.ylim(0,5) #min to max y values
plt.setp(plt.gca().get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the x axis to false
plt.setp(sec.get_xticklabels()[1::2], visible=False) # Set visibility of every 2nd label of the secondary x axis to false
plt.legend(['Unused Generation', 'Base Demand w/Appliances - Generation']) #show the legend
#plt.legend(['Unused Generation','Base Demand', 'Base Demand w/Appliances - Generation']) #show the legend
plt.grid(True)
plt.show()
'''##############################################################################################################'''
'''###this prints the data type
print(type(df_demand_app))
###use this to show the data types
#print(df_list.dtypes)
#df_list.to_csv('outputs/combined_appliance_data1.csv', index=False) # index=False prevents saving row numbers
###this exports dataframe to .csv
#df = pd.DataFrame(data)
#df_demand_app.to_csv('output_pandas_post.csv', index=False) # index=False prevents saving row numbers
#df_demand.to_csv('output_pandas_pre.csv', index=False) # index=False prevents saving row numbers
##################################################################'''