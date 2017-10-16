import numpy as np
import fnmatch
import os

def grab_files_recursive(input_directory, regex='*'):

    output_list = []

    for root, subFolders, files in os.walk(input_directory):
        for file in files:
            if fnmatch.fnmatch(file, regex):
                output_list += [os.path.join(root, file)]

    return output_list

def flip(array, axis):
    # Backport of np.flip in Numpy 1.12
    indexer = [slice(None)] * array.ndim
    indexer[axis] = slice(None, None, -1)
    return array[tuple(indexer)]

def create_glue_affine(array, affine):

    # Switch first and last dimension in accordance with glue (numpy?) expectation.
    glue_affine = np.matmul(np.array(([0,0,1,0],[0,1,0,0],[1,0,0,0],[0,0,0,1])), affine)

    # Find primary dimension from the largest value of each column in the affine matrix
    cx, cy, cz = np.argmax(np.abs(glue_affine[0:3,0:3]), axis=0)

    # Transpose the array by these dimensions to match it to a [0, 1, 2] diagonal affine matrix
    array = np.transpose(array, (cx,cy,cz))

    # Transpose the affine matrix accordingly. There is likely a more direct method to do this.
    transpose_matrix = np.eye(4)
    for dim, i in enumerate([cx,cy,cz]):
        transpose_matrix[i,i] = 0
        transpose_matrix[dim, i] = 1
    glue_affine = np.matmul(glue_affine, transpose_matrix)

    # Switch left and right. I don't know the precise reason this is required in glue, but left-right
    # flipping with affine matrices is a frequent problem in viewing medical imaging.
    glue_affine = np.matmul(glue_affine, np.array(([1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,1])))

    # Find negative diagonal values, and make them positive by flipping the data array.
    # I am currently not sure how this works with skewed arrays with non-zero off-diagonal
    # values, and to what extent their signs should be flipped. However, those elements should
    # only matter for accurate pixel dimensions and axes, not array ordering.
    flip_matrix = np.eye(4)
    for i in xrange(3):
        if glue_affine[i,i] < 0:
            flip_matrix[i,i] = -1
            array = np.flip(array, i)
    glue_affine = np.matmul(glue_affine, flip_matrix)

    return array, glue_affine

def reverse_glue_affine(array, affine):

    # Get the original transpose.
    glue_affine = np.matmul(np.array(([0,0,1,0],[0,1,0,0],[1,0,0,0],[0,0,0,1])), affine)
    transpose = np.argmax(np.abs(glue_affine[0:3,0:3]), axis=0)

    # Get the tranposed and flipped matrix as usual..
    transpose_matrix = np.eye(4)
    for dim, i in enumerate(transpose):
        transpose_matrix[i,i] = 0
        transpose_matrix[dim, i] = 1
    glue_affine = np.matmul(glue_affine, transpose_matrix)
    glue_affine = np.matmul(glue_affine, np.array(([1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,1])))

    # Flip our data back through the except same process as previous.
    for i in xrange(3):
        if glue_affine[i,i] < 0:
            array = np.flip(array, i)

    # and transpose our data back using some magic inverse-transpose code from:
    # https://stackoverflow.com/questions/11649577/how-to-invert-a-permutation-array-in-numpy
    inverse_tranpose = np.empty(transpose.size, transpose.dtype)
    inverse_tranpose[transpose] = np.arange(transpose.size)
    array = np.transpose(array, inverse_tranpose)

    return array