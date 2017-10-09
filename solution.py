assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]



"""

Building data structure.
0. rows & cols - forming 9x9 matrix to form sudoku board
1. boxes - all square positions
2. unitlists- forming all possible units. no numbers can repeat
   in a unit(diagonal unit,row unit, column unit square unit).
3. units- all unit associated with individual square(eg A1)
3. peers - a single square lies in many unit. all square within these
   units form peer of this square

"""

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
diagonal_1=[x+y for x,y in zip(rows,cols)]
diagonal_2=[x+y for x,y in zip(rows,cols[::-1])]
diagonal_units=[diagonal_1,diagonal_2]
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units+diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)



def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values



def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    #finding all naked twins in a unit and removing these numbers from its units 
    for box in boxes:
        for unit in units[box]:
            for unit_box in unit:
                if unit_box!=box:
                    #if two different box values match within a unit then they are naked twins
                    if values[box]==values[unit_box]:
                        if len(values[box])==2:
                            #removing naked twins number from unit
                            remove_naked_twin(values,unit,box) 

    return values

def remove_naked_twin(values,unit,box):
    """naked twin found in passed unit
    this function remove naked twin values from other square of given unit
    """
    for unit_box in unit:
        #remove numbers from squares other than naked twins square 
        if values[box]!=values[unit_box]:
            for value in values[box]:
                if value in values[unit_box]:
                    to_assign=values[unit_box].replace(value,"")
                    values=assign_value(values,unit_box,to_assign)
    return values                       

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))
  

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
        
    """
    
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return
   

def eliminate(values):
    """
    eliminate the value of a solved sudoku square from all its peer as
    peers can not have that number.

    Args:
        values(dict): The sudoku in dictionary form
        
    Returns:
        the values dictionary with the solved sudoku square number eliminated from peers.

    """
    for key,value in values.items():
        if len(value)==1:
            
            for peer in peers[key]:
                to_assign=values[peer].replace(value,"")
                values=assign_value(values,peer,to_assign)
                
    return values
    

def only_choice(values):
    
    """
    to find only choice we
    find frequency of each possible values in each square of a unit
    e.g for squares {'A1':'123','A2':'24':'A3':'324'} frequencies
    of numbers are {'1':['A1'],'2':['A1','A2','A3'],'3':['A1','A3'],'4':['A2','A3']} 
    and assigning the value with unit frequency (1 in this case) to that square(A1 in this case) in which it lies

    Args:
        values(dict): The sudoku in dictionary form
        
    Returns:
        the values dictionary with the only choice assigned to its square.
    """
    from collections import defaultdict
    for unit in unitlist:
        d = defaultdict(list)
        
        #finding frequency of each value of a box in unit
        for box in unit:
            for n in range(0,len(values[box])):
                (d[values[box][n]].append(box))

        #assigning value if requency of a number is 1
        for number in d:
            if len(d[number])==1:
                box =''.join(d[number])
                values=assign_value(values,box,number)
    return values


def reduce_puzzle(values):

    """
    reduce the puzzle by iteratively applying elimination, naked_twins, only_choice
    strategy. If further iteration does not imporove the result then return the latest
    value dictionary

    Args:
        values(dict): The sudoku in dictionary form
        
    Returns:
        the values dictionary when sudoku can not further be reduced or false if sudoku failed to solve.
        
    """
    
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values=naked_twins(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values
    

def search(values):

    """
    to solve sudoku with search techniques we try to find square with least number
    of possible values for a square. Do the depth first search to solve sudoku.

    Args:
        values(dict): The sudoku in dictionary form
        
    Returns:
        the values dictionary for solved sudoku or false if sudoku failed to solve.
        
    """
    
    values=reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!

    #finding the un-solved squares with minimum number of possible values
    min_value=10 #starting with maximum value
    min_key=''
    for key,value in values.items():
        if len(value) !=1:
            if len(value) <min_value:
                min_value=len(value)
                min_key=key
    
    #using depth first search to solve sudoku
    for value in values[min_key]:
        new_values=values.copy()
        new_values[min_key]=value
        attempt=search(new_values)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """

    values=grid_values(grid)
    values=reduce_puzzle(values)    
    values=search(values)
    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))
  

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
