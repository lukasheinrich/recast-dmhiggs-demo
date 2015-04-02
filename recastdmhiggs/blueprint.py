from flask import Blueprint, render_template, jsonify, request
blueprint = Blueprint('dmhiggs_analysis', __name__, template_folder='templates')

import json
import requests
import requests
import os
from zipfile import ZipFile
import glob
import yaml

from recastbackend.resultaccess import resultfilepath

@blueprint.route('/result/<requestId>/<parameter_pt>')
def result_view(requestId,parameter_pt):
  resultdir  = resultfilepath(requestId,parameter_pt,'dedicated','')

  globresult = glob.glob('{}/plots/DMHiggsFiducial/*.dat'.format(resultdir))

  resultdata = yaml.load(open('{}/results.yaml'.format(resultdir)))
  efficiency = resultdata['efficiency']

  plotlist = [os.path.basename(p).rsplit('.',1)[0] for p in globresult]
  return render_template('dmhiggs_result.html',
                         efficiency = efficiency, 
                         requestId=requestId,
                         parameter_pt=parameter_pt,
                         plotlist = plotlist)
