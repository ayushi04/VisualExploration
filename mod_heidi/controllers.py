from flask import request, render_template, Blueprint, json, redirect, url_for, flash, session
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, current_user, logout_user
import random
import os
import pandas as pd
import config
import _pickle as cPickle

from mod_datacleaning import data_cleaning
from mod_heidi import heidi_api
from mod_heidiPreprocessing import assign_color

mod_heidi_controllers = Blueprint('heidi_controllers', __name__)



@mod_heidi_controllers.route('/interactive_heidi', methods=['GET','POST'])
def interactive_heidi():
    cleaned_file = cPickle.loads(session['cleaned_file'])
    filename = session['filename']
    del cleaned_file['classLabel']
    cleaned_file.index = cleaned_file['id']
    del cleaned_file['id']
    paramObj = heidi_api.getAllSubspaces(cleaned_file, filename)
    return render_template('dimension_new.html', title = 'visual tool', user = current_user, paramObj = paramObj) #title='dimension Visualization',datasetPath=datasetPath,user=current_user, dimensions=['a','b','c'])
    

@mod_heidi_controllers.route('/heidi', methods=['GET','POST'])
def heidi():
    colorList = request.form.getlist('color[]')
    orderDim = request.form.getlist('orderDim')
    otherDim = request.form.getlist('otherDim')
    cleaned_file = cPickle.loads(session['cleaned_file'])

    datasetname = session['filename']


    #CODE TO ORDER POINTS BASED ON ORDER DIM (CAN DO LATER)

    #GET HEIDI IMAGE FROM DATABASE
    
    #REORDER THE POINTS IN IMAGE (CAN DO LATER)

    #CREATE THE COMBINED IMAGE FOR SELECTED SUBSPACES.




    #return redirect(url_for('heidi_controllers.interactive_heidi'))
    return "hello" + str(colorList) + str(orderDim) + str(otherDim) + str(colorMap)
    #title=request.args.get('title')
    #user = request.args.get('user')
    #paramObj = jsonrequest.data.get('paramObj').to_dict()
    #print(paramObj['datasetPath'],'heidi_controllers')
    #return render_template('dimension_new.html', paramObj = paramObj) #title='dimension Visualization',datasetPath=datasetPath,user=current_user, dimensions=['a','b','c'])
