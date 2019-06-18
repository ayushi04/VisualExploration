import math
import numpy as np
import pandas as pd
import _pickle as cPickle
from sklearn.neighbors import NearestNeighbors
from PIL import Image
from flask import session

import models
from mod_heidiPreprocessing import assign_color
from mod_heidiPreprocessing import jaccardMatrix
from app import db
import cv2

class SubspaceCl:

    def __init__(self):
        self.columns = []
        self.allSubspace = []
        self.nofdims = ''

    def initialize(self, columns):
        self.columns = columns
        self.nofdims = len(columns)
        #self.setAllSubspace()

    """
    This method identifies all possible subspaces and saves in class variable allSubspaces
    e.g.,
        self.allSubspace = [(d1,d2),(d1),(d2)]
    """
    def setAllSubspace(self, subspace=None):
        if(subspace!=None):
            return NotImplementedError('setAllSubspace set subspace not implemented')
        self.allSubpace = []
        
        max_count=int(math.pow(2,self.nofdims))
        allsubspaces=range(1,max_count)
        f=lambda a:sorted(a,key=lambda x:sum(int(d)for d in bin(x)[2:]))
        allsubspaces=f(allsubspaces)

        frmt=str(self.nofdims)+'b'
        for i in allsubspaces:
            bin_value=str(format(i,frmt))
            bin_value=bin_value[::-1]
            subspace_col=[self.columns[index] for index,value in enumerate(bin_value) if value=='1']
            self.allSubspace.append(tuple(subspace_col))
        return      

    def getAllSubspace(self):
        return self.allSubspace


class HeidiMatrix:

    def __init__(self):
        self.dataset = ''
        self.pointsOrder = []
        self.subspaceHeidi_map = {}
        self.subspaceList = '' #[(a,b,c), (a)] [tuple, tuple, ..]
        self.knn = 10
        self.datasetName = ''

    def initialize(self, dataset, datasetName):
        self.dataset = dataset
        self.pointsOrder = list(dataset.index)
        self.datasetName = datasetName
        self.subspaceList = []
        #self._setSubspaceHeidi_map()
    
    def getSubspaceHeidi_map(self):
        return self.subspaceHeidi_map

    def getSubspaceList(self):
        return self.subspaceList
    
    def getHeidiMatrix_oneSubspace(self,subspace):
        return self.subspaceHeidi_map[subspace]

    def getHeidiMatrix_allSubspace(self):
        #TODO : write code to create Heidi matrix for all subspaces
        pass

    def setSubspaceHeidi_map_db(self):
        """
        sets the subspaceHeidi_map dictionary object
        e.g.,
        subspaceHeidi_map[tuple]=np.array([[],.....[]]) 
        subspaceHeidi_map[(d1,d2)]=np.array([[],.....[]]) 
        subspaceHeidi_map[(d1)]=np.array([[],.....[]]) 

        INPUT:
        subspaces=[]
        """
        for subspace in self.subspaceList:
            heidiMap = models.SubspaceHeidiMap.query.filter_by(subspace = str(subspace), dataset = self.datasetName).first()
            self.subspaceHeidi_map[subspace] = cPickle.loads(heidiMap.heidiMatrix)


    """
    Reorders the matrices in subspaceHeidi_map based on newPointsOrder given
    """
    def reorderHeidiMatrix(self, newPointsOrder):
        pass        

    def setSubspaceHeidi_map(self):
        """
        sets the subspaceHeidi_map dictionary object
        e.g.,
        subspaceHeidi_map[tuple]=np.array([[],.....[]]) 
        subspaceHeidi_map[(d1,d2)]=np.array([[],.....[]]) 
        subspaceHeidi_map[(d1)]=np.array([[],.....[]]) 
        """
        for subspace in self.subspaceList:
            self.subspaceHeidi_map[subspace] = self._createHeidiMatrix(subspace)

    def setSubspaceList(self, subspaceList):
        self.subspaceList = subspaceList

    def _createHeidiMatrix(self, subspace):
        #DONE : write Heidi algorithm to return knn matrix for this subspace
        row=self.dataset.shape[0]
        heidi_matrix=np.zeros(shape=(row,row),dtype=np.uint64)
        #subspace_col = [i for i,x in enumerate(subspace) if x]
        #filtered_data=self.inputData.iloc[:,subspace_col]
        filtered_data=self.dataset.loc[:,subspace]
        np_subspace=filtered_data.values
        nbrs=NearestNeighbors(n_neighbors=self.knn,algorithm='ball_tree').fit(np_subspace)
        temp=nbrs.kneighbors_graph(np_subspace).toarray()
        heidiMatrix=temp.astype(np.uint64)
        return heidiMatrix


class HeidiImage:

    def __init__(self):
        self.heidiMatrix_obj = HeidiMatrix()
        self.dataset = ''
        self.colorAssign = ''
        self.heidiImage = ''
        self.subspaceVector = []
        self.datasetName = ''
        self.subspaceHeidiImage_map = {}


    def initialize(self, dataset, datasetName):
        self.dataset = dataset
        self.datasetName = datasetName
        #self.heidiMatrix_obj.initialize(self.dataset, self.datasetName)
        self.colorAssign = assign_color.ColorAssign()

    def setHeidiMatrix_obj(self, hobj):
        self.heidiMatrix_obj = hobj

    def getHeidiMatrix_obj(self):
        return self.heidiMatrix_obj

    def setSubspaceVector(self, subspaceVector):
        self.subspaceVector = subspaceVector

    def getSubspaceVector(self):
        return  self.subspaceVector

    def _imageUnion(self,img1, img2):
        row = img1.shape[0]
        col = img1.shape[1]
        #print(row,col)
        for i in range(0,row):
            for j in range(0,col):
                #print(img2[i][j], type(img2[i][j]))
                if(list(img2[i][j])==[255,255,255]):
                    continue
                if(list(img1[j][j])==[255,255,255]):
                    img1[i][j]=img2[i][j]
                    continue
                img1[i][j] = (img1[i][j]+img2[i][j])/2
        return img1


    def getHeidiImage(self):
        #TODO: write code to generate composite image  
        compositeImg = 0
        mask_sum=0
        for subspace in self.subspaceVector[0:]:
            heidi_matrix = self.heidiMatrix_obj.getHeidiMatrix_oneSubspace(subspace)
            mask = np.dstack((heidi_matrix, heidi_matrix, heidi_matrix))
            mask_sum +=mask
            compositeImg = compositeImg + np.multiply(mask, self.subspaceHeidiImage_map[subspace])

        compositeImg = compositeImg / mask_sum
        compositeImg = compositeImg.astype(np.uint8)
        index_list = np.where(np.all(compositeImg == [0,0,0], axis=-1))
        compositeImg[index_list]=[255,255,255]
        compositeImg = Image.fromarray(compositeImg)
        #compositeImg.save('./imgs/compositeImg.png')
        compositeImg.save('./static/imgs/compositeImg.png')
        return compositeImg
        
    def getSubspaceHeidiImage_map(self):
        return self.subspaceHeidiImage_map

    def setSubspaceHeidiImage_map(self):
        c=1
        for subspace in self.subspaceVector:
            self.subspaceHeidiImage_map[subspace] = self.getHeidiImage_oneSubspace(subspace)
            img = Image.fromarray(self.subspaceHeidiImage_map[subspace])
            img.save('./imgs/img'+str(c)+'.png')
            c=c+1
        return

    def getHeidiImage_oneSubspace(self,subspace):
        color = models.SubspaceColorMap.query.filter_by(dataset=self.datasetName, subspace=str(subspace))
        color = assign_color.hex_to_rgb(color[0].color)
        heidi_matrix = self.heidiMatrix_obj.getHeidiMatrix_oneSubspace(subspace)
        arr = np.zeros((heidi_matrix.shape[0],heidi_matrix.shape[1],3))
        for i in range(heidi_matrix.shape[0]):
            for j in range(heidi_matrix.shape[1]):
                if(heidi_matrix[i][j]==1):
                    arr[i][j]=color
                else:
                    arr[i][j]=[255,255,255]
        tmp = arr.astype(np.uint8)
        return tmp
        #img = Image.fromarray(tmp)
        #return img


def saveHeidiMatrix_DB(subspaceHeidiMatrix_map, subspaceHeidiImage_map, datasetName):
    """
    INPUT
    ------
    subspaceHeidiMatrix_map : dictionary type
    {(d1,d2):[[0,1,.....1],.....[1,1,.......0]}
    """
    existingDataset = models.SubspaceHeidiMap.query.filter_by(dataset=datasetName).all()
    for data in existingDataset:
        db.session.delete(data)
    objects = []
    '''
    for key in subspaceHeidiMatrix_map:
        print('kkkk',key)
        serialized_matrix = cPickle.dumps(subspaceHeidiMatrix_map[key])
        img = ''
        if(key in subspaceHeidiImage_map.keys()):
            img = subspaceHeidiImage_map[key]
            img = Image.fromarray(img)
        serialized_image = cPickle.dumps(img)
        obj = models.SubspaceHeidiMap(str(key), datasetName, serialized_matrix, serialized_image) # (subspace:tuple_string,datasetName:string, heidi_matrix (2-d numpy array), heidi_image)
        objects.append(obj)
    '''
    for key in subspaceHeidiImage_map:
        serialized_matrix = cPickle.dumps(subspaceHeidiMatrix_map[key])
        serialized_image = cPickle.dumps(subspaceHeidiImage_map[key])
        obj = models.SubspaceHeidiMap(str(key), datasetName, serialized_matrix, serialized_image) # (subspace:tuple_string,datasetName:string, heidi_matrix (2-d numpy array), heidi_image)
        objects.append(obj)
    db.session.bulk_save_objects(objects)
    db.session.commit()



def getBlockId(x,y,cleaned_file):
    #rowBlock = 0
    #colBlock = 1
    #return rowBlock, colBlock
    #TODO remove hardcode and write code here
    classLabel= list(cleaned_file['classLabel'])
    class_count=[]
    class_label=[]
    for i in set(classLabel):
        c=classLabel.count(i)
        class_count.append(c)
        class_label.append(i)
    #print('class_count', class_count)
    #print('classLabel', class_label)
    c=0
    for i in range(len(class_count)):
        c = c + class_count[i]
        if(c >= x):
            block_row = i
            break
    c=0
    for i in range(len(class_count)):
        c = c + class_count[i]
        if(c >= y):
            block_col = i
            break

    return block_row, block_col
    
def getBlockRange(block_row,block_col,cleaned_file):
    #count = cleaned_file['classLabel'].value_counts()
    x= list(cleaned_file['classLabel'])
    class_count=[]
    class_label=[]
    for i in set(x):
        c=x.count(i)
        class_count.append(c)
        class_label.append(i)
    tlx=0
    tly=0
    #print('BBLOCK',block_row,block_col)
    for i in range(block_row): tlx = tlx + int(class_count[i])
    for i in range(block_col): tly = tly + int(class_count[i])
    brx=0
    bry=0
    for i in range(block_row+1): brx = brx + int(class_count[i])
    for i in range(block_col+1): bry = bry + int(class_count[i])
    
    return tlx+1, tly+1, brx-1, bry-1


def getPatternPoints(compositeImg,rowBlock,colBlock, cleaned_file, selectedColor):
    pix = compositeImg.load()
    rowPoints = []
    colPoints = []
    pointsPair = []
    tlx, tly, brx, bry = getBlockRange(rowBlock,colBlock,cleaned_file)
    #print('range:', tlx,tly,brx, bry)
    #print('selectedColor', selectedColor)
    for i in range(tlx, brx +1):
        for j in range(tly, bry + 1):
            if(pix[i,j]==selectedColor):
                rowPoints.append(cleaned_file.loc[i,'id'])
                colPoints.append(cleaned_file.loc[j,'id'])
                pointsPair.append((cleaned_file.loc[i,'id'],cleaned_file.loc[j,'id']))
    rowPoints = list(set(rowPoints))
    colPoints = list(set(colPoints))
    return rowPoints, colPoints, pointsPair

"""
This method computes the similarity of different color patterns in a Heidi Block
Similarity Measure: Jaccard Similarity of (rowPoints U colPoints ) set

INPUT
------
rowBlock: row Block number (integer)
colBlock: column Block number (integer)
cleaned_file: file with id and classLabel as columns (dataframe)

OUTPUT
--------
matrix: similarity matrix (dataframe)

"""
def getAllPatterns_block(rowBlock, colBlock, cleaned_file):
    tlx, tly, brx, bry = getBlockRange(rowBlock,colBlock, cleaned_file)
    datasetName=session["filename"]
    colorMap = cPickle.loads(session["paramObj"]).filteredSubspaces_colormap
    #print(colorMap.keys(),'-----------hello----------------')
    allSubspaces = list(colorMap.keys())

    heidiMatrix_obj = HeidiMatrix()
    heidiMatrix_obj.initialize(cleaned_file, datasetName)
    heidiMatrix_obj.setSubspaceList(allSubspaces)
    heidiMatrix_obj.setSubspaceHeidi_map_db()
    subspaceHeidiMatrix_map = heidiMatrix_obj.getSubspaceHeidi_map()
    
    heidiImage_obj = HeidiImage()
    heidiImage_obj.initialize(cleaned_file, datasetName)
    heidiImage_obj.setHeidiMatrix_obj(heidiMatrix_obj)
    heidiImage_obj.setSubspaceVector(allSubspaces)
    #print('allsubspaces',allSubspaces)
    heidiImage_obj.setSubspaceHeidiImage_map()

    patterns_df = pd.DataFrame(columns=['color','subspace','rowPoints','colPoints','pointsPair'])
    i=0
    for subspace in allSubspaces:
        imgarray = heidiImage_obj.getHeidiImage_oneSubspace(subspace)
        img = Image.fromarray(imgarray)
        colors = img.convert('RGB').getcolors()
        rowPoints,colPoints,pointsPair = getPatternPoints(img,rowBlock,colBlock, cleaned_file,colors[1][1])
        patterns_df.loc[i] = [str(colors[1][1]), str(subspace), rowPoints, colPoints, pointsPair]
        #img.save('static/output/temp'+str(i)+'.png')    
        i=i+1
    return patterns_df
    #mat = jaccardMatrix.getJaccardMatrix(patterns_df)
    #return mat
