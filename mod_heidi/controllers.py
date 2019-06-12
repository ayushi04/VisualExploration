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

from mod_datacleaning import data_cleaning
from mod_heidi import heidi_api
from mod_heidiPreprocessing import assign_color

mod_heidi_controllers = Blueprint('heidi_controllers', __name__)



@mod_heidi_controllers.route('/interactive_heidi', methods=['GET','POST'])
def interactive_heidi():
    filename = session['filename']
    obj = models.Dataset.query.filter_by(name=filename).first()
    cleaned_file = cPickle.loads(obj.content)
    del cleaned_file['classLabel']
    cleaned_file.index = cleaned_file['id']
    del cleaned_file['id']
    print(cleaned_file)
    paramObj = heidi_api.getAllSubspaces(cleaned_file, filename)
    session['paramObj'] = cPickle.dumps(paramObj)
    return render_template('dimension_new.html', title = 'visual tool', user = current_user, paramObj = paramObj) #title='dimension Visualization',datasetPath=datasetPath,user=current_user, dimensions=['a','b','c'])
    

@mod_heidi_controllers.route('/heidi', methods=['GET','POST'])
def heidi():
    colorList = request.form.getlist('color[]')
    orderDim = request.form.getlist('orderDim')
    otherDim = request.form.getlist('otherDim')
    datasetname = session['filename']
    obj = models.Dataset.query.filter_by(name=datasetname).first()
    cleaned_file = cPickle.loads(obj.content)
    del cleaned_file['classLabel']
    cleaned_file.index = cleaned_file['id']
    del cleaned_file['id']
    paramObj = heidi_api.getAllSubspaces(cleaned_file, datasetname)
    
    #CODE TO ORDER POINTS BASED ON ORDER DIM (CAN DO LATER)

    #GET HEIDI IMAGE FROM DATABASE

    #REORDER THE POINTS IN IMAGE (CAN DO LATER)

    #CREATE THE COMBINED IMAGE FOR SELECTED SUBSPACES.
    compositeImg = heidi_api.getSelectedSubspaces(datasetname,colorList)
    return render_template('dimension_new.html', title = 'visual tool', user = current_user, paramObj = paramObj, image = 'imgs/composite_img.png')




    #return redirect(url_for('heidi_controllers.interactive_heidi'))
    return "hello" + str(colorList) + str(orderDim) + str(otherDim)
    #title=request.args.get('title')
    #user = request.args.get('user')
    #paramObj = jsonrequest.data.get('paramObj').to_dict()
    #print(paramObj['datasetPath'],'heidi_controllers')
    #return render_template('dimension_new.html', paramObj = paramObj) #title='dimension Visualization',datasetPath=datasetPath,user=current_user, dimensions=['a','b','c'])
