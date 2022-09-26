from statistics import mean
import math
import random
import numpy as np
# https://github.com/lvphj/epydemiology/wiki/Calculate-relative-risks-for-cross-sectional-or-longitudinal-studies


def rate_to_prob(rate, t=1/12):
    '''
    Function that converts a given rate to a probability for use in the model
    :param rate: numeric value
    :return: probability (between 0 and 1)
    '''
    risk = 1- math.e**(-rate * t)
    return risk


def mean_age(population):
    '''
    Function that takes a population, creates a list of ages (in months) of all people, and returns the mean
    :param population: a list of instances of the women class
    :return: mean values for population's age (in  years)
    '''
    t = ()
    for person in population:
        t = t + (int(person.ageYears),)
    return mean(t)


def num_dead(population):
    '''
    Count the number of dead women in a population
    :param population: list of instances of "women" class
    :return: Number of dead people from the population, and the average age of the dead population
    '''
    deadage = []

    for person in population:
        if not person.alive:
            deadage.append(person.agedeath)

    print("Number of dead women:", len(deadage))
    if len(deadage) > 0:
        print("Average age of death:", (sum(deadage) / len(deadage)))


# Function to calculate prevalence
def prevalence(population, characteristic, casedef):
    '''
    Takes a characteristic of a population and calculates the incidence of casedef in the population
    :param population: list of instances of Women class
    :param casedef: string indicating what a case is for incidence calculation
    :param characteristic:  attribute for which to calculate incidence
    :return:
    '''
    total = len(population)
    cases = 0
    for person in population:
        if isinstance(person.__getattribute__(characteristic), list):
            for item in person.__getattribute__(characteristic):
                if item == casedef:
                    cases += 1
                else:
                    pass
        else:
            if person.__getattribute__(characteristic) == casedef:
                cases += 1
            else:
                pass
    prev = cases/total
    return prev
    # print("Prevalence of " + casedef, prev)


def count_bool(histories):
    total = histories.count(True)
    return total


def check_random(value):
    '''
    Determines whether a value is greater than a random number between 0 and 1. AKA given value, returns
    whether or not that actually happens
    :param value: probability
    :return: boolean
    '''
    if value > random.random():
        return True
    else:
        return False