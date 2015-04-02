import time
from celery import shared_task

import subprocess
import glob
import jinja2
import yoda
import os
import shutil
import yaml

import zipfile

from recastbackend.logging import socketlog

@shared_task
def fiducialeff(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)
  yodafile = '{}/Rivet.yoda'.format(workdir)
  histos = yoda.readYODA(yodafile)
  cutflow = histos['/DMHiggsFiducial/Cutflow']
  efficiency = cutflow.bins[-1].area/cutflow.bins[0].area

  socketlog(jobguid,'calculated efficiency: {}'.format(efficiency))

  with open('{}/results.yaml'.format(workdir),'w') as f:
    f.write(yaml.dump({'efficiency':efficiency},default_flow_style=False))
      
  return jobguid

@shared_task
def rivet(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)
  hepmcfiles = glob.glob('{}/*.hepmc'.format(workdir))

  if not hepmcfiles: raise IOError

  yodafile = '{}/Rivet.yoda'.format(workdir)
  plotdir = '{}/plots'.format(workdir)
  analysisdir = os.path.abspath('rivet')
  socketlog(jobguid,'running rivet')

  subprocess.call(['rivet','-a','DMHiggsFiducial','-H',yodafile,'--analysis-path={}'.format(analysisdir)]+hepmcfiles)


  socketlog(jobguid,'preparing plots')
  subprocess.call(['rivet-mkhtml','-c','rivet/DMHiggsFiducial.plot','-o',plotdir,yodafile])
  
  return jobguid

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
def isLesHouches(file):
  if not os.path.isfile(file): return False
  print "trying file {}".format(file)
  try:
      e,el = ET.iterparse(file,events=['start','end']).next()
      return (e=='start' and el.tag =='LesHouchesEvents')
  except ParseError:
      return False
  
@shared_task
def pythia(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)

  fileglob = "{}/inputs/*.events".format(workdir)
  print "looking for files: {}".format(fileglob)

  eventfiles = filter(isLesHouches,glob.glob("{}/inputs/*".format(workdir)))
  
  print 'found {} event files'.format(len(eventfiles))

  env = jinja2.Environment(undefined=jinja2.StrictUndefined)


  if not eventfiles: raise IOError

  for i,file in enumerate(eventfiles):
    absinputfname = os.path.abspath(file)
    basefname = os.path.basename(absinputfname)

    steeringfname = '{}/{}.steering'.format(workdir,basefname)
    outfname = workdir+'/'+'.'.join(basefname.split('.')[0:-1]+['hepmc'])

    with open('pythiasteering.tplt') as steeringfile:
      template = env.from_string(steeringfile.read())
      with open(steeringfname,'w+') as output:
        output.write(template.render({'INPUTLHEF':absinputfname}))

    socketlog(jobguid,'running pythia on input file {}/{}'.format(i+1,len(eventfiles)))
    
    subprocess.call(['pythia/pythiarun',steeringfname,outfname])
  
  return jobguid

def resultlist():
  return ['Rivet.yoda','plots','results.yaml']

def get_chain(queuename):
  chain = (
            pythia.subtask(queue=queuename) |
            rivet.subtask(queue=queuename)  |
            fiducialeff.subtask(queue=queuename)
          )
  return chain
