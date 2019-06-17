from flask import request, render_template, Blueprint, json, redirect, url_for, flash, session

from mod_heidiPreprocessing import assign_color, order_points, subspace_filter
from mod_heidi import heidi_classes
import _pickle as cPickle
import models


class HeidiParam:

	def __init__(self):
		self.datasetPath=''
		self.allDims = ''
		self.orderDims = ''
		self.otherDims = ''
		self.allSubspaces = ''
		self.selectedSubspace = ''
		self.allSubspaces_colormap = ''


def getAllSubspaces(dataset, datasetname):
	subspace_obj = heidi_classes.SubspaceCl()
	subspace_obj.initialize(list(dataset.columns))
	subspace_obj.setAllSubspace()
	allSubspaces = subspace_obj.getAllSubspace()
	
	colorAssign_obj = assign_color.ColorAssign()
	colorAssign_obj.initialize(dataset, allSubspaces)
	colormap = colorAssign_obj.getColormap()
	assign_color.saveColormap_DB(colormap, datasetname)

	heidiMatrix_obj = heidi_classes.HeidiMatrix()
	heidiMatrix_obj.initialize(dataset, datasetname)
	heidiMatrix_obj.setSubspaceList(allSubspaces)
	heidiMatrix_obj.setSubspaceHeidi_map()
	subspaceHeidiMatrix_map = heidiMatrix_obj.getSubspaceHeidi_map()
	
	heidiImage_obj = heidi_classes.HeidiImage()
	heidiImage_obj.initialize(dataset, datasetname)
	heidiImage_obj.setHeidiMatrix_obj(heidiMatrix_obj)
	heidiImage_obj.setSubspaceVector(allSubspaces)
	#print('allsubspaces',allSubspaces)
	heidiImage_obj.setSubspaceHeidiImage_map()
	
	
	compositeImage = heidiImage_obj.getHeidiImage()
	

	subspaceHeidiImg_map = heidiImage_obj.getSubspaceHeidiImage_map()

	heidi_classes.saveHeidiMatrix_DB(subspaceHeidiMatrix_map,subspaceHeidiImg_map,datasetname)

	paramobj = HeidiParam()
	paramobj.datasetPath = datasetname
	paramobj.allDims = list(dataset.columns)
	paramobj.allSubspaces = allSubspaces
	paramobj.allSubspaces_colormap = {str(k):colormap[k] for k in colormap}

	return paramobj

def getSelectedSubspaces(datasetname, colorList):
	obj = models.Dataset.query.filter_by(name=datasetname).first() #SERAILIZED CONTENT FROM DATABASE
	dataset = cPickle.loads(obj.content) #cleaned file is stored in Database
	colorMap = assign_color.getColormap_DB(datasetname, colorList)
	selectedSubspaces = list(colorMap.keys())

	heidiMatrix_obj = heidi_classes.HeidiMatrix()
	heidiMatrix_obj.initialize(dataset, datasetname)
	heidiMatrix_obj.setSubspaceList(selectedSubspaces)
	heidiMatrix_obj.setSubspaceHeidi_map_db()
	subspaceHeidiMatrix_map = heidiMatrix_obj.getSubspaceHeidi_map()
	
	heidiImage_obj = heidi_classes.HeidiImage()
	heidiImage_obj.initialize(dataset, datasetname)
	heidiImage_obj.setHeidiMatrix_obj(heidiMatrix_obj)
	heidiImage_obj.setSubspaceVector(selectedSubspaces)
	#print('allsubspaces',allSubspaces)
	heidiImage_obj.setSubspaceHeidiImage_map()
	
	
	compositeImage = heidiImage_obj.getHeidiImage()

	return compositeImage
	

	
    