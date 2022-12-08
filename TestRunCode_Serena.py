import configparser
from Classes_Serena import Data, Women
from Statemachine_Serena import run_1month
from helper import *
from calculationhelper import *
from statistics import mean
from pathlib import Path
import timeit
import sys


# 100 times ,run main with exeample 0, example 1 

def main(file="example0.ini"):
    start = timeit.default_timer()

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = file

    model_data = []
    config = configparser.ConfigParser()
    config.read(filename)
    sections = config.sections()
    for section in sections:
        model_data.append(Data(config[section]))

    for run in range(len(model_data)):
        population = list(range(model_data[run].COHORTSIZE))

        for i in range(len(population)):
            population[i - 1] = Women(i, model_data[run])

        Women.screening_age = scenarios.get(model_data[run].SCENARIO)[4][0]
        Women.screening_freq = scenarios.get(model_data[run].SCENARIO)[4][1]

        allstats = pd.DataFrame()
        deadwomen = []
        statsofinterest = {"Cycle": []}
        for infection in infectionlist:
            statsofinterest[infection] = []

        #pulls COUNTER value from ini file and put into model_data
        counter = model_data[run].COUNTER
        
        while counter < model_data[run].NUMMONTHS:
            for woman in population:
                run_1month(woman, infectionlist, model_data[run])
                if woman.agedeath is not None and woman not in deadwomen:
                    deadwomen.append(woman)
                woman.cycle_step()

                if counter % 12 == 0:  # can add any characteristic of "Woman"
                    allstats = allstats.append(pd.DataFrame(export_population(population, ('ageYears', 'cd4hnum',
                                                                                           'screenresulthpv',
                                                                                           'selfscreenresulthpv'))))
            if counter % 12 == 0:
                print(counter / 12)
            statsofinterest['Cycle'].append(counter)
            for infection in infectionlist:
                statsofinterest[infection].append(prevalence(population, 'activetypes', infection))
            counter += 1
            # bar.next()
            
            
        allstats_output = "Run_" + str(run) + ".csv"
        outputdir = Path("/Users/serenatheobald/Downloads/output/" + str(model_data[run].SCENARIO))
       
        outputdir.mkdir(parents = True, exist_ok = True)
        

        allstats.to_csv(outputdir / allstats_output)

        prevdata = pd.DataFrame(statsofinterest)
        prevdata_output = "HPVStats_" + str(run) + ".csv"
        prevdata.to_csv(outputdir / prevdata_output)
        
        

        dead_data = pd.DataFrame(export_population(deadwomen, ('agedeath', 'cause', 'activetypes', 'cancer', 'cd4num')))
        dead_data_output = "DeadWomen_" + str(run) + ".csv"
        dead_data.to_csv(outputdir / dead_data_output)
        

        print('Run time: ', timeit.default_timer() - start)

        d = get_duration(population, active=True)
        for strain in d:
            if d[strain]:
                print('Average duration of ', strain, ' :', mean(d[strain]), 'for run', run)

        num_dead(population)


if __name__ == "__main__":

    #range 0 to 5 now
    for x in range(0,5):
        main(file="example0.ini")
        x +=1
        
        

    for y in range(0,5):
        main(file="example1.ini")
        y +=1
      
        
    for z in range(0,5):
        main(file="example2.ini")
        z+=1
       
        
       #100 women who have possibility of living up to 100 years, running 1 iteration per company (3 companies)
       # eventually increase women or iterations
        
