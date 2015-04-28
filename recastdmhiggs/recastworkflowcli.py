import subprocess
import glob
import jinja2
import yoda
import os
import yaml
import logging
import click

logging.basicConfig(level=logging.INFO)
log = None
log = logging.getLogger(__name__)

import adage
from adage import adagetask,mknode

@adagetask
def fiducialeff(workdir,yodafile):
  histos = yoda.readYODA(yodafile)
  cutflow = histos['/DMHiggsFiducial/Cutflow']
  efficiency = cutflow.bins[-1].area/cutflow.bins[0].area

  log.info('calculated efficiency: {}'.format(efficiency))

  with open('{}/results.yaml'.format(workdir),'w') as f:
    f.write(yaml.dump({'efficiency':efficiency},default_flow_style=False))

@adagetask
def rivet(workdir):
  yodafile = '{}/Rivet.yoda'.format(workdir)
  plotdir = '{}/plots'.format(workdir)
  analysisdir = os.path.abspath('rivet')
  log.info('running rivet')

  individualyodafiles = glob.glob('{}/*.yoda'.format(workdir))
  subprocess.check_call(['yodamerge','-o',yodafile]+individualyodafiles)

  log.info('preparing plots')
  subprocess.check_call(['rivet-mkhtml','-c','rivet/DMHiggsFiducial.plot','-o',plotdir,yodafile])
  
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
def isLesHouches(file):
  if not os.path.isfile(file): return False
  log.info("checking file format of {}".format(file))
  try:
      e,el = ET.iterparse(file,events=['start','end']).next()
      return (e=='start' and el.tag =='LesHouchesEvents')
  except ParseError:
      return False

@adagetask
def combined_pythia_rivet(workdir,lhefilename):
  log.info('running pythia on {}'.format(lhefilename))

  absinputfname = os.path.abspath(lhefilename)
  basefname = os.path.basename(absinputfname)

  steeringfname = '{}/{}.steering'.format(workdir,basefname)
  fifoname = workdir+'/'+basefname.rsplit('.',1)[0]+'.fifo'
  yodaname = workdir+'/'+basefname.rsplit('.',1)[0]+'.yoda'

  env = jinja2.Environment(undefined=jinja2.StrictUndefined)
  steeringfile = 'pythiasteering.tplt'
  if not os.path.exists(steeringfile):
    log.error('steering file does not exist')

  with open(steeringfile  ) as steeringfile:
    template = env.from_string(steeringfile.read())
    with open(steeringfname,'w+') as output:
      output.write(template.render({'INPUTLHEF':absinputfname}))

  analysisdir = os.path.abspath('rivet')

  os.mkfifo(fifoname)
  pythia_proc = subprocess.Popen(['pythia/pythiarun',steeringfname,fifoname])
  rivat_proc = subprocess.check_call(['rivet','-a','DMHiggsFiducial',fifoname,'-H',yodaname,'--analysis-path={}'.format(analysisdir)])
  pythia_proc.wait()
  
  os.remove(fifoname)
  
def build_initial_dag(workdir):
  dag = adage.mk_dag()

  fileglob = "{}/inputs/*.events".format(workdir)
  log.info("looking for files: {}".format(fileglob))

  eventfiles = filter(isLesHouches,glob.glob("{}/inputs/*".format(workdir)))

  if not eventfiles: raise IOError

  pythia_nodes = [mknode(dag,combined_pythia_rivet.s(workdir = workdir, lhefilename = lhe)) for lhe in eventfiles]
  rivet_node    = mknode(dag,rivet.s(workdir = workdir), depends_on = pythia_nodes)
  prepare_node  = mknode(dag,fiducialeff.s(workdir = workdir, yodafile = '{}/Rivet.yoda'.format(workdir)),depends_on = [rivet_node])

  rules = []
  return dag,rules

@click.command()
@click.argument('workdir')
@click.option('--logger', default = __name__, help = 'name of logger to log to')
@click.option('--track/--no_track', default=False)
def run_workflow(workdir,logger,track):
  global log
  log = logging.getLogger(logger)
  dag,rules = build_initial_dag(workdir)
  adage.rundag(dag,rules, track = track)