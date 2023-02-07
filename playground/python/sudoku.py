import os
import time

board = [
    [7,8,8,4,0,0,1,2,0], # 5
    [6,0,0,0,7,5,0,0,9], # 4
    [0,0,0,6,0,1,0,7,8], # 4
    [0,0,7,0,4,0,2,6,0], # 4
    [0,0,1,0,5,0,9,3,0], # 4
    [9,0,4,0,6,0,0,0,5], # 4
    [0,7,0,3,0,0,0,1,2], # 4
    [1,2,0,0,0,7,4,0,0], # 4
    [0,4,9,2,0,6,0,0,7]  # 5
]

def print_board(bo, message=""):
    for i in range(len(bo)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - - - ")
        for j in range(len(bo[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")
            if j == 8:
                print(bo[i][j])
            else:
                print(str(bo[i][j]) + " ", end="")
    print(message)
    # time.sleep(0.5)
    os.system('clear')

def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, col
    return None

def valid(bo, num, pos):
    # Check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False
    # Check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False
    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3
    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if bo[i][j] == num and (i,j) != pos:
                return False

    return True

def solve(bo, assingments_till_now=[]):
    find = find_empty(bo)
    # All tiles filled
    if not find:
        return True
    else:
        row, col = find

    for i in range(1,10):
        if valid(bo, i, (row, col)):
            bo[row][col] = i
            print_board(bo, "found valid assignment for "+ str((row,col))+":"+ str(i))
            # add_line_to_veripb(f"1 xg[{row+1},{col+1}]_{i} >= 1 ;\n", "u")
            n = assingments_till_now+ [(row,col,i)]
            if solve(bo, n):
                return True
            bo[row][col] = 0
        # else:
            # add_line_to_veripb(f"1 ~xg[{row+1},{col+1}]_{i} >= 1 ;\n", "u")

    # All combinations didn't work, backtracking
    print_board(bo, "backtracking")
    # print(assingments_till_now)
    some_assignment_is_wrong = ""
    for idx, assignment in enumerate(assingments_till_now):
        row, col, i = assignment
        if idx == 0:
            some_assignment_is_wrong += f"1 ~xg[{assignment[0]+1},{assignment[1]+1}]_{assignment[2]} "
        else:            
            some_assignment_is_wrong += f"1 ~xg[{assignment[0]+1},{assignment[1]+1}]_{assignment[2]}  "

    some_assignment_is_wrong += f">= 1 ;\n"
    add_line_to_veripb(some_assignment_is_wrong, "u")
    return False


# creates file "sudoku.veripb"
def create_veripb(board):
    if os.path.exists("sudoku.veripb"):
        os.remove("sudoku.veripb")
    with open("sudoku.veripb", "w") as f:
        f.write("pseudo-Boolean proof version 1.0\n")
        f.write("f "+str(405+sum([sum([1 for x in row if x != 0]) for row in board]))+" 0\n")

# function that adds line to file "sudoku.veripb"
def add_line_to_veripb(line, action):
    with open("sudoku.veripb", "a") as f:
        f.write(action+" "+ line)

create_veripb(board)
solve(board)
