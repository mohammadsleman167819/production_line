from django.shortcuts import render
from django.http import HttpResponse
from numpy.random import randint
from numpy.random import random
import os

#global vars
adjList = {}
adjListr = {}
vals = {}
n=0 
m=0 
shifts=0
genetic_pool=[]
pool_size = 1000
generation = []
times_sum = 0 
answer = []
ans = 10000000
fitness_map = [int(-1)] * (10000010)
best_fitness_map = [int(-1)] * (10000010)

all_results_file_path = os.path.join('Media', 'all_results_steps.txt')
best_results_file_path = os.path.join('Media', 'optimal_results_steps.txt')
        

def reset_globals():
    adjList.clear()
    adjListr.clear()
    vals.clear()
    genetic_pool.clear()
    generation.clear()
    global times_sum,ans,fitness_map,best_fitness_map
    ans = 10000000
    times_sum = 0
    answer.clear()
    fitness_map = [int(-1)] * (10000010)
    best_fitness_map = [int(-1)] * (10000010)




#generting 1000 person to choose from them the first generation later
# visited help me keep track of the visited nodes
# avabs help me keep track of all the possible nodes I can visit at the time
# person is a list I keep the solution I am constructing in it
def generate_gens_pool(visited,avabs,person):
    
    #if I generated 1000 already then no need for more
    if(len(genetic_pool)==pool_size):
        return
    
    #if the length of the person equal to the number of node (+1 because of the helping node) then I've reached a correct solution and I can add it to genpool
    if(len(person)==n+1):
        genetic_pool.append(person)


    else:
        for node in avabs:
            #if node have been visited number of times equal to its number of parents then I can add it to the solution 
            #if not move on
            if(visited[node]<len(adjListr[node])):
               continue
            cur_avabs = avabs.copy()
            cur_vis = visited.copy()

            for child in adjList[node]:
                #visit all my children                 
                cur_vis[child]+=int(1)
                #if a child not in avabs I add it because I can reach it now
                if(child not in avabs):
                    cur_avabs.append(child)
            #remove node from avabs because I can't add it to the solution more than once
            cur_avabs.remove(node)
            cur_person = person.copy()
            cur_person.append(node)
            #recuersivly try reaching all the possible solution from this state
            generate_gens_pool(cur_vis,cur_avabs,cur_person)


#function responsible of generating the first generation
# sz : number of persons in one generation
def generate_generation(sz):
    

    visited =[int(0)] *(n+2)
    person = []
    avabs = [0]
    visited[0]=0
    generate_gens_pool(visited,avabs,person)
    
    #after generating the gens pool we will randomly choose the first generation
    chosen = []
    for i in range (sz):
        
        zx = 0 
        #repeat to get more random choosing 
        while(zx < 10):
            index = randint(0,len(genetic_pool))
            zx=zx+1
        
        chosen.append(index)
        #remove the additional zero in the beggining of each person
        if(genetic_pool[index][0]==0):
            genetic_pool[index].pop(0)

        generation.append(genetic_pool[index])

#this function is used to write a sol in the required format to the file
# person : the solution
# File : path to the file towrite on
# max_shift_time : the maximum time of one shift (used to devide the solution into shifts)
def write_sol(person,File,max_shift_time):
    global shifts
    with open(File,mode='a') as file:
        cur_sum = 0
        tot_difs = 0
        max_time = 0
        min_time = 10000000
        AVGval = times_sum/shifts
        file.write("[")
        for i in person:
            if((cur_sum+vals[i])>max_shift_time):
                tot_difs +=abs(cur_sum - AVGval)
                max_time = max(max_time,cur_sum)
                min_time = min(min_time , cur_sum)
                L = ["] Total Time = (" , str(cur_sum) , "), dif = " , str(round(abs(cur_sum - AVGval),3)),"\n["]
                file.writelines(L)
                cur_sum=0    
            
            file.write(str(i))
            file.write(",")
            cur_sum+=vals[i]
        
        tot_difs+=abs(cur_sum - AVGval)
        max_time = max(max_time,cur_sum)
        min_time = min(min_time , cur_sum)
        
        L1 = ["] Total Time = (" , str(cur_sum) , "), dif = ",str(round(abs(cur_sum - AVGval),3))]
        L2 = ["\n Total Time = ",str(times_sum),"\n Total Time/steps = ", str(round(AVGval,3))," \n Total differences = "]
        L3 = [str(round(tot_difs,3)),"\n Average differences = ",str(round(tot_difs/shifts,3))]
        L4 = ["\n Max Time = ",str(round(max_time,3)) , "\n Min Time = ", str(round(min_time,3))]
        file.writelines(L1)
        file.writelines(L2)
        file.writelines(L3)
        file.writelines(L4)
        file.write("\n----------------------------------------\n")
        file.close()

'''
 to check weather it's possible to have val as the maximum time per shift
 iterate throw solution and maintain the current_sum of times of the tasks done in the current shift
 if csum reaches maximum start new shift and add 1 to the total shifts used
 if used shifts are greater than the shifts we have then val don't provide a valid distrbution  
'''
def check(val,person):
    csum = 0
    cur_sh = 1  
    for i in person:
        if(vals[i]>val):
            return False
        if((csum+vals[i])>val):
            csum=0
            cur_sh+=int(1)
        csum+=vals[i]
    
    if (cur_sh>shifts):
        return False
    else:
        return True

'''
 finding the best ditrubution of tasks over shifts to get minimum avg_dif will be time consuming
 so we calculate a relative paramter which is minimizing the maximum total time among shifts
 we use binary search to search for this value
 and use the function check to find if it's possible to achive this value
'''
def fitness(person):

    #binary search for the value   
    left = int(1)
    right = int(times_sum)
    ans = int(100000000) 
    while(left<=right):
        mid = int((left+right)/int(2))
        if(check(mid,person)==True):
            if(ans>mid):
                ans=mid
            right = (mid-1)
        else:
            left = (mid+1)
    
    global shifts

    #calculating the corresponding avg_dif
    cur_sum = 0
    tot_difs = 0
    AVGval = times_sum/shifts
    for i in person:
        if((cur_sum+vals[i])>ans):
            tot_difs +=abs(cur_sum - AVGval)
            cur_sum=0    
        cur_sum+=vals[i]
    tot_difs+=abs(cur_sum - AVGval)

    #use hashing to avoid adding the same solution to file more than once
    this_hash = hash(person,ans)
    if(fitness_map[this_hash]==-1):
        write_sol(person,all_results_file_path,ans)
        fitness_map[this_hash] = 1
    
    #return two values the minimum_maximum(ans) and the avg_dif
    return [round(tot_difs/shifts,3),ans]


#apply the crossover on two parents to generate two new children
def crossover(parent1,parent2):

    #randomly choose an index to make the crossover
    point = randint(0,len(parent1)-2)
    child1=[]
    child2=[]

    #copy the same tasks before point
    for i in range(point+1):
        child1.append(parent1[i])
        child2.append(parent2[i])
    
    # to maintain that the solution is correct and maintain applying the prerequests and not dublicating tasks
    # we iterate over both parents and each task not appering in the other child append to it
    # since both parents are correct solutions then the children will be
    
    for i in range(len(parent1)):
        if(parent2[i] not in child1):
            child1.append(parent2[i])
        if(parent1[i] not in child2):
            child2.append(parent1[i])
    return[child1,child2]

'''
 hash a solution to be able to track it using the value without having to store all of it
 use max shift time to add numbers when shifts end to differ solutions 
 with same order of tasks but different ditrubution over shifts
'''
def hash(person,max_shift_time):
    Base1  = int(29)
    Mod1 = int(999983)
    hash_value = int(person[0])
    cur_sum = vals[person[0]]
    for i in range(1,len(person)):
        if((cur_sum+vals[person[i]])>max_shift_time):
            hash_value = int((hash_value*Base1+i)%Mod1)
            cur_sum=0    
        cur_sum+=vals[person[i]]
        hash_value = int((hash_value*Base1+person[i])%Mod1)
    return hash_value

# to apply the mutation randomly choose a task and insert it right after its last prerequest appear
def mutation(child):
    #randomly choose index
    chosen = randint(2,n)
    #copy all chosen task prerequest's to list(pre)
    pre = adjListr[chosen].copy()
    
    insertion=0
    #iterate throw children and remove prerequests from 'pre' when appears 
    for i in range(len(child)):
        if(child[i] in pre):
            pre.remove(child[i])
        #if you removed all prerequest then insert the task in this index
        if(len(pre)==0):
            insertion=i+1
            break
    #delete the task from children
    child.remove(chosen)
    #insert it in the new index
    child.insert(insertion,chosen)


def nxtgen():

    global generation,ans,answer,shifts 
    
    rollete = []
    fitnesses=[]
    sum = 0
    for i in range(len(generation)):
        parent_fitness = fitness(generation[i])
        
        #maintain the best solution among generations 
        if(parent_fitness[0] < ans):
            ans  = parent_fitness[0]
            answer = generation[i].copy()
            minmax = parent_fitness[1]
            #if found better solution then erase everything in the file of optimal solutions
            with open(best_results_file_path,mode='w') as f:
                f.close()
            write_sol(generation[i],best_results_file_path,minmax)
            #use hashing and list to keep track of the solutions already addet to file
            my_hash = hash(generation[i],minmax)
            best_fitness_map[my_hash] = 1
            
        if(parent_fitness[0] == ans):
            #if found another optimal solution add it to the file
            my_hash = hash(generation[i],parent_fitness[1])
            if(best_fitness_map[my_hash] == -1):
                best_fitness_map[my_hash] = 1
                write_sol(generation[i],best_results_file_path,parent_fitness[1])
        
        #keep the fitness of its solution in list(fitnesses) and the sum of them in 'sum' 
        sum+=parent_fitness[0]
        fitnesses.append(parent_fitness[0])
    
    #make the rollete list values by giving each solution chance equal to its fitness divided by sum which all add up to 1
    rollete.append(round(fitnesses[0]/sum,3))
    for i in range(1,len(fitnesses)):
        cur = fitnesses[i]/sum
        rollete.append(round(rollete[-1]+cur,3))

    #choose n/2 parents from current generation to make next one
    next_gen = []
    chosen_parents = []
    for i in range(int(len(generation)/2)+1):
        #choose random number < 1
        rollet_pick = random()
        pop = 0
        #search in the rollete list to the range that rollet_pick fell into to add the corresponding solution(person)  
        for j in range(len(rollete)):
            if(rollet_pick <= rollete[j]):
                chosen_parents .append( generation[j].copy())
                pop = 1  
                break
        if (pop==0):
            chosen_parents.append(generation[-1].copy())
    
    #after choosing n/2 parents make the new generation by crossover each consicutive parents
    for i in range(len(chosen_parents)-1):
        
        #each crossover gives back two children
        children = crossover(chosen_parents[i],chosen_parents[i+1])
        
        #picking random number smaller than 1 repersent the chanse of mutation happening
        mutation_chance = random()
        if(mutation_chance<=0.2):
            mutation(children[0])
        
        #repeat for the second child
        mutation_chance = random()
        if(mutation_chance<=0.2):
            mutation(children[1])
        
        #add the resulted children to the new generation
        next_gen.append(children[0])
        next_gen.append(children[1])
    
    #in case generation have odd number of person
    if(len(next_gen)<len(generation)):
        next_gen.append(chosen_parents[-1])
    generation.clear()
    #the new generation became the generation for next time
    generation=next_gen.copy()

#driver function to make new generations 
def driver(number_of_generations,generation_size):
    generate_generation(generation_size)
    for i  in range (number_of_generations):
        nxtgen()


#function to take input from files
def getInput(valsfile,linksfile):

    # Declare global variables that will be used later
    global n ,m,times_sum

    # Read values from the first file and store the time each operation
    with valsfile.open() as f:
        contents = f.read().split()
        f.close()
    cursor = 0 
    n = int(len(contents))
    for i in range(1,n+1):
        line = contents[cursor].decode('utf-8')
        ints = line.split(",")
        node = int(ints[0])
        vals[node] = int(ints[1])
        times_sum += vals[node]
        cursor+=1
    
    
    # Read values from the first file and store links between nodes
    # adjlist[x] contain all the tasks directly followed by x
    # adjlistr[x] contain all the tasks need to be done before being able to do x
    
    with linksfile.open() as f:
        contents = f.read().split()
        f.close()

    m = int(len(contents))

    for i in range(0,n+1):
        adjList[i]=[]
        adjListr[i]=[]

    cursor = 0
    for i in range(0,m):
        line = contents[cursor].decode('utf-8')
        ints = line.split(",")
        x = int(ints[0])
        cursor+=1
        y = int(ints[1])
        adjList[x].append(y)
        adjListr[y].append(x)
    
    #linking all possible starting tasks to helper node 0 and start searching from it 
    for i in range(1,n+1):
        if len(adjListr[i]) == 0:
            adjListr[i].append(0)
            adjList[0].append(i)


#the function that get values from the form
def index(request):
    if request.method == 'POST':
        tasks_file = request.FILES['tasks']
        tasks_links_file = request.FILES['tasks_links']
        global shifts 
        shifts= int(request.POST.get('shifts'))
        number_of_generations = request.POST.get('no_gen')
        generation_size = request.POST.get('gen_size')
        open(all_results_file_path,mode='w')
        reset_globals()
    
        
        getInput(tasks_file,tasks_links_file)
        
        driver(int(number_of_generations),int(generation_size))

    return render(request,'pages/index.html',{})


#download the output files when asked
def download_files(request):
        
    # Create an HTTP response that downloads the file
    response = HttpResponse(open(all_results_file_path, 'r'), content_type='text/plain')
    response['Content-Disposition'] = "attachment; filename =%s" %"all_results_steps.txt"
    open(all_results_file_path,mode='w')
    return response


def download_files2(request):
    # Create an HTTP response that downloads the file
    response = HttpResponse(open(best_results_file_path, 'r'), content_type='text/plain')
    response['Content-Disposition'] = "attachment; filename =%s" %"optimal_results_steps.txt"
    open(best_results_file_path,mode='w')
    return response
