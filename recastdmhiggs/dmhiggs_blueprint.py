from flask import Blueprint, render_template, jsonify, request
blueprint = Blueprint('dmhiggs_analysis', __name__, template_folder='dmhiggs_templates')

RECAST_ANALYSIS_ID = '858fb12c-b62f-9954-1997-a6ff8c27be0e'


RECASTSTORAGEPATH = '/home/analysis/recast/recaststorage'

import json
import requests
import dmhiggs_backendtasks
import requests
import os
from zipfile import ZipFile
import glob

@blueprint.route('/result/<requestId>/<parameter_pt>/efficiency')
def efficiency(requestId,parameter_pt):
  result =  dmhiggs_backendtasks.fiducialeff(requestId,parameter_pt)
  return jsonify(efficiency=result)

@blueprint.route('/result/<requestId>/<parameter_pt>')
def result_view(requestId,parameter_pt):
  plotlist = [os.path.basename(p).rsplit('.',1)[0] for p in glob.glob('{}/results/{}/{}/plots/DMHiggsFiducial/*.dat'.format(RECASTSTORAGEPATH,requestId,parameter_pt))]
  return render_template('dmhiggs_result.html',analysisId = RECAST_ANALYSIS_ID,requestId=requestId,parameter_pt=parameter_pt,plotlist = plotlist)


