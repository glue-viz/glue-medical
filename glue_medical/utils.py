def flip(array, axis):
    # Backport of np.flip in Numpy 1.12
    indexer = [slice(None)] * array.ndim
    indexer[axis] = slice(None, None, -1)
    return array[tuple(indexer)]
