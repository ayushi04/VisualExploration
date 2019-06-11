from mod_heidiPreprocessing import assign_color, order_points, subspace_filter
from mod_heidi import heidi_classes

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
	heidiMatrix_obj.setSubspaceAllHeidi_map()
	subspaceHeidiMatrix_map = heidiMatrix_obj.getSubspaceHeidi_map()
	
	heidiImage_obj = heidi_classes.HeidiImage()
	heidiImage_obj.initialize(dataset, datasetname)
	heidiImage_obj.setHeidiMatrix_obj(heidiMatrix_obj)
	#print('allsubspaces',allSubspaces)
	heidiImage_obj.setSubspaceVector(allSubspaces)
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

def getSelectedSubspaces(dataset, colorList):
	colorMap = assign_color.getColormap_DB(dataset, colorList)
	heidiMatrix_obj = heidi_classes.HeidiMatrix()
	heidiMatrix_obj.initialize(dataset, datasetname)
	
    