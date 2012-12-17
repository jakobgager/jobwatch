#! /usr/bin/env python
"""Python dynamic status plotter
"""

import sys
import glob
import os
import stat

progname='JobWatch V1.0'
titlename=progname + ' ::: '

def create_rc():
    fil = open('jobrc.py','w')
    fil.write("# JobWatch Format Options\n# ~~~~~~~~~~~~~~~~~~~~~~~\n# (written as Python Code!)\n")
    fil.write("\nLinestyle = '-ro'\n")
    fil.write("xLabel = 'Displacement'\n")
    fil.write("yLabel = 'Reaction Force'\n")
    fil.close()

def create_plotsh():
    filename='plot.sh'
    fil = open(filename,'w')
    fil.write("#! /bin/tcsh\n")
    fil.write("#\n# This is an example plot.sh file to be used with JobWatch or Webpage Creator\n")
    fil.write("#\n# Here, 3 lines following the keyword RF1 are processed and the data extracted\n# is printed to the terminal.\n")
    fil.write("#\necho \"0 0\" ; grep RF1 -A3 qq*.dat | grep -v '\-\-' | sed -n '0~4p'|awk '{print $3, $2}'")
    fil.close()
    # change permissions to be executable
    mode = os.stat(filename).st_mode
    os.chmod(filename, mode | stat.S_IXUSR)

if glob.glob('plot.sh')==[]:
  print progname + ': plot.sh file not found!'
  print 'Create plot.sh file? (y/n): ',
  input=sys.stdin.readline().strip()
  if input=='y':
    create_plotsh()
    print 'File created!'
  else:
    print 'No file created!'
  sys.exit()

if glob.glob('jobrc.py')==[]:
  print 'JobWatch: jobrc.py File not found, using defaults!'
  print 'If template file is desired use keyword -tf'
  # Defaults:
  Linestyle = '-or'
  xLabel = 'Displacement'
  yLabel = 'Reaction Force'
else:
  usetempl = True
  execfile('jobrc.py')

if sys.argv[-1] == '-tf':
  create_rc()
  print 'File created!'
  sys.exit()

from subprocess import Popen, PIPE
import gobject
import numpy as np
import matplotlib
matplotlib.use('GTKAgg')

import matplotlib.pyplot as plt


def getout(cmd):
    p=Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr=p.communicate()
    if stdout=='': return stderr
    else: return stdout

def update():
    #p=Popen("plot.sh", stdout=PIPE, stderr=PIPE)
    #pline, err=p.communicate()
    pline=getout('plot.sh')
    line.set_xdata(pline.split()[::2])
    line.set_ydata(pline.split()[1::2])
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()
    if glob.glob('*.lck')==[]: 
      fig.canvas.set_window_title(titlename + os.getcwd()+' - Simulation Finished!')
    else:
      fig.canvas.set_window_title(titlename +os.getcwd()+' - Running...')
    ax2.cla()
    ax2.set_xticks([])
    ax2.set_yticks([])
    #statxt=getout('tail -9 *.sta')
    if glob.glob('*.sta')==[]:
      print titlename +'*.sta File does not exist. Waiting ...'
      return False
    stalength=int(getout('wc -l *.sta').split()[0])
    toptxt1=getout('head -1 *.sta')
    if stalength<13:
      statxt=getout('tail -'+str(stalength-5)+' *.sta')
    else:
      statxt=getout('tail -9 *.sta')
    toptxt=toptxt1 +' STEP  INC ATT SEVERE EQUIL TOTAL  TOTAL      STEP       INC OF       DOF    IF\n               DISCON ITERS ITERS  TIME/    TIME/LPF    TIME/LPF    MONITOR RIKS\n               ITERS               FREQ\n'+statxt
    ax2.text(0.03, 0.95, toptxt, fontsize=11, va='top', name='monospace')
    return True  # return False to terminate the updates


fig = plt.figure(1,(8,8))
ax = fig.add_axes([0.12,0.41,0.78,0.55])
#ax.set_ylim(0, 1)
line, = ax.plot([0],[0],Linestyle,lw=1.5)
ax.set_ylabel(yLabel)
ax.set_xlabel(xLabel)
ax.grid(True)
ax2 = fig.add_axes([0.01,0.01,0.98,0.34])
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_xlim((0,1))
ax2.set_ylim((0,1))
update()

gobject.timeout_add(10000, update)  # you can also use idle_add to update when gtk is idle
plt.show()


