import numpy as np
from astropy.wcs import WCS
from glue.core.coordinates import Coordinates


class Coordinates4DMatrix(Coordinates):

    def __init__(self, matrix, axis_labels):

        # Other code to translate header into labels depending on file format.

        self.matrix = matrix
        self.matrix_invert = np.linalg.inv(matrix)
        self.axis_labels = axis_labels

    def axis_label(self, axis):
        return self.axis_labels[axis]

    def pixel2world(self, *args):
        return np.matmul(self.matrix, args + (np.zeros_like(args[0]),))[:-1]

    def world2pixel(self, *args):
        return np.matmul(self.matrix_invert, args + (np.zeros_like(args[0]),))[:-1]

    @property
    def wcs(self):
        # We provide a wcs property since this can then be used by glue
        # to display world coordinates. In this case, the transformation matrix
        # is in the same order as the WCS convention so we don't need to swap
        # anything.
        wcs = WCS(naxis=self.matrix.shape[0] - 1)
        wcs.wcs.cd = self.matrix[:-1, :-1]
        wcs.wcs.crpix = np.zeros(wcs.naxis)
        wcs.wcs.crval = self.matrix[:-1, -1]
        wcs.wcs.ctype = self.axis_labels[::-1]
        return wcs
