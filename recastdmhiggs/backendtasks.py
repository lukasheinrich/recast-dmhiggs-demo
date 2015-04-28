import subprocess
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('RECAST')

def recast(ctx):
  jobguid = ctx['jobguid']
  log.info('running single function using dagger')

  workdir = 'workdirs/{}'.format(jobguid)

  subprocess.call(['recastworkflow-dmhiggs',workdir,'--logger','RECAST'])

  log.info('finished. thanks.')
  return jobguid

def resultlist():
  return ['Rivet.yoda','plots','results.yaml']