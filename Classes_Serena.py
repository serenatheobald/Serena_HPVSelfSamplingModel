import random
import math
import pandas as pd
import numpy as np
from helper import vaccinations
from calculationhelper import check_random
from enum import Enum


class CancerStage(Enum):
    Stage1 = 0
    Stage2 = 1
    Stage3 = 2
    Stage4 = 3


class Data:
    """"
    NEED TO FIGURE OUT DOSAGE EFFICACY
    Data class that holds information on HPV, HIV, and Vaccine transmission from ini file
    """

    def __init__(self, section):
        self.COHORTSIZE = int(section["COHORT_SIZE"])
        self.NUMYEARS = int(section["SIM_YEARS"])
        self.NUMMONTHS = self.NUMYEARS * 12
        self.SCENARIO = int(section["SCENARIO"])
        self.VACCINATIONS = int(section["VACCINATIONS"])
        self.VACCINEIMMUNITY = pd.DataFrame(data={'HPV06': [0, 0, 0, 0], 'HPV11': [0, 0, 0, 0],
                                                  'HPV16': [vaccinations.get(self.VACCINATIONS)[1] / 4,
                                                            vaccinations.get(self.VACCINATIONS)[1] / 2,
                                                            vaccinations.get(self.VACCINATIONS)[1],
                                                            vaccinations.get(self.VACCINATIONS)[1]],
                                                  'HPV18': [vaccinations.get(self.VACCINATIONS)[2] / 4,
                                                            vaccinations.get(self.VACCINATIONS)[2] / 2,
                                                            vaccinations.get(self.VACCINATIONS)[2],
                                                            vaccinations.get(self.VACCINATIONS)[2]],
                                                  'HPV31': [0, 0, 0, 0], 'HPV33': [0, 0, 0, 0], 'HPV45': [0, 0, 0, 0],
                                                  'HPV52': [0, 0, 0, 0], 'HPV58': [0, 0, 0, 0]})
        self.MORTALITY = pd.read_csv(section["MORTALITY_FILE"])
        self.HPVCLEARANCE = pd.read_csv(section["HPV_CLEARANCE_FILE"])
        self.HPVPROGRESS = pd.read_csv(section["HPV_PROGRESS_FILE"])
        self.HPVINCIDENCE = pd.read_csv(section["HPV_RISK"])  # names of columns are HPV types
        self.PROGRESS_Mult_ART = float(section["PROGRESS_CIN_ART"])
        self.PROGRESS_Mult = float(section["PROGRESS_CIN"])
        self.REGRESS_Mult_ART = float(section["REGRESSION_CIN_ART"])
        self.REGRESS_Mult = float(section["REGRESSION_CIN"])
        self.SEXUALACTIVITY = [0, .009646302, .009646302, 0.032154341, 0.086816720, 0.163987138, 0.218649518,
                               0.241157556, 0.170418006, 0.061093248, 0.006430868]
        self.SELFTESTING = pd.read_csv(section["SELFTESTING_DATA"])
        self.LAB = int(section["LAB"])  # specifying which lab data to use
        
        ##Source of error:
        self.CLINICALTESTING = pd.read_csv(section["CLINICALTESTING_DATA"])
        self.VALUE = int(section["Value"])
        self.COUNTER = int(section["COUNTER"])
        
        
        
        



class Infection:
    """Class of HPV infections that takes infection name (str) and data (Data class)"""

    def __init__(self, infection, data):
        self.mTimer = 1
        self.yTimer = 0
        self.Type = infection
        self.InfectionAge = None
        self.diagnosed = False
        self.diagnosedself = False
        # self.duration = pd.DataFrame(data.HPVDURATION[self.Type])
        self.HPVClearance = pd.DataFrame(data.HPVCLEARANCE[self.Type])
        self.HPVProgress_CIN2 = pd.DataFrame(data.HPVPROGRESS[self.Type + "CIN2"])
        self.HPVProgress_CIN3 = pd.DataFrame(data.HPVPROGRESS[self.Type + "CIN3"])

    # returns the probability of progression to CIN stage from HPV infection, duration specific
    def get_progression(self):

        z = random.random()
        if z == 0:
            x = float(self.HPVProgress_CIN2.iloc[self.yTimer])
            return [x, "CIN2"]
        else:
            x = float(self.HPVProgress_CIN3.iloc[self.yTimer])
            return [x, "CIN3"]

    # returns the probability of clearing HPV, duration specific
    def get_clearance(self):
        y = float(self.HPVClearance.iloc[math.floor(self.mTimer / 12)])
        return y


# CIN regression and progression are hard-coded
class CIN:
    def __init__(self, cintype, infectiontype, woman):
        self.CINtype = cintype
        self.CINTimer = 1
        self.CINAge = None
        self.CINtoCancerTime = np.random.gamma(5.13, 4.90)
        self.infectiontype = infectiontype
        self.diagnosed = False
        if self.CINtype == 2:
            self.CINRegression = 0.47 * woman.regmult
        else:
            self.CINRegression = 0.58 * woman.regmult
        self.CINProgress = woman.progmult * np.random.normal(0.34, 0.99 - 0.28 / (1.96*2))

    # returns bool: CIN progresses (true) or not (false)
    def CIN_progression(self):
        # if self.CINTimer / 12 >= self.CINInfectionTime:
        # prob = np.random.normal(0.34, 0.17857142857142858)
        return check_random(self.CINProgress[self.CINTimer - 1])
        # return check_random(prob)

    def CIN_regression(self):
        b = self.CINTimer  # math.floor(self.CINTimer)-1
        if b < 0:
            b = 0
        else:
            b = self.CINRegression
        return check_random(b)


# Progression and Regression Probabilities hard-coded
class Cancer:
    def __init__(self):
        self.mCancerTimer = 1
        self.yCancerTimer = 0

    def progress_cancer(self):
        pass

    def regress_cancer(self):
        pass


class CStage1(Cancer):
    def __init__(self, data):
        super(CStage1, self).__init__()
        self.CancerAge = None
        self.CancerType = CancerStage.Stage1
        self.CancerName = "CA1"
        self.Diagnosed = False
        self.CancerMortality = data.MORTALITY["CA1"]
        self.Progression = .4
        self.Regression = .2

    def progress_cancer(self):
        check_random(self.Progression)

    def regress_cancer(self):
        check_random(self.Regression)


class CStage2(Cancer):
    def __init__(self, data):
        super(CStage2, self).__init__()
        self.CancerAge = None
        self.CancerType = CancerStage.Stage2
        self.CancerName = "CA2"
        self.Diagnosed = False
        self.CancerMortality = data.MORTALITY["CA2"]
        self.Progression = .4
        self.Regression = .2

    def progress_cancer(self):
        check_random(self.Progression)

    def regress_cancer(self):
        check_random(self.Regression)


class CStage3(Cancer):
    def __init__(self, data):
        super(CStage3, self).__init__()
        self.CancerAge = None
        self.CancerType = CancerStage.Stage3
        self.CancerName = "CA3"
        self.Diagnosed = False
        self.CancerMortality = data.MORTALITY["CA3"]
        self.Progression = .5
        self.Regression = .1

    def progress_cancer(self):
        check_random(self.Progression)

    def regress_cancer(self):
        check_random(self.Regression)


class CStage4(Cancer):
    def __init__(self, data):
        super(CStage4, self).__init__()
        self.CancerAge = None
        self.CancerType = CancerStage.Stage4
        self.CancerName = "CA4"
        self.Diagnosed = False
        self.CancerMortality = data.MORTALITY["CA4"]
        self.Progression = .7
        self.Regression = .01

    def progress_cancer(self):
        check_random(self.Progression)

    def regress_cancer(self):
        check_random(self.Regression)


class Women:
    """
    Class of women with perinatally acquired HIV infection
    """
    cycleMonth = 0  # current time in months
    cycleYear = 0  # current time in years
    ARTdropout = .007  # likelihood of dropping off ART once on
    # natural simulation is 2 months, 6 months
    vaccine_spacing = [2, 6]
    screening_age = None  # age in years
    screening_freq = None  # years

    def __init__(self, name, data):
        self.id = name
        self.ageMonths = 84
        self.ageYears = 7
        self.sexactive_age = np.random.choice([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], 1, p=data.SEXUALACTIVITY)
        self.sexactive = False

        # HPV Infection information (active and inactive infections)
        self.hpvh = []
        self.activeinfections = []
        self.activetypes = []
        self.activeages = []

        # CIN lesions information (active and inactive lesions)
        self.lesionh = {"CIN2": [], "CIN3": []}
        self.activelesion = []  # Change to a list
        self.activelesiontype = []  # Change to a list

        # self.caT = {"Stage1": False, "Stage2": False, "Stage3": False, "Stage1d": False,
        #             "Stage2d": False, "Stage3d": False}

        # Clinical screening information (lines 229-239)
        self.screenresulthpv = {'HPV16': None, 'HPV18': None, 'HPV31': None, 'HPV33': None, 'HPV45': None,
                                'HPV52': None, 'HPV58': None}
        self.screenresultCIN = {"CIN2": None, "CIN3": None}

        # self-screening attributes
        self.selfscreenresulthpv = {'HPV16': None, 'HPV18': None, 'HPV31': None, 'HPV33': None, 'HPV45': None,
                                    'HPV52': None, 'HPV58': None}
        self.selfscreenresultCIN = {"CIN2": None, "CIN3": None}

        self.everscreen = False
        self.firstscreenage = None
        self.lastscreenage = None

        self.cancer = None
        self.cancerstage = None
        self.mCancerTimer = 0

        # HPV Vaccine information
        self.vaccinedoses = 0
        self.vaccineage = []

        self.alive = True
        self.agedeath = None  # Only given a value when dead
        self.cause = None
        self.mortality = data.MORTALITY  # ['Background'], ['HIV'], [CA1'], ['CA2'], ['CA3'], ['CA4']

        #  based on PHACS distribution at age 9 (no 7 year olds and only 12 8 yr olds)
        self.cd4num = np.random.normal(767.5000, 257.5332)
        if self.cd4num < 250:
            self.cd4cat = 1
        elif self.cd4num >= 250:
            if self.cd4num < 350:
                self.cd4cat = 2
            elif self.cd4num < 500:
                self.cd4cat = 3
            else:
                self.cd4cat = 4
        self.cd4hcat = []
        self.cd4hnum = []

        self.ART = check_random(.1257)  # may eventually be data driven
        if not self.ART:
            self.ARTtime = None
        else:
            self.ARTtime = random.randrange(60, 84)  # generate month when started ART
        self.ARTh = []

        if self.ART:
            self.progmult = data.PROGRESS_Mult_ART
        else:
            self.progmult = data.PROGRESS_Mult

        if self.ART:
            self.regmult = data.REGRESS_Mult_ART
        else:
            self.regmult = data.REGRESS_Mult

    # This function adds one to the time tracker cycleMonth
    # If the number of months is divisible by 12, add one to the year cycle tracker
    def cycle_step(self):
        self.cycleMonth += 1
        if self.cycleMonth % 12 == 0:
            self.cycleYear += 1

    # This function makes the woman age 1 month
    # of the month is divisible by 12, age one year as well
    def age_step(self):
        self.ageMonths += 1
        if self.ageMonths % 12 == 0:
            self.ageYears += 1

    def record_death(self):
        self.alive = False
        self.agedeath = self.ageYears

    def update_sex(self):
        if self.ageYears == self.sexactive_age:
            self.sexactive = True
        else:
            self.sexactive = False

    # This function appends current ART status to ART history list
    def add_ART(self):
        self.ARTh.append(self.ART)

    # initiate ART and record ART start time as current age (in months)
    def start_ART(self):
        self.ART = True
        self.ARTtime = self.ageMonths

    # takes the current cd4 value and appends it to the list of all previous cd4
    def add_cd4(self):
        self.cd4hcat.append(self.cd4cat)
        self.cd4hnum.append(self.cd4num)

    # categorizes updated numerical cd4 value
    def update_cd4(self):
        if self.cd4num < 250:
            self.cd4cat = 1
        elif self.cd4num >= 250:
            if self.cd4num < 350:
                self.cd4cat = 2
            elif self.cd4num < 500:
                self.cd4cat = 3
            else:
                self.cd4cat = 4

    # Give a woman an HPV vaccine dose and add her age to list of vaccine ages
    def give_vaccine(self):
        self.vaccinedoses += 1
        self.vaccineage.append(self.ageMonths)

    # takes an instance of HPV infection and appends it to the list of all hpv infections
    def clear_hpvinfection(self, infection):
        # self.infection.duration = self.infection.mTimer
        self.hpvh.append(infection)
        self.activeinfections.remove(infection)

    # creates an instance of an HPV infection and adds it to woman's infection information
    def acquire_infection(self, infection, data):
        # if self.sexactive <= self.ageYears:
        x = Infection(infection, data)
        x.InfectionAge = self.ageYears
        self.activeinfections.append(x)
        self.activetypes.append(infection)
        self.activeages.append(self.ageYears)
        # else:
        # pass

    # Initiates CIN lesion from HPV infection
    def acquire_CIN(self, cintype, infection):
        y = CIN(cintype, infection.Type, self)
        y.CINAge = self.ageYears
        self.activelesion.append(y)
        self.activelesiontype.append(y.CINtype)
        self.lesionh[cintype].append(infection)

    def clear_CIN(self, lesion):
        self.activelesion.remove(lesion)
        self.activelesiontype.remove(lesion.CINtype)

    def acquire_cancer(self, data):
        """
        This function initiates a stage 1 cancer class
        :param data: Data used for Cancer class initiation
        :return: Changes cancer stage for woman to one stage lower
        """
        # self.caT["Stage0"] = True
        self.cancer = CStage1(data)
        self.cancerstage = self.cancer.CancerName
        self.mCancerTimer += 1

    # changes current cancer to next stage
    def progression_cancer(self, data):
        """
        This function progresses a woman's cancer
        :param data: Data used for Cancer class initiation
        :return: Changes cancer stage for woman to one stage higher
        """
        if self.cancer.CancerName == "CA1":
            self.cancer = CStage2(data)
            self.cancerstage = self.cancer.CancerName
        elif self.cancer.CancerName == "CA2":
            self.cancer = CStage3(data)
            self.cancerstage = self.cancer.CancerName
        elif self.cancer.CancerName == "CA3":
            self.cancer = CStage4(data)
            self.cancerstage = self.cancer.CancerName
        else:  # when self.cancer.CancerName == "CA4"
            self.record_death()

    def regression_cancer(self, data):
        """
        This function regresses a woman's cancer
        :param data: Data used for Cancer class initiation
        :return: Changes cancer stage for woman to one stage lower
        """
        if self.cancer.CancerName == "CA4":
            self.cancer = CStage3(data)
            self.cancerstage = self.cancer.CancerName
        elif self.cancer.CancerName == "CA3":
            self.cancer = CStage2(data)
            self.cancerstage = self.cancer.CancerName
        elif self.cancer.CancerName == "CA2":
            self.cancer = CStage1(data)
            self.cancerstage = self.cancer.CancerName
        else:  # when self.cancer.CancerName == "CA1"
            pass

    # Screening
    def update_screening(self):
        self.lastscreenage = self.ageYears ## if last screen age is = to current age
        self.everscreen = True

    # Returns a bool for whether woman dies from background mortality
    def check_bgmort(self):
        return check_random(self.mortality.loc[self.ageYears, "Background"])

    # Returns a bool for whether woman dies from HIV
    def check_hivmort(self):
        return check_random(self.mortality.loc[self.ageYears, "HIV"])

    # Returns a bool for whether woman dies from cancer
    def check_cancermort(self, cancer):
        if cancer.Diagnosed is False:
            return check_random(self.mortality.iloc[self.ageYears][cancer.CancerName])
        if cancer.Diagnosed:
            return check_random(self.mortality.iloc[self.ageYears][cancer.CancerName + "D"])