import numpy as np
import itertools
    
class Piece: #Class to describe the shape of each piece in the puzzle.
    def __init__(self, top_point, top_slab,bot_point,bot_slab): #Args: arrays. 'top' and 'bot' are arbitrary assignments to each half of a piece. point refers to vector of 'pointing' block, slab refers to vector orthogonal to 'slab' of each respective half.
        self.tp=top_point 
        self.ts=top_slab
        self.bp=bot_point
        self.bs=bot_slab

class Orientation: #Class to describe orientation of a piece using Coordinates.
    def __init__(self, point, slab): #Args: numpy arrays.
        self.point = point #Vector of 'pointing' block
        self.slab = slab #Vector orthogonal to 'slab' (pointing 'inwards')
    
def Print_Orientation(given_ori):
    print('Point: ' + str(given_ori.point) + ', Slab: ' + str(given_ori.slab))

def Find_Required_Orientation(given_ori): #method to return orientation of the piece needed to fit with a given orientation. Args: Orientation.
    return Orientation(np.cross(given_ori.point,given_ori.slab),-given_ori.slab)

def Find_Rotation_Matrix(i_point,i_slab,ori): #input the initial and end orientations. Returns rotation matrix to get from intial to end orientation.
    R = np.matmul(np.transpose(i_point),ori.point) + np.matmul(np.transpose(i_slab),ori.slab) #finds two of the rows of the rotation matrix
    for i in range(3): #locate the zero row
        if i_point[0][i] == i_slab[0][i]:
            R[i] = (np.cross(R[(i+1)%3],R[(i+2)%3])) #sets the zero row of the matrix (i.e makes the row orthogonal to the other two)
            R[i] = np.linalg.det(R)*R[i] #swaps sign of row i if determinant is -1 
    return R

def Find_New_Pos(given_pos,rotation_matrix,toporbot): #returns new position 
    if toporbot == 0:
        new_pos = given_pos + np.matmul(np.array([[0,0,-1]]),rotation_matrix)
    elif toporbot == 1:
        new_pos = given_pos + np.matmul(np.array([[0,0,1]]),rotation_matrix)
    else:
        return None
    return new_pos

def Find_New_Ori(rotation_matrix,attaching_piece,toporbot): #returns new orientation
    if toporbot == 0:
        new_ori = Orientation(np.matmul(np.array(attaching_piece.bp),rotation_matrix),np.matmul(np.array(attaching_piece.bs),rotation_matrix))
    elif toporbot == 1:
        new_ori = Orientation(np.matmul(np.array(attaching_piece.tp),rotation_matrix),np.matmul(np.array(attaching_piece.ts),rotation_matrix))
    else:
        return None
    return new_ori

def Attach_Piece(given_pos,given_ori,attaching_piece,toporbot): #returns updated position and orientation
    needed_ori = Find_Required_Orientation(given_ori)
    if toporbot == 0:
        rotation_matrix = Find_Rotation_Matrix(attaching_piece.tp,attaching_piece.ts,needed_ori)
    elif toporbot == 1:
        rotation_matrix = Find_Rotation_Matrix(attaching_piece.bp,attaching_piece.bs,needed_ori)
    else:
        print("Invalid toporbot value. Please set as 0 or 1")
    return [Find_New_Pos(given_pos,rotation_matrix,toporbot),Find_New_Ori(rotation_matrix,attaching_piece,toporbot)]

#Setting initial conditions:
start_point = np.array([[1,0,0]])
start_slab = np.array([[0,-1,0]])

start_pos = np.array([[1,0,0]])
start_ori = Orientation(start_point, start_slab)

current_pos = start_pos
current_ori = start_ori

#Defining the 8 pieces in the puzzle:
piece0 = Piece([[1,0,0]],[[0,0,1]],[[0,0,-1]],[[0,1,0]])
piece1 = Piece([[1,0,0]],[[0,0,1]],[[0,0,-1]],[[-1,0,0]])
piece2 = Piece([[1,0,0]],[[0,0,1]],[[0,0,1]],[[0,-1,0]])
piece3 = Piece([[1,0,0]],[[0,0,1]],[[0,0,1]],[[1,0,0]])
piece4 = Piece([[1,0,0]],[[0,0,1]],[[0,-1,0]],[[-1,0,0]])
piece5 = Piece([[1,0,0]],[[0,0,1]],[[-1,0,0]],[[0,1,0]])
piece6 = Piece([[0,0,1]],[[1,0,0]],[[0,0,-1]],[[0,-1,0]])
piece7 = Piece([[0,0,1]],[[1,0,0]],[[1,0,0]],[[0,1,0]])

in_play = [piece0,piece1,piece2,piece3,piece4,piece5,piece6]

def Solve_Puzzle(set_of_pieces,position,orientation):
    start_position = position
    start_orientation = orientation
    counter = 0
    for j in range(128): #runs through every flipping of each piece within each permutation.
        k = format(j,'b').zfill(7)
        for perm in itertools.permutations([0,1,2,3,4,5,6]): #runs through every permutaion of pieces with flipping determined by k.
            for i in range(7):
                if int(str(k)[perm.index(6)]) == 1: #ignore the perm if piece 6 is flipped as piece 6 is symmetric, so otherwise this would double count solutions.
                    break
                conditions = Attach_Piece(position,orientation,in_play[perm[i]],int(str(k)[i]))
                position = conditions[0]
                orientation = conditions[1]
            if (position == [[0,0,0]]).all() and (orientation.point == [[1,0,0]]).all() and (orientation.slab == [[0,0,1]]).all(): #checks if piecing the puzzle together this way ends up with the end at [0,0,0], and in the right orientation.
                if (perm.index(4) - perm.index(5) - int(str(k)[perm.index(4)]) + int(str(k)[perm.index(5)]) == 0) or (perm.index(2) - perm.index(3) - int(str(k)[perm.index(2)]) + int(str(k)[perm.index(3)]) == 0): #ensures pieces aren't stuck together in ways which aren't physically possible
                    break
                position = start_position
                orientation = start_orientation
                positions_visited = [start_position]
                overlap = False
                for i in range(7): #re-piece the puzzle together to check for overlaps.
                    conditions = Attach_Piece(position,orientation,in_play[perm[i]],int(str(k)[i]))
                    position = conditions[0]
                    orientation = conditions[1]
                    for visited in positions_visited:
                        if (position == visited).all():
                            overlap = True
                    if (i == 6 and overlap == False): #if no overlap after piecing puzzle together we have a solution!
                        counter += 1
                        print('Solution ' + str(counter) + ':')
                        print(perm)
                        k_in_list = []
                        for l in range(7):
                            k_in_list.append(int(str(k)[l]))
                        print(k_in_list)
                    elif overlap == True:
                        break
                    else:
                        positions_visited.append(position)
            position = start_position
            orientation = start_orientation

Solve_Puzzle(in_play,start_pos,start_ori)