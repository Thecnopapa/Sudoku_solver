

import copy
from itertools import count
from shlex import join
from tracemalloc import start
from typing import KeysView
import numpy as numpy
import generator as gen
import os

def run():
    get_input([])

def get_input(plain):
    clear = os.system('cls')
    print("")
    print("")
    print("")
    print("Type the sudoku using 0 as empty:")
    print("(press enter freely)")
    print("")
    x = 1
    trio = []
    row = []
    puzzle = []
    for n in plain: 
        row.append(n)
        trio.append(n)
        if x%3 == 0:
            if x%9 == 0:
                print(trio,sep=' ', end="\n")
                puzzle.append(row)
                row = []
                if x%27 ==0:
                    print("---------------------------")
            else:
                print(trio,sep=' ', end= "") 
            trio = []
        if x==81:
            print(trio, sep='')
            unpack(puzzle)
            break
        x+=1
    print(trio, sep='')
    import_terminal(plain)


def import_terminal(plain):
    r = 1
    if len(plain) <= 81:
        inp = input("-->")
        for n in inp:
            try:
                plain.append(int(n))
            except:
                break
        get_input(plain)
    else:
        if r%3 == 0:
            print("   ---------")
        r += 1


def find_square(row,col):
    squ = 3*(row//3) + col//3     
    ind = 3*(row%3) + col%3
    return (squ, ind)

def find_coordinates(squ,ind):
    row = 3*(squ//3) + ind//3
    column = 3*(squ%3) + ind%3
    return (row, column)

def count_unks(sudoku):
    plain= []
    for i in sudoku:
        plain += i
    unknowns = plain.count(0)
    return unknowns


def display_one_sudoku(puzzle):
        square = 0
        print("---------------------")
        for r in puzzle:
            print (r[0:3], end="")
            print (r[3:6], end="")
            print (r[6:10])
            square += 1
            if (square % 3) == 0:
                print("---------------------")


def display_sudoku(puzzles):
    if len(puzzles) >1:
        for puzzle in puzzles:
            display_one_sudoku(puzzle)
    else:
        display_one_sudoku(puzzle)


def unpack(sudoku):
    rows = sudoku
    columns = []
    for row in range(9): 
        column = []
        for n in range(9): 
            column.append(rows[n][row])
        columns.append(column)
    #gen.display_one_sudoku(columns)
    squares = []
    for sq in range(9):
        sq_row = sq//3
        sq_col = sq%3
        square = []
        for row in range(3):  
            square+=(rows[sq_row*3 + row][(sq_col*3):(sq_col*3+3)])
        squares.append(square)
        solving = [rows,columns,squares]
    global simulations 
    simulations = [solving]
    cycle_unk(solving)


def replace(row, column, solving, number):
        solving[0][row][column] = number
        solving[1][column][row] = number
        solving[2][find_square(row,column)[0]][find_square(row,column)[1]] = number
        print("Number ", number, " at row:", row, " col:", column," squ:", find_square(row,column))
        return solving


def cycle_unk(solving):
    #print("Searching...")
    unks = count_unks(solving[0])
    global starting_unks 
    starting_unks= unks
    global starting_seq 
    global total_iterations 
    global total_sims
    total_sims = 0
    total_iterations = 0
    starting_seq= solving[0]
    change = False
    done = 0
    iterations = 1
    while unks >= 1:
        print("Iteration: ",iterations, " Unknowns: ", unks)
        r=0
        for row in solving[0]:
            c = 0
            for n in row:
                if n==0:
                    #print("found (", r, ",", c,")")
                    #reset_terminal(r, c, solving, iterations,unks)
                    solving, change = check_options(r,c,solving)
                    if change == True:
                        done +=1
                    
                c+=1
            r+=1
        
        unks = count_unks(solving[0])
        if unks == 0:
            finished(10, 10, solving, iterations)
            #print("Solved!  (", iterations," iterations requiered)")
            #exit()

        if done == 0:
            #stuck(10, 10, solving, iterations,starting_unks)
            print ("No more found numbers :(")
            print (unks, " unknowns left")
            print ("Iterations: ", iterations)
            print (" -------------------------------")
            print("")
            print("")
            display_one_sudoku(solving[0])
            print("")
            print("stuck")
            print(starting_seq)
            for i in starting_seq:
                for n in i:
                    print(n, end="")
            print("")
            if len(simulations) ==1:
                print("Switching to simulation...")
                start_simulating(0)
                print("WTF.. I give up")
                stuck(10, 10, solving, iterations,starting_unks)
        iterations += 1
        total_iterations = total_iterations + 1
        done = 0


def check_options(row, column,solving):
    global total_iterations
    options = list(set(range(1,10)))
    square = find_square(row, column)[0]
    for i in solving[0][row]:
        if i in options:
            options.remove(i)
    for i in solving[1][column]:
        if i in options:
            options.remove(i)
    for i in solving[2][square]:
        if i in options:
            options.remove(i)
    if len(options) == 1:
        solving = replace(row, column, solving, options[0])
        change = True
    else:
        if len(options) >1:
            for p in options:
                change = check_adv(row, column,solving, options)
                if change:
                    break
        else:
            change = False
    total_iterations += 1
    return solving, change


def check_adv(row, column, solving, options):
    for number in options:
        nos = 0
        # check number in row:
        x = 0
        pos = []
        for n in solving[0][row]:
            #print("z:", z, " x:",x)
            if n ==0 and x!= column:
                for p in check_alt(row, x, solving):
                    pos.append(p)
            x+=1
        check_row = True    
        for p in pos:
            if p == number:
                check_row = False
                nos += 1
        # check number in col:
        y = 0
        pos = []
        for n in solving[1][column]:   
            if n ==0 and y!= row:
                for p in check_alt(y,column, solving):
                    pos.append(p)
            y+=1
        check_col = True    
        for p in pos:
            if p == number:
                check_col = False
                nos += 1
        # check number in square
        squ = find_square(row, column)
        z = 0
        pos = []
        for n in solving[2][squ[0]]:   
            if n ==0 and z!= squ[1]:
                cords = find_coordinates(squ[0], z)
                #print("(",cords[0],",",z,")")
                for p in check_alt(cords[0],cords[1], solving):
                    pos.append(p)
            z+=1           
        check_squ = True 
        for p in pos:
            if p == number:
                check_squ = False
                nos += 1
        if check_col or check_row or check_squ:
            solving = replace(row,column,solving,number)
            return True
    return False


def check_alt(y, x, solving):
    po = list(set(range(1,10)))
    square = find_square(y, x)[0]
    for i in solving[0][y]:
        if i in po:
            po.remove(i)
    for i in solving[1][x]:
        if i in po:
            po.remove(i)
    for i in solving[2][square]:
        if i in po:
            po.remove(i)
    return po      


def stuck(row, column, solving,iteration, unks):
    clear = os.system('cls')
    print("")
    print("")
    print("")
    print("  Stuck!")
    print("  After" ,iteration, "iterations")
    print(" ",count_unks(solving[0]),"/",unks,"missing unknowns")
    print_sudoku(row, column, solving,iteration, unks)
    print("")
    print("")
    for row in solving[0]:
        for n in row:
            print(n, end="")
    print("")
    exit()
 

def finished(row, column, solving,iteration):
    clear = os.system('cls')
    print("")
    print("")
    print("")
    print("  Solved!")
    print("  In" ,iteration, "iterations")
    print(" ",starting_unks,"Initial unknowns")
    print_sudoku(row, column, solving,iteration, starting_unks)
    print("")
    print("")
    exit()


def reset_terminal(row, column, solving,iteration, unks, sim,cycle):
    clear = os.system('cls')
    print("")
    print("")
    print("")
    print("  Solving", (iteration)*".")
    print("  Cycle:",cycle)
    print(" ",unks,"Unknowns left")
    print("  Simulation level:",sim, " Total: ", total_sims)
    print("  Total iterations:", total_iterations)
    print_sudoku(row, column, solving,iteration, unks)


def print_sudoku(row, column, solving,iteration, unks):
    y = 0
    for row in solving[0]:
        x = 0
        prt = []
        for n in row:
            if x%3 == 0:
                if x==column and y== row:
                    prt.append(" |[")
                elif x==column+1 and y== row:
                    prt.append("]| ")
                else:
                    prt.append(" | ")
            else:
                if x==column and y== row:
                    prt.append(" [")
                elif x==column+1 and y== row:
                    prt.append("] ")
                else:
                    prt.append("  ")

            if x==column and y==row:
                prt.append("X")
            elif n ==0:
                prt.append(" ")
            else:
                prt.append(str(n))
            x+=1
        if y%3 == 0:
            print(" -------------------------------")
        y+=1
        prt.append(" | ")
        print("".join(prt))
    print(" -------------------------------")
 

def find_simulation(row, column,solving):
    global total_iterations
    total_iterations+=1
    options = list(set(range(1,10)))
    square = find_square(row, column)[0]
    for i in solving[0][row]:
        if i in options:
            options.remove(i)
    for i in solving[1][column]:
        if i in options:
            options.remove(i)
    for i in solving[2][square]:
        if i in options:
            options.remove(i)
    return options


def start_simulating(sim):
    cycle = 0
    simulations[sim] = cycle_simulation(simulations[sim],sim,cycle) # solve previous simulation
    global total_sims
    total_sims +=1
    # simulations[sim] has original/replaced from previous sim
    # solving has stuck version

    unks = count_unks(simulations[sim][0])
    if unks == 1: # if only one unk left no point simulating
        return # therefore go back
    
    while cycle <=1:
        r=0 #row
        for row in simulations[sim][0]: # check for 0s in stuck version
            c = 0 #column
            for n in row:
                if n==0: # found a 0
                    options = find_simulation(r,c,simulations[sim]) # when a 0 is found check for posssible options
                    while len(options) > 0: # if options are found replace the 0 by the first option
                        rep = copy.deepcopy(simulations)
                        rep = rep[sim]
                        rep[0][r][c] = options[0]
                        rep[1][c][r] = options[0]
                        rep[2][find_square(r,c)[0]][find_square(r,c)[1]] = options[0]
                        if cycle == 0:
                            cycle_simulation(rep,sim, cycle)
                        else:
                            simulations.append(rep) #make replacement and save as sim+1 in simulations
                            start_simulating(sim+1) #start all over with sim+1 using replaced version
                            del simulations[sim+1]
                        options.remove(options[0])
                        

                c+=1
            r+=1
        cycle+=1
    return   


def cycle_simulation(solving,sim,cycle):
    change = False
    done = 0
    iterations = 1
    unks = count_unks(solving[0])
    while unks >= 1:
        r=0
        for row in solving[0]:
            c = 0
            for n in row:
                if n==0:
                    solving, change = check_options(r,c,solving)
                    if change == True:
                        done +=1
                        reset_terminal(r,c,solving,iterations,unks,sim,cycle)    
                c+=1
            r+=1
        unks = count_unks(solving[0])
        if unks == 0:
            finished(10, 10, solving, iterations)
        if done == 0:
            return solving          
        iterations += 1
        done = 0



run()    
