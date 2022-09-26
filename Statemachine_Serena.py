from helper import scenarios, get_CD4prog, infectionlist, vaccinations
from calculationhelper import check_random


def life_update(woman):
    """
    Runs through background, HIV and Cancer mortality
    :param woman: an instance of the woman class
    :return: updates a woman's life status and age death (if applicable)
    """
    if woman.alive:
        if woman.check_bgmort():
            woman.record_death()
            woman.cause = 'Background'
        elif woman.check_hivmort():
            woman.record_death()
            woman.cause = 'HIV'
        elif woman.cancer:
            if woman.check_cancermort(woman.cancer):
                woman.record_death()
                woman.cause = str('Cancer:' + woman.cancerstage)


def HIV_update(woman, data):
    """
    Updates a woman's ART and CD4 status
    :param woman: an instance of the Women class
    :param data: an instance of Data class
    :return: updates ART history, current status, CD4 history and cd4 current status
    """
    if woman.alive:
        # append current ART to history list
        woman.add_ART()

        # append current CD4/VL to history list
        woman.add_cd4()

        woman.cd4num = get_CD4prog(woman)
        woman.update_cd4()

        # if the woman is on ART, calculate dropout likelihood:
        if woman.ART:

            if check_random(woman.ARTdropout):
                woman.ART = False

        # if the woman is not on ART, calculate ART initiation likelihood and decrease cd4:
        else:
            # determine whether initiates ART (*will change)
            # if low cd4 (below 500) 80% chance of starting ART
            if woman.cd4cat < 4:
                x = .8
            # if high cd4 (at least 500) 60% chance of starting ART
            else:
                x = .4
            # start ART given above distribution
            if check_random(x):
                woman.start_ART()


def HPV_update(woman, data):
    """
    Runs through active infections and progresses, regresses or continues infection
    :param woman: an instance of the Women class
    :param data: an instance of the class Data
    :return: updates a woman's active infections, HPV infection history and infection information
    """
    if woman.alive:
        for infection in woman.activeinfections:
            if woman.vaccinedoses == 0:  # if the woman has not received a vaccine
                c = infection.get_progression()
                b = float(c[0]) * woman.progmult
                a = [b, c[1]]
                if check_random(a[0]):
                    woman.acquire_CIN(a[1], infection)
                    infection.mTimer += 1
                    if infection.mTimer % 12 == 0:
                        infection.yTimer += 1
                        # remove infection from current infections?
                elif check_random(infection.get_clearance() * woman.regmult):
                    woman.clear_hpvinfection(infection)
                else:
                    infection.mTimer += 1
                    if infection.mTimer % 12 == 0:
                        infection.yTimer += 1
            else:  # if she has received a vaccine, factor vaccine immunity into equation
                if check_random(infection.get_clearance() * woman.regmult):
                    woman.clear_hpvinfection(infection)
                elif check_random(data.HPVINCIDENCE.loc["Main", infection] *
                                  (1 - data.VACCINEIMMUNITY[infection.Type].loc[woman.vaccinedoses])):
                    c = infection.get_progression()
                    b = float(c[0]) * woman.progmult
                    a = [b, c[1]]
                    if check_random(a[0]):
                        woman.acquire_CIN(a[1], infection, data)
                        infection.mTimer += 1
                        if infection.mTimer % 12 == 0:
                            infection.yTimer += 1
                else:
                    infection.mTimer += 1
                    if infection.mTimer % 12 == 0:
                        infection.yTimer += 1
    # else:
    #     pass


def HPV_newinfection(woman, infections, data):
    """
    Scans list of possible infections and gives new infection by likelihood
    :param woman: an instance of the women class
    :param infections: list of strings of possible HPV infections
    :param data: instance of the Data class
    :return: adds new infection to woman's activeinfections list
    """
    if woman.alive and woman.sexactive:
        for infection in infections:
            if infection not in woman.activetypes:
                if check_random(data.HPVINCIDENCE.loc["Main", infection] *
                                (1 - data.VACCINEIMMUNITY[infection].loc[woman.vaccinedoses])):
                    if woman.vaccinedoses > 0:
                        if check_random(.3):  # if they are vaccinated, acquire infection 1/3 times
                            woman.acquire_infection(infection, data)
                    else:
                        woman.acquire_infection(infection, data)


# Regress or progress existing CIN infection
def CIN_update(woman, data):
    """
    For an active lesion, function either progresses, clears or maintains.
    :param woman: instance of woman class
    :param data: instance of data class
    :return: updated CIN information for the woman
    """
    if woman.alive:
        if len(woman.activelesion) == 0:  # If no active lesions, do nothing
            pass
        else:
            for lesion in woman.activelesion:
                if lesion.CIN_regression():
                    woman.clear_CIN(lesion)
                elif lesion.CIN_progression():
                    woman.acquire_cancer(data)
                else:
                    lesion.CINTimer += 1


# assuming she has cancer
def cancer_update(woman, data):
    """
    updates a woman's cancer status (Only valid for women with cancer)
    :param woman: instance of woman class
    :param data: instance of data class
    :return: updated cancer information for the woman
    """
    if woman.alive:
        if woman.cancer.progress_cancer():  # she either progresses
            woman.progression_cancer(data)
            woman.cancer.mCancerTimer += 1
        elif woman.cancer.regress_cancer():  # or regresses
            woman.regression_cancer(data)  # Cancer stage 1 lower bound?
        else:  # or nothing happens to the cancer
            woman.cancer.mCancerTimer += 1
    # else:
    #     pass


# Update vaccination information
def vaccination_update(woman, data):
    """
    Updates vaccine information for the woman, depending on the scenario of interest. Scenarios are:
    1) scenario 0: natural history, no vaccine given
    2) scenario 1: current implementation, 3 doses vaccine given starting age 11 with no other conditions
    3) scenario 2: 3 doses given starting age 9 with no other conditions
    4) scenario 3: 3 doses given starting age 11 with CD4 at least category 3 (i.e. > 349)
    5) scenario 4: 4 doses given starting age 11 with the fourth dose given 12 months after the 3rd
    :param woman: instance of the woman class
    :param data: instance of the data class
    :return: updated vaccine information
    """
    if woman.alive:
        # if vaccination is False for the scenario, don't vaccinate
        if not scenarios.get(data.SCENARIO)[0]:
            pass
        elif woman.ageYears < scenarios.get(data.SCENARIO)[1]:
            pass
        else:  # if there is no CD4 restriction, vaccinate woman based on spacing
            if scenarios.get(data.SCENARIO)[2] is None:
                if woman.vaccinedoses == 0:  # if will be first dose, give vaccine
                    if check_random(vaccinations.get(data.VACCINATIONS)[0][0]):
                        woman.give_vaccine()
                elif woman.vaccinedoses < 3:  # if will be 1st or 2nd dose, check vaccine spacing
                    if woman.ageMonths >= woman.vaccineage[woman.vaccinedoses - 1] + \
                            woman.vaccine_spacing[woman.vaccinedoses - 1]:
                        if check_random(vaccinations.get(data.VACCINATIONS)[0][woman.vaccinedoses]):  # prob of dose
                            woman.give_vaccine()
                elif woman.vaccinedoses >= 3:  # if has had 3 doses already
                    if scenarios.get(data.SCENARIO)[3][0]:  # If the scenarios involves a fourth dose
                        if woman.ageMonths >= woman.vaccineage[woman.vaccinedoses - 1] + \
                                scenarios.get(data.SCENARIO)[3][1]:
                            if check_random(vaccinations.get(data.VACCINATIONS)[0][3]):
                                woman.give_vaccine()  # all women who get 3rd will get 4th
            else:  # if there is a CD4 restriction
                if woman.cd4cat < scenarios.get(data.SCENARIO)[2]:  # if she doesn't meet CD4 requirement
                    pass
                else:  # if she meets the age and cd4 requirements
                    if woman.vaccinedoses == 0:  # if will be first dose, give vaccine
                        if check_random(vaccinations.get(data.VACCINATIONS)[0][0]):
                            woman.give_vaccine()
                    elif woman.vaccinedoses == 1:  # if will be second dose, check vaccine spacing
                        if woman.ageMonths >= woman.vaccineage[0] + woman.vaccine_spacing[0]:
                            if check_random(vaccinations.get(data.VACCINATIONS)[0][1]):
                                woman.give_vaccine()
                    elif woman.vaccinedoses == 2:  # if this will be third dose, check vaccine spacing
                        if woman.ageMonths >= woman.vaccineage[1] + woman.vaccine_spacing[1]:
                            if check_random(vaccinations.get(data.VACCINATIONS)[0][2]):
                                woman.give_vaccine()
                    else:  # woman.vaccindoses >= 3:  # if has had 3 doses already
                        if scenarios.get(data.SCENARIO)[3][0]:  # If the scenarios involves a fourth dose
                            if woman.ageMonths >= woman.vaccineage[0] + scenarios.get(data.SCENARIO)[3][1]:
                                if check_random(vaccinations.get(data.VACCINATIONS)[0][3]):
                                    woman.give_vaccine()  # all women who get 3rd will get 4th


def screening_update(woman, data):
    """
    Walk through the logic of screening. If she's old enough, check  frequency restrictions, then check if she has HPV
    and CIN. If she has HPV and no CIN, tests positive. If she has HPV and CIN, some % chance that she tests negative.
    If she tests positive, get diagnose and treated.
    :param woman: instance of class Woman
    :return: updates screening information and HPV/CIN status
    """
    if woman.alive:
        ## if she's older than screening age
        if woman.screening_age <= woman.ageYears:
            if not woman.everscreen or woman.ageYears >= woman.lastscreenage + woman.screening_freq:
                
                ## among people who are eligible, check if they are going to accept screning(95% are accepting this)
                if check_random(.95):  # 5% non-compliance with screenings
                    if woman.firstscreenage is None:
                        woman.firstscreenage = woman.ageYears
                    if len(woman.activeinfections) > 0:  # If has HPV infection
                        for infection in woman.activeinfections:
                            
                        
                        
                            if check_random(1-data.CLINICALTESTING.loc["Se", data.VALUE]):
                                woman.screenresulthpv[infection.Type] = "negative"  # False negative
                                
                            else:
                                woman.screenresulthpv[infection.Type] = "positive"  # True positive
                                infection.diagnosed = True

                                if len(woman.activelesion) > 0:  # If has CIN
                                    for lesion in woman.activelesion:
                                        if check_random(.05):  # 95% se
                                            woman.screenresultCIN[lesion.CINtype] = "negative"  # False Neg
                                        else:
                                            woman.screenresultCIN[lesion.CINtype] = "positive"  # True Pos
                                            # clear infection 90% of the time once diagnosed
                                            if check_random(.90):
                                                woman.clear_CIN(lesion)

                                else:  # if she does not have CIN, 100% sp
                                    woman.screenresultCIN['CIN2'] = "negative"
                                    woman.screenresultCIN['CIN3'] = "negative"

                    else:  # If has no HPV (100% sp), if truly negative, will always return negative result (we want to edit this)
                       
                        for infection in infectionlist:
                        
                            ## later change 0.047 to input variable
                            if check_random(data.CLINICALTESTING.iloc[1, data.VALUE]):  
                                woman.screenresulthpv[infection] = "negative"
                                    
                            else:
                                woman.screenresulthpv[infection] = "positive"
                                
                    


def self_screening_update(woman, data):
    """does the same as screening_update function but for self-testing kits
    """
    if woman.alive:
        if woman.screening_age <= woman.ageYears:
            if not woman.everscreen or woman.ageYears >= woman.lastscreenage + woman.screening_freq:

                # percentage potentially representing last medical screening
                if check_random(.95):  # 5% non-compliance with screenings
                    if len(woman.activeinfections) > 0:  # If has HPV infection
                        for infection in woman.activeinfections:

                            # false negative rate
                            if check_random(1-data.SELFTESTING.loc["Se", data.LAB]):
                                woman.selfscreenresulthpv[infection.Type] = "negative"  # False negative
                            else:
                                woman.selfscreenresulthpv[infection.Type] = "positive"  # True positive
                                infection.diagnosedself = True
                    else:  # If has no HPV
                        for infection in infectionlist:
                            if check_random(data.SELFTESTING.iloc[1,data.LAB]): 
                                woman.selfscreenresulthpv[infection] = "negative"  # true negatives
                            else:
                                woman.selfscreenresulthpv[infection] = "positive"  # false positive


def update_health(woman, infections, data):
    """
    If a woman has cancer, updates cancer state. If she does not, function updates CIN and HPV information
    :param woman: instance of woman class
    :param infections: list of HPV infections of interest
    :param data: instance of data class
    :return: updated information for woman
    """

    if woman.alive:
        if woman.cancer is None:
            CIN_update(woman, data)
            HPV_update(woman, data)
            HPV_newinfection(woman, infections, data)
        else:
            cancer_update(woman, data)


def run_1month(woman, infections, data):
    """
    run through all above functions
    :param woman: instance of woman class
    :param infections: list of possible HPV infections
    :param data: instance of data class
    :return: updated information for woman
    """

    if woman.alive:
        life_update(woman)
        HIV_update(woman, data)
        update_health(woman, infections, data)
        vaccination_update(woman, data)
        screening_update(woman, data)
        self_screening_update(woman, data)
        # if woman.ageMonths % 12 == 0:
            # woman.update_sex
        woman.age_step()
        woman.cycle_step()