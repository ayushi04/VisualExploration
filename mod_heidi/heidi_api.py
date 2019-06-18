from flask import request, render_template, Blueprint, json, redirect, url_for, flash, session

from mod_heidiPreprocessing import assign_color, order_points, subspace_filter
from mod_heidi import heidi_classes
import _pickle as cPickle
import models


class HeidiParam:

	def __init__(self):
		self.datasetName=''
		self.allDims = ''
		self.orderDims = ''
		self.otherDims = ''
		self.allSubspaces = ''
		self.filteredSubspaces = ''
		self.filteredSubspaces_colormap = ''

"""
This method computes Heidi matrices for each individual subspace
INPUT:
-----
dataset : DataFrame representing the input dataset with no id and classLabel column
datasetName : dataset name

OUTPUT:
------
heidiMatrix_obj : HeidiMatrix object
"""
def matrix_map(dataset, datasetName):
	subspace_obj = heidi_classes.SubspaceCl()
	subspace_obj.initialize(list(dataset.columns))
	subspace_obj.setAllSubspace()
	allSubspaces = subspace_obj.getAllSubspace()
	
	
	heidiMatrix_obj = heidi_classes.HeidiMatrix()
	heidiMatrix_obj.initialize(dataset, datasetName)
	heidiMatrix_obj.setSubspaceList(allSubspaces)
	heidiMatrix_obj.setSubspaceHeidi_map()
	return heidiMatrix_obj

def image_map(dataset, datasetName, heidiMatrix_obj, filtered_subspaces):
#getAllSubspaces	
	colorAssign_obj = assign_color.ColorAssign()
	colorAssign_obj.initialize(dataset, filtered_subspaces)
	colormap = colorAssign_obj.getColormap()
	assign_color.saveColormap_DB(colormap, datasetName)

	heidiImage_obj = heidi_classes.HeidiImage()
	heidiImage_obj.initialize(dataset, datasetName)
	heidiImage_obj.setHeidiMatrix_obj(heidiMatrix_obj)
	heidiImage_obj.setSubspaceVector(filtered_subspaces)
	#print('filtered_subspaces',filtered_subspaces)
	heidiImage_obj.setSubspaceHeidiImage_map()
	
	
	compositeImage = heidiImage_obj.getHeidiImage()
	

	subspaceHeidiImg_map = heidiImage_obj.getSubspaceHeidiImage_map()
	subspaceHeidiMatrix_map = heidiMatrix_obj.getSubspaceHeidi_map()
	heidi_classes.saveHeidiMatrix_DB(subspaceHeidiMatrix_map,subspaceHeidiImg_map,datasetName)

	paramobj = HeidiParam()
	paramobj.datasetName = datasetName
	paramobj.allDims = list(dataset.columns)
	paramobj.filteredSubspaces = filtered_subspaces
	paramobj.filteredSubspaces_colormap = {str(k):colormap[k] for k in colormap}
	
	
	return paramobj

def getSelectedSubspaces(datasetName, colorList):
	obj = models.Dataset.query.filter_by(name=datasetName).first() #SERAILIZED CONTENT FROM DATABASE
	dataset = cPickle.loads(obj.content) #cleaned file is stored in Database
	colorMap = assign_color.getColormap_DB(datasetName, colorList)
	selectedSubspaces = list(colorMap.keys())

	heidiMatrix_obj = heidi_classes.HeidiMatrix()
	heidiMatrix_obj.initialize(dataset, datasetName)
	heidiMatrix_obj.setSubspaceList(selectedSubspaces)
	heidiMatrix_obj.setSubspaceHeidi_map_db()
	subspaceHeidiMatrix_map = heidiMatrix_obj.getSubspaceHeidi_map()
	
	heidiImage_obj = heidi_classes.HeidiImage()
	heidiImage_obj.initialize(dataset, datasetName)
	heidiImage_obj.setHeidiMatrix_obj(heidiMatrix_obj)
	heidiImage_obj.setSubspaceVector(selectedSubspaces)
	#print('allsubspaces',allSubspaces)
	heidiImage_obj.setSubspaceHeidiImage_map()
	
	
	compositeImage = heidiImage_obj.getHeidiImage()

	return compositeImage
	

	
    