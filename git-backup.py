#!/usr/bin/python -tt

import sys,getopt
import commands 
import logging
import json
import time

logger = logging.getLogger('stencil')
hdlr = logging.StreamHandler(sys.stdout)
#hdlr = logging.FileHandler('stencil.log') 
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO) #logging.DEBUG


class Repo(object):

  def __init__(self, r, destination):

    self.endpoint = r['endpoint']
    self.name = "%s.%d" % ( r['name'], time.time() )
    self.destination = "%s/%s" % ( destination, self.name )

    self.backup()

  def backup(self):
    logger.info("Backing up %s" % self.name)
    self.cleanup()
    self.clone()
    self.compress()
    self.cleanup()
    logger.info("%s Complete" % self.name)

  def clone(self):

    cmd = "git clone %s %s" % ( self.endpoint, self.name )
    output = Run(cmd)

  def compress(self):
    cmd = "tar -czf %s.tgz %s" % ( self.destination, self.name )
    Run(cmd)

  def cleanup(self):
    cmd="rm -fr %s" % self.name
    Run(cmd)



def help():

  print " Usage: %s --repos-file your-repo-file.json [--help] " % sys.argv[0]



def Run(cmd):
 
  logger.info("** Running: %s" % cmd)

  (status,output) = commands.getstatusoutput(cmd)

  if status > 0:
    logger.error(cmd)
    logger.error(output)
    sys.exit(2)

  return output



def main(argv):

  reposFile=None
  destination="."
  # make sure command line arguments are valid
  try:
    options, args = getopt.getopt(

       argv, 
      'hvr:d:', 
      [ 
        'help',
        'verbose',
        'repos-file=',
        'destination='
    
      ])
 
  except getopt.GetoptError:
    logging.fatal("Bad options!")
    help()
    sys.exit(2)


  # handle command line arugments
  for opt, arg in options:
    if opt in ('-h', '--help'):
      help()
      sys.exit(2)
    elif opt in ('-v', '--verbose'):
      logger.setLevel(logging.DEBUG) 
    elif opt in ('-r', '--repos-file'):
      reposFile=arg
    elif opt in ('-d', '--destination'):
      destination=arg

  ###################################
  # main code starts here
  ###################################

  if not reposFile:
    help()
    sys.exit(2)

  # read the json file
  try:
    with open(reposFile) as data:    
      repos = json.load(data)
  except Exception, e:
    logger.error("Could not parse repo JSON file")
    sys.exit(2)    

  for repo in repos:
    r = Repo(repo, destination)
 

if __name__ == "__main__":
  main(sys.argv[1:])
 
 