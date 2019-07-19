from mod_heidiPreprocessing import orderPoints
import numpy as np
import pandas as pd
import models
from app import db
import _pickle as cPickle

default_order = 'dimension'
"""
INPUT: 
A) cleaned_file with index and classLabel (dataframe)
B) Subspace (list)
OUTPUT: sorted index (list)
"""
def order(cleaned_file, subspace, orderMeasure = default_order):
    #cleaned_file.index = cleaned_file['id']
    if('id' in cleaned_file.columns):
        del cleaned_file['id']
    order_inp = cleaned_file[list(subspace)+['classLabel'] ]
    order_inp.loc[:,'classLabel_orig']=order_inp.loc[:,'classLabel']
    order_inp.index.name='id'
    param={}
    param['columns']=list(subspace)
    param['order']=[True for i in list(subspace)]
    sorted_data = orderPoints.sortbasedOnclassLabel(order_inp,orderMeasure, param) 
    sorted_data_index = list(sorted_data.index)
    return sorted_data_index

"""
INPUT:
A) heidiMatrix (numpy array)
B) pointsorder (list)
OUTPUT: rearranged heidiMatrix
"""
def orderMatrix(heidiMatrix, pointsorder):
    heidiMatrix_new = heidiMatrix[:,pointsorder]
    heidiMatrix_new = heidiMatrix_new[pointsorder,:]
    return heidiMatrix_new


def orderMatrixMap_composite(heidiMatrixMap,datasetname):
    ordered_map={}
    for subspace in heidiMatrixMap.keys():
        ord1 = getOrder_fromDB_1subspace(datasetname, subspace)
        #print(ord1)
        if(ord1 is not None):
            ordered_map[subspace] = orderMatrix(heidiMatrixMap[subspace], ord1)
        else:
            print('None subspace', subspace)
    return ordered_map

def orderSubspaceMatrixMap(heidiMatrixMap,datasetname, subspace):
    ordered_map={}
    #print(su)
    ord1 = getOrder_fromDB_1subspace(datasetname, subspace)
    print(ord1,'000000000000000000')
    for s1 in heidiMatrixMap.keys():
        if(ord1 is not None):
            ordered_map[s1] = orderMatrix(heidiMatrixMap[s1], ord1)
        else:
            print('None subspace', subspace)
            ordered_map[s1] = heidiMatrixMap[s1]
    return ordered_map



def saveOrder_toDB(datasetname, cleaned_file, subspaceList, orderMeasure=default_order):
    existingDataset = models.PointOrder.query.filter_by(dataset=datasetname).all()
    for data in existingDataset:
        db.session.delete(data)
    db.session.commit()
    objects=[]
    for subspace in subspaceList:
        print(subspace)
        sorted_order = order(cleaned_file, subspace, orderMeasure)
        obj = models.PointOrder(datasetname, str(subspace), orderMeasure, cPickle.dumps(sorted_order))
        objects.append(obj)
    db.session.bulk_save_objects(objects)
    db.session.commit()

def getOrder_fromDB(datasetname, subspaceList, orderMeasure=default_order):
    subspace_order_map={}
    for subspace in subspaceList:
        obj = models.PointOrder.query.filter_by(dataset = datasetname, subspace = str(subspace), orderMeasure = orderMeasure).first()
        subspace_order_map[subspace] = cPickle.loads(obj.sorted_order)
    return subspace_order_map

def getOrder_fromDB_1subspace(datasetname, subspace, orderMeasure=default_order):
    obj = models.PointOrder.query.filter_by(dataset = datasetname, subspace = str(subspace), orderMeasure = orderMeasure).first()
    if(obj is None):
        print('ERROR: None returned!!')
        return None
    return cPickle.loads(obj.sorted_order)

