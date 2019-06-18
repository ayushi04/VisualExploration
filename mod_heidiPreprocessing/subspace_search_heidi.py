from mod_heidi import heidi_classes 
import numpy as np
import collections
import operator


class SubspaceSearch_Heidi:

	def __init__(self):
		#self.heidiObj = heidi_classes.HeidiMatrix()
		self.classDistribution = [] #order of class Label is same as the one in Heidi image
		self.subspaceHeidi_map = {}
		self.sortedSubspaces = []
		self.freq_subspace = {} #{tuple:integer} number of 1's in non diagonal block of all subspaces 

	def initialize(self, classDistribution, subspaceHeidi_map):
		self.classDistribution = classDistribution
		#self.heidiObj.initialize(dataset)
		self.subspaceHeidi_map = subspaceHeidi_map
		self._setDiagonalBlocks_zero()
		self._sortSubspaces_interesting()
		
	def _setDiagonalBlocks_zero(self):
		#TODO: write code here to set diagonal blocks to zero

		for subspace in self.subspaceHeidi_map:
			prev=0
			for curr in self.classDistribution:
				for i in range(prev,prev+curr):
					for j in range(prev,prev+curr):
						self.subspaceHeidi_map[subspace][i][j]=0
				prev=curr+prev
	
	"""
	This method sorts all interesting subspaces identified using denseness of patterns
    in non diagonal blocks (HEIDI based algorithm)
    e.g.,
        self.freq_subspace = {tuple:count, ....}
    INPUT
    ------
    subspaceHeidi_map {tuple:np.array, tuple:np.array....} {(a,b):heidiMatrix, (a):heidiMatrix, ....}
    
	"""
	def _sortSubspaces_interesting(self):
		#TODO: write code here to sort subspaces based on interestingness
		self.freq_subspace = {} #frequency of all subspaces {tuple:integer}
		for subspace in self.subspaceHeidi_map:
			self.freq_subspace[subspace] = np.count_nonzero(self.subspaceHeidi_map[subspace])
		#for k,v in sorted(self.freq_subspace.items(), key=operator.itemgetter(1), reverse=True):
		#	print(k,v)

	def getTopAInterestingSubspace(self, A):
		#TODO: write code to return top A interesting subspaces
		filtered_subspaces = []
		c=0
		for k,v in sorted(self.freq_subspace.items(), key=operator.itemgetter(1), reverse=True):
			filtered_subspaces.append(k)
			c=c+1
			if(c==A):
				break
		return filtered_subspaces





	
