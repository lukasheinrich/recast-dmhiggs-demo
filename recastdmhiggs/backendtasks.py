import subprocess
import glob
import jinja2
import yoda
import os
import yaml
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('RECAST')

def fiducialeff(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)
  yodafile = '{}/Rivet.yoda'.format(workdir)
  histos = yoda.readYODA(yodafile)
  cutflow = histos['/DMHiggsFiducial/Cutflow']
  efficiency = cutflow.bins[-1].area/cutflow.bins[0].area

  log.info('calculated efficiency: {}'.format(efficiency))

  with open('{}/results.yaml'.format(workdir),'w') as f:
    f.write(yaml.dump({'efficiency':efficiency},default_flow_style=False))
      
def rivet(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)
  hepmcfiles = glob.glob('{}/*.hepmc'.format(workdir))

  if not hepmcfiles: raise IOError

  yodafile = '{}/Rivet.yoda'.format(workdir)
  plotdir = '{}/plots'.format(workdir)
  analysisdir = os.path.abspath('rivet')
  log.info('running rivet')

  subprocess.call(['rivet','-a','DMHiggsFiducial','-H',yodafile,'--analysis-path={}'.format(analysisdir)]+hepmcfiles)


  log.info('preparing plots')
  subprocess.call(['rivet-mkhtml','-c','rivet/DMHiggsFiducial.plot','-o',plotdir,yodafile])
  
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

    log.info('running pythia on input file {}/{}'.format(i+1,len(eventfiles)))
    
    subprocess.call(['pythia/pythiarun',steeringfname,outfname])
  

def recast(ctx):
  jobguid = ctx['jobguid']
  log.info('running single function')
  log.info('hello we are logging with logging module')
  log.debug('hello we are logging on debug')

  pythia(jobguid)
  rivet(jobguid)
  fiducialeff(jobguid)
  log.info('finished. thanks.')
  return jobguid

def resultlist():
  return ['Rivet.yoda','plots','results.yaml']