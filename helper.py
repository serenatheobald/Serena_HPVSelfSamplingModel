import pandas as pd
import numpy as np
from os import chdir
from glob import glob

# Times:
# 9.3515 with 100 women and 100 cycles (scenario 0)
# 107.06 with 1,000 women and 100 cycles
# 49.600 with 100 women and 500 cycles
# 28.47 with 100 women and 100 cycles (scenario 1)

# Scenarios[i] = Vaccinate (y/n), age at first dose, cd4 limit, [fourth dose, timing], [screening age, freq]
scenarios = {0: (False, None, 1, [False, 12], [21, 3]), 1: (True, 11, 1, [False, 12], [21, 3]),
             2: (True, 9, 1, [False, 12], [21, 3]), 3: (True, 11, 3, [False, 12], [21, 3]),
             4: (True, 11, 1, [True, 12], [21, 3])}

# need to add scenarios/options for:
# 0) everyone vaccinated and vaccine 100% efficacious
# 1) everyone vaccinated at normal population efficacy
# 2) everyone vaccinated at PHACS efficacy
# 3) proportion vaccinated in PHACS vaccinated at PHACS efficacy
# vaccinations[i] = % vaccinated (each dose), % efficacy against HPV16, % efficacy against HPV18
vaccinations = {0: ([1, 1, 1, 1], 1, 1), 1: ([1, 1, 1, 1], 0.86, 0.86), 2: ([1, 1, 1, 1], 0.9, 0.62),
                3: ([0.9, 0.9, 0.9, 0.9], 0.9, 0.62)}

# Dictionary of HPV infection types
infectionlist = ['HPV16', 'HPV18', 'HPV31', 'HPV33', 'HPV45', 'HPV52', 'HPV58']

# Dictionary of CIN types
CINlist = ['CIN2', 'CIN3']


def export_population(population, characteristics):
    """
    Export a csv file with the name "filename.csv" to your working directory.
    Columns of the dataset are Name and attributes from characteristics, each row is a person from population
    example: export_population(population, ('cycleMonth', 'cd4', 'ARTtime', 'cancer'))
    :param population: a list of instances of the "women" class
    :param characteristics: a list of attributes for which you would like to print information about
    :return: a dataset with ID, cycle, and characteristics as columns
    """
    data = {'Name': [], 'Cycle': []}
    for item in characteristics:
        data[item] = []
    for person in population:
        data["Name"].append(person.id)
        data["Cycle"].append(person.cycleMonth)
        for item in characteristics:
            if getattr(person, item) is None:
                data[item].append(0)
            else:
                data[item].append(getattr(person, item))
    return data

    # if scenario is None:
    # datatest.to_csv("/Users/rbarnardmayersmph/PycharmProjects/HPVVaccineModel/Output/" + filename + ".csv")
    # else:
    # datatest.to_csv("/Users/rbarnardmayersmph/PycharmProjects/HPVVaccineModel/Output/" + str(scenario) +
    # "/" + filename + ".csv")


def produceOneCSV(list_of_files, file_out, custtype=None):
    # Consolidate all CSV files into one object
    if custtype is None:
        result_obj = pd.concat([pd.read_csv(file) for file in list_of_files])
    else:
        types = {}
        for column in custtype:
            types[column] = object
        result_obj = pd.concat([pd.read_csv(file, dtype=types) for file in list_of_files])
    # Convert the above object into a csv file and export
    result_obj.to_csv(file_out, index=False, encoding="utf-8")


def merge_output(scenario=None, folder='/Users/serenatheobald/Downloads/',
                 filename="AllRuns_data.csv", custtype=None):
    """    :param folder: directory in which to write exported file
    :param filename: name of merged file, if different from "AllRuns_data"
    :param custtype: name of attribute that is list, only one list column allowed
    :param scenario: scenario folder to add to folder path, if desired
    :return: csv file in specified directory
    """

    if scenario is None:
        csv_file_path = folder
    else:
        csv_file_path = folder + str(scenario) + "/"
    chdir(csv_file_path)
    file_pattern = ".csv"
    list_of_files = [file for file in glob('*'.format(file_pattern))]
    produceOneCSV(list_of_files, filename, custtype)


def get_CD4prog(woman):
    """
    :param data: instance of data class
    :param woman: instance of women class
    :return: new CD4 category value"
    """
    cd4start = woman.cd4num
    if woman.ART:
        change = np.random.normal(4.039638, 181.3373)
        if cd4start + change >= 1400:
            return cd4start
        else:
            return cd4start + change
    else:
        change = np.random.normal(16.63768, 138.5521)
        if cd4start - change <= 500:
            return cd4start
        else:
            return cd4start - change


def get_CD4prog_og(woman, data):
    """
    :param data: instance of data class
    :param woman: instance of women class
    :return: new CD4 category value"
    """
    cd4start = woman.cd4
    if cd4start == 1:  # if CD4 less than 200
        if woman.ART:
            progress = data.CD4_ART.iloc[int(woman.ARTtime / 12), 1:5]
        else:
            progress = data.CD4_NOART.iloc[woman.ageYears, 1:7]
    elif cd4start == 2:  # if CD4 between 200 and 349
        if woman.ART:
            progress = data.CD4_ART.iloc[int(woman.ARTtime / 12), 5:9]
        else:
            progress = data.CD4_NOART.iloc[woman.ageYears, 1:7]
    elif cd4start == 3:  # if CD4 between 350 and 499
        if woman.ART:
            progress = data.CD4_ART.iloc[int(woman.ARTtime / 12), 9:13]
        else:
            progress = data.CD4_NOART.iloc[woman.ageYears, 1:7]
    else:  # if CD4 500+
        if woman.ART:
            progress = data.CD4_ART.iloc[int(woman.ARTtime / 12), 13:]
        else:
            progress = data.CD4_NOART.iloc[woman.ageYears, 1:7]

    if woman.ART:
        val = np.random.choice([4, 3, 2, 1], 1, p=progress)
    else:
        val = np.random.choice([4, 3, 2, 2, 1, 1], 1, p=progress)

    return val[0]

def get_list(woman):
    aa = []
    for item in dir(woman):
        if item[:2] != "__":
            aa.append(item)
        else:
            pass
    attributes = []
    for item in aa:
        if "_" in item:
            pass
        else:
            attributes.append(item)
    return attributes


def get_duration(population, active=False):
    time_list = {'HPV16': [], 'HPV18': [], 'HPV31': [], 'HPV33': [], 'HPV45': [], 'HPV52': [], 'HPV58': []}
    for person in population:
        if not active:
            for infection in person.hpvh:
                time_list[infection.Type].append(infection.mTimer)
        else:
            all_infections = person.hpvh + person.activeinfections
            for infection in all_infections:
                time_list[infection.Type].append(infection.mTimer)
    return time_list