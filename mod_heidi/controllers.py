from flask import request, render_template, Blueprint, json, redirect, url_for, flash, session
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, current_user, logout_user
import random
import os
import pandas as pd
import config
import _pickle as cPickle
import models
import math
from PIL import Image

from mod_datacleaning import data_cleaning
from mod_heidi import heidi_api
from mod_heidi import heidi_classes
from mod_heidiPreprocessing import assign_color
from mod_heidiPreprocessing.subspace_search_heidi import SubspaceSearch_Heidi
from mod_heidiPreprocessing import jaccardMatrix


mod_heidi_controllers = Blueprint('heidi_controllers', __name__)

@mod_heidi_controllers.route('/interactive_heidi', methods=['GET','POST'])
def interactive_heidi():
    filename = session['filename']
    obj = models.Dataset.query.filter_by(name=filename).first()
    cleaned_file = cPickle.loads(obj.content)
    del cleaned_file['classLabel']
    cleaned_file.index = cleaned_file['id']
    del cleaned_file['id']
    #print(cleaned_file)
    heidiMatrix_obj = heidi_api.matrix_map(cleaned_file,filename)
    subspaceHeidiMatrix_map = heidiMatrix_obj.getSubspaceHeidi_map()

    #GET INTERESTING SUBSPACES
    classLabel= list(cPickle.loads(obj.content)['classLabel'])
    class_count=[]
    class_label=[]
    for i in set(classLabel):
        c=classLabel.count(i)
        class_count.append(c)
        class_label.append(i)
    #print('class_count', class_count)
    sobj = SubspaceSearch_Heidi()
    sobj.initialize(class_count, subspaceHeidiMatrix_map)
    filtered_subspaces = sobj.getTopAInterestingSubspace(15)
    #print('-------------------------------------------------')
    #print(filtered_subspaces)
    #filtered_subspaces = list(subspaceHeidiMatrix_map.keys())
    paramObj = heidi_api.image_map(cleaned_file, filename, heidiMatrix_obj, filtered_subspaces)
    session['paramObj'] = cPickle.dumps(paramObj)
    jaccard_matrix = ''
    patterns_df = heidi_classes.getAllPatterns_block( 0, 1,cPickle.loads(obj.content))
    jaccard_matrix = jaccardMatrix.getJaccardMatrix(patterns_df)
    jaccard_matrix2 = jaccardMatrix.getJaccardMatrix2(patterns_df)
    session['paramObj'] = cPickle.dumps(paramObj)
    session['jaccard_matrix'] = cPickle.dumps(jaccard_matrix)
    session['jaccard_matrix2'] = cPickle.dumps(jaccard_matrix2)
    return render_template('dimension_new.html', title = 'visual tool', user = current_user, \
                                paramObj = paramObj, \
                                jaccard_matrix = jaccard_matrix.reset_index().to_json(orient='records'), \
                                jaccard_matrix2 = jaccard_matrix2.reset_index().to_json(orient='records'))
    

#CREATE HEIDI IMAGE BASED ON USER SELECTION (SUBSPACES, ORDER DIM)
@mod_heidi_controllers.route('/heidi', methods=['GET','POST'])
def heidi():
    colorList = request.form.getlist('color[]')
    orderDim = request.form.getlist('orderDim')
    otherDim = request.form.getlist('otherDim')
    datasetName = session['filename']
    obj = models.Dataset.query.filter_by(name=datasetName).first()
    cleaned_file = cPickle.loads(obj.content)
    del cleaned_file['classLabel']
    cleaned_file.index = cleaned_file['id']
    del cleaned_file['id']
    paramObj = cPickle.loads(session['paramObj'])

    #CODE TO ORDER POINTS BASED ON ORDER DIM (CAN DO LATER)

    #GET HEIDI IMAGE FROM DATABASE

    #REORDER THE POINTS IN IMAGE (CAN DO LATER)

    #CREATE THE COMBINED IMAGE FOR SELECTED SUBSPACES.
    compositeImg = heidi_api.getSelectedSubspaces(datasetName,colorList)
    #session['compositeImg'] =cPickle.dumps(compositeImg)
    session['selectedColors'] = colorList 
    jaccard_matrix = cPickle.loads(session['jaccard_matrix'])
    jaccard_matrix2 = cPickle.loads(session['jaccard_matrix2'])
    return render_template('dimension_new.html', title = 'visual tool', \
                            user = current_user, paramObj = paramObj, \
                            image = 'imgs/compositeImg.png', \
                            jaccard_matrix = jaccard_matrix.reset_index().to_json(orient='records'), \
                            jaccard_matrix2 = jaccard_matrix2.reset_index().to_json(orient='records') \
                            )




    #return redirect(url_for('heidi_controllers.interactive_heidi'))
    return "hello" + str(colorList) + str(orderDim) + str(otherDim)
    #title=request.args.get('title')
    #user = request.args.get('user')
    #paramObj = jsonrequest.data.get('paramObj').to_dict()
    #print(paramObj['datasetName'],'heidi_controllers')
    #return render_template('dimension_new.html', paramObj = paramObj) #title='dimension Visualization',datasetName=datasetName,user=current_user, dimensions=['a','b','c'])


#IF USER CLICKS ON A PIXEL IN IMAGE, THIS METHOD IS CALLED
@mod_heidi_controllers.route('/highlightPattern')
def highlightPattern():
    print('-- highlightPattern-- ')
    x = float(request.args.get('x'))
    y = float(request.args.get('y'))
    id1 = request.args.get('id')
    #grid=request.args.get('grid')
    #gridPatterns=request.args.get('gridPatterns')
    #print('grid',grid)
    #imgType = '_'+request.args.get('imgType')
    datasetName = 'static/output'
    datasetName = session['filename']
    obj = models.Dataset.query.filter_by(name=datasetName).first()
    cleaned_file = cPickle.loads(obj.content)
    
    width, height= cleaned_file.shape[0], cleaned_file.shape[0]
    scale = 1
    x=(x*width)/scale
    y=(y*height)/scale
    #print(x-1,y-1)

    x=int(math.ceil(x))
    y=int(math.ceil(y))
    #print(x,y)
    colorList = session['selectedColors']
    compositeImg = heidi_api.getSelectedSubspaces(datasetName,colorList)
    pix = compositeImg.load()
    #print(pix[x,y],'pixxx')
    colorList = session['selectedColors']

    rowBlock,colBlock = heidi_classes.getBlockId(x,y,cleaned_file)
    #print('blockid:', rowBlock, colBlock)
    rowPoints,colPoints,pointsPair = heidi_classes.getPatternPoints(compositeImg,rowBlock,colBlock, cleaned_file,pix[x,y])
    #print(rowPoints, colPoints, pointsPair)
    rowPoints_df = cleaned_file[cleaned_file['id'].isin(rowPoints)]
    colPoints_df = cleaned_file[cleaned_file['id'].isin(colPoints)]
    #print(rowPoints_df)
    t=pd.DataFrame(rowPoints_df)
    t=t.append(colPoints_df)
    t.to_csv('static/output/rowColPoints.csv');
    return json.dumps({'rowPoints':rowPoints_df.to_json(orient='records'),'colPoints':colPoints_df.to_json(orient='records')})
    
@mod_heidi_controllers.route('/jaccardMatrix')
def jaccardMatrix_Controller():    
    datasetName = session['filename']
    obj = models.Dataset.query.filter_by(name=datasetName).first()
    cleaned_file = cPickle.loads(obj.content)
    jaccard_matrix = heidi_classes.getAllPatterns_block( 0, 1, cleaned_file)
    return json.dumps({'jaccard_matrix':jaccard_matrix.reset_index().to_json(orient='records')})
    