import numpy as np

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



