#assignment 1 (b)
import random
import matplotlib.pyplot as plt
import pandas as pd

#somewhat constant variables
target_preferences_sum = 0 #unrealisitic goal because it assumes every student gets their first choice. should still work towards it
mutation_rate = 0.02
generations = 200
population_size = 100
penalty_value = 1000
population = []
avg_fitness_list = []

#read in the data for the lecturers
lecturers_df = pd.read_excel("Supervisors.xlsx")
students_df = pd.read_excel("Student-choices.xlsx")

#make lists and dictionaries out of the dataframes for ease of use
lecturer_names = lecturers_df['Lecturer'].tolist() #get list of lecturer 'names'
capacities = lecturers_df['Capacity'].tolist() #get list of lecturer capacities
supervisor_capacity_dict = dict(zip(lecturer_names, capacities)) #create capacity dictionary from these lists
student_names = students_df['Student'].tolist()
student_preference_dict = students_df.to_dict()
#original_lecturer_names = lecturer_names.copy() #random.shuffle() alters the original list so i need to copy the original for later use
#original_student_names = student_names.copy() #same reason as above

# #print for debedugging
# print("Lecturer Names\n" +str(lecturer_names) + "\n")
# print("Capacities\n" + str(capacities) + "\n")
# print("Supervisor Capacities Dict:\n" + str(supervisor_capacity_dict) + "\n")
# print("Student Names\n" + str(student_names) + "\n")

#fitness function returns preferences sum
def find_fitness(student_assignments):
    found_fitness = 0

    #student_assignment is a dict with each student assigned to a lecturer
    for student in student_assignments:
        assigned_lecturer = student_assignments[student] #returns Supervisor_x
        stud_row_index = int(student.split("_")[1]) #get the row index from the student assignment sent in. i couldnt think of a better way to do this
        found_fitness += students_df.loc[stud_row_index-1, str(assigned_lecturer) + '_Rank'] #sum up all the preference values

    return found_fitness


#crossover function(parent 1, parent 2) WHERE both parents are student => lecturer mappings
def crossover(parent1, parent2):
    #choose crossover point
    crossover_point = random.choice(list(parent1.keys()))
    #print("Crossover point: " + str(crossover_point))
    #create first offspring
    offspring1 = {}
    for key in parent1:
        if key <= crossover_point:
            offspring1[key] = parent1[key]
        else:
            offspring1[key] = parent2[key]
    #create second offspring
    offspring2 = {}
    for key in parent2:
        if key <= crossover_point:
            offspring2[key] = parent2[key]
        else:
            offspring2[key] = parent1[key]

    offspring1 = sanatize_offspring(offspring1)
    offspring2 = sanatize_offspring(offspring2)

    return offspring1, offspring2

#function to make sure the offspring dooesnt break the capacities of the lecturers
def sanatize_offspring(offspring):
    frequencies = {}
    over_capacity = []
    under_capacity = []
    # loop through offspring
    # keep track of how many times a lecturer is assigned
    for mapping in offspring:
        if offspring[mapping] in frequencies:
            frequencies[offspring[mapping]] += 1
        else:
            frequencies[offspring[mapping]] = 1

    # loop through lecturer names
    # add them to two arrays, so you have one with overcapacity lecturers and one with undercapacity
    for lecturer in lecturer_names: #to get the lecturer names to act as the key
        if lecturer not in frequencies.keys(): #prevents a keyerror when a lecturer isnt assigned to anyone in the frequencies dict
            frequencies[lecturer] = 0
        if (frequencies[lecturer] > supervisor_capacity_dict[lecturer]):
            over_capacity.append(lecturer)
        if (frequencies[lecturer] < supervisor_capacity_dict[lecturer]):
            under_capacity.append(lecturer)

    # while there are over capacity supervisors
    while len(over_capacity) > 0:
        # pick a random one
        lecturer = random.choice(over_capacity)
        over_capacity.remove(lecturer)
        # find a student assigned to it
        student_to_reassign = None
        for student in offspring:
            if offspring[student] == lecturer:
                student_to_reassign = student
                break
        # reassign the student to a random under capacity lecturer
        new_lecturer = random.choice(under_capacity)
        offspring[student_to_reassign] = new_lecturer
        # update the frequencies
        frequencies[lecturer] -= 1
        frequencies[new_lecturer] += 1
        # check if the new lecturer is now at capacity
        if frequencies[new_lecturer] == supervisor_capacity_dict[new_lecturer]:
            under_capacity.remove(new_lecturer)
            #over_capacity.append(new_lecturer)

#print for bedugging
    # print("Frequencies: " + str(frequencies))
    # print("Lecturers over capacity: " + str(over_capacity))
    # print("Lecturers under capacity: " + str(under_capacity))

    return offspring


#INITIALIZING THE POPULATION
#population is random assignment of lecturers to students
for i in range(population_size):
    #loop through shuffled lecturers (so its random)
    student_dict = {}
    temp_students = student_names.copy()  #for the sake of removing students during the loop without altering the original thing

    #randomly shuffle the lecturer and student names for random assignment
    random.shuffle(lecturer_names)
    random.shuffle(temp_students)

    for lecturer in lecturer_names:
        #loop through the range of thier capacities (so capacity is never exceeded)(use the lecturer dict)
        for j in range(supervisor_capacity_dict[lecturer]):
            # print("Capacity of " + str(lecturer) + " = " + str(supervisor_capacity_dict[lecturer]))
            #randomly assign a student to the lecturer
            student_dict[temp_students[0]] = lecturer
            #remove that student from the students list (its just getting overridden
            temp_students.remove(temp_students[0])
    population.append(student_dict)


#######################################################################################################################

for generation in range(generations):
    #CALCULATE FITNESS OF POPULATION
    fitness = []
    #loop through population of student => lecturer mappings
    for mapping in population:
        fitness.append(find_fitness(mapping)) #send dict into the fitness function thats the
                                                 #fitness for that individual student. also adds to list of fitnesses
                                                 #population isnt changing per generation so it returns the same values
    avg_fitness = 0
    fitnesses = []

    #divide by lecturer names to give the avergage RANKED PREFERENCE per student
    #avg_fitness = ((sum(fitness) / len(fitness))/len(student_names)) / len(lecturer_names)
    avg_fitness = (sum(fitness) / len(fitness))/len(lecturer_names)
    #really good performance for now because theres no limits on how many students each can take on. so it should just keep going until everyone is organised
    for f in fitness:
        fitnesses.append((len(student_names))/len(lecturer_names))
    best_fitness = min(fitnesses)
    avg_fitness_list.append(avg_fitness)
    print("Generation: " + str(generation) + " Average fitness :" + str(avg_fitness) + " Best fitness: " + str(best_fitness))


    #SELECTION
    #create parents list
    # SELECTION
    parent_indices = []
    for index, fit in enumerate(fitness):
        parent_indices.append(index)

    parents = []
    for i in range(len(parent_indices)):
        parents.append(population[parent_indices[i]])

    #CROSSOVER AND SELECTION (part 2 electric boogaloo)
    offspring = []
    for i in range(population_size):
        #take two random parents from the parents array
        parent1 = parents[random.randint(0, len(parents) - 1)]
        parent2 = parents[random.randint(0, len(parents) - 1)]
        #send both parents to crossover function
        offspring1, offspring2 = crossover(parent1, parent2)
        offspring.append(offspring1)
        offspring.append(offspring2)
        # tournament selection to add a duplicate of the better offspring to the array
        if (find_fitness(offspring1) <= find_fitness(offspring2)):
            offspring.append(offspring1)
        else:
            offspring.append(offspring2)


    #MUTATION
    #loop through offspring and randomly mutate
    for offsprng in offspring:
        for mapping in offsprng:
            if random.random() < mutation_rate:
                temp_lecturers = lecturer_names.copy()
                temp_lecturers.remove(offsprng[mapping])
                offsprng[mapping] = random.choice(temp_lecturers)

    #EVALUATE OFFSPRING
    #take 100 (or whatever) best offspring
    fitness_scores = []
    for i in offspring:
        fitness_scores.append(find_fitness(i))
    # Zip the offspring and fitness scores together
    zipped = zip(fitness_scores, offspring)
    # Sort the zipped list based on the fitness scores
    sorted_zipped = sorted(zipped, key=lambda x: x[0], reverse=False)
    # Unzip the sorted list to get two separate lists: the offspring and fitness scores
    temp_population = []
    for i in range(len(sorted_zipped)):
        temp_population.append(sorted_zipped[i][1])
    sorted_zipped = temp_population

    # Take only the best offspring up until population size (no hardcoded number)
    offspring = sorted_zipped[:population_size]  # maybe taking too much of the best? working too well i think...

    #sorted by best fitness
    #integrate by setting population = offspring
    population = offspring

print("Best Mapping: " + str(offspring[0]))

#plot the results
plt.plot(avg_fitness_list)
plt.title("Average Fitness over Generations (Part b)")
plt.xlabel("Generation")
plt.ylabel("Average Fitness")
plt.show()

