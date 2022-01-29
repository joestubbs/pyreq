#!/usr/bin/env python
# coding: utf-8

# # Free Field Analysis Example
# Pedro Arduino - UW Computational Geomechanics Group

# This example shows how to run OpenSees in DesignSafe from a jupyter notebook and how to postprocess the output results using python scripts, generate a LaTex report, and create interactive plots. 
# 
# A simple 1D free field analysis of a liquefiable soil layer is analyzed using OpenSees. An schematic of the soil profile in shown in the Figure. The soil profile consists of a 10 m liquefiable layer underlained by 20 m of dense material. The ground water table is at 2 m. An earthquake excitation is applied at the bottom of the soil column. A complyant rock is considered in the analysis. 
# 
# The results are presented in terms of:
# 
# a) Time history of acceleration at the surface and corresponding response spectra.
# 
# b) Profiles of maximum displacement, PGA, maximum shear strain, and stress ratio
# 
# c) Stress strain plots for a point near the center of the liquefiable zone, and
# 
# d) Evolution of pore water pressure for a point near the center of the liquefiable zone. 

# <img src = "schematic.png"  height="200" width="200" align = "center">

# # Setup agave and start OpenSees job

# ### Setup job description

# In[1]:


from agavepy.agave import Agave
ag = Agave.restore()
import os

app_name = 'OpenSees'
app_id = 'opensees-docker-2.5.0.6248u11'
storage_id = 'designsafe.storage.default'

control_batchQueue = 'debug'
control_jobname = 'opensees-ex'
control_nodenumber = '1'
control_processorsnumber = '1'
control_memorypernode = '1'
control_maxRunTime = '00:30:00'

cur_dir = os.getcwd()
if ('jupyter/MyData' in cur_dir ):
    cur_dir = cur_dir.split('MyData').pop() 
    storage_id = 'designsafe.storage.default'
    input_dir = ag.profiles.get()['username']+ cur_dir
    input_uri = 'agave://{}/{}'.format(storage_id,input_dir)
    input_uri = input_uri.replace(" ","%20")
elif('jupyter/mydata' in cur_dir ):
    cur_dir = cur_dir.split('mydata').pop()
    storage_id = 'designsafe.storage.default'
    input_dir = ag.profiles.get()['username']+ cur_dir
    input_uri = 'agave://{}/{}'.format(storage_id,input_dir)
    input_uri = input_uri.replace(" ","%20")
elif('jupyter/MyProjects' in cur_dir):
    cur_dir = cur_dir.split('MyProjects/').pop()
    PRJ = cur_dir.split('/')[0]
    qq = {"value.projectId": str(PRJ)}
    cur_dir = cur_dir.split(PRJ).pop()
    project_uuid = ag.meta.listMetadata(q=str(qq))[0]["uuid"]
    input_dir = cur_dir
    input_uri = 'agave://project-{}{}'.format(project_uuid,cur_dir)
    input_uri = input_uri.replace(" ","%20")
elif('jupyter/CommunityData' in cur_dir):
    cur_dir = cur_dir.split('jupyter/CommunityData').pop() 
    input_dir = cur_dir
    input_uri = 'agave://designsafe.storage.community/{}'.format(input_dir)
    input_uri = input_uri.replace(" ","%20")    

input_filename = 'freeFieldEffective.tcl'
inputs = {"inputDirectory": [ input_uri ]}
parameters = {"inputScript" : [input_filename]}

app = ag.apps.get(appId=app_id)
job_description = {}
job_description["name"] = (control_jobname)
job_description["appId"] = (app_id)
job_description["batchQueue"] = (control_batchQueue)
job_description["nodeCount"] = int(control_nodenumber)
job_description["processorsPerNode"] = int(control_processorsnumber)
job_description["memoryPerNode"] = (control_memorypernode)
job_description["maxRunTime"] = control_maxRunTime
job_description["archive"] = True
job_description["inputs"] = inputs
job_description["parameters"] = parameters


# ### Run job

# In[2]:


job = ag.jobs.submit(body=job_description)
from agavepy.async import AgaveAsyncResponse
asrp = AgaveAsyncResponse(ag, job)
asrp.result()


# # Postprocess Results

# ### Go to archived folder

# In[3]:


jobinfo = ag.jobs.get(jobId=job.id)


# In[4]:


jobinfo.archivePath


# In[5]:


user = jobinfo.archivePath.split('/', 1)[0]


# In[6]:


import os


# In[7]:


get_ipython().run_line_magic('cd', '..')


# In[8]:


os.chdir(jobinfo.archivePath.replace(user,'/home/jupyter/MyData'))


# In[9]:


cur_dir_name = cur_dir.split('/').pop() 


# In[10]:


if not os.path.exists(cur_dir_name):
    os.makedirs(cur_dir_name)


# In[11]:


os.chdir(cur_dir_name)


# In[12]:


cur_dir_name


# ### Import python libraries

# In[13]:


get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import matplotlib.pyplot as plt


# ### Plot acceleration time history

# Plot acceleration time hisotory and response spectra on log-linear scale

# In[14]:


from plotAcc import plot_acc
plot_acc()


# ### Plot profiles

# Plot profiles of max displacement, PGA, max shear strain, stress ratio and plot stress strain near the center of liquefiable layer 

# In[15]:


from plotProfile import plot_profile
plot_profile()


# ### Plot excess pore water pressure

# In[16]:


from plotPorepressure import plot_porepressure
plot_porepressure()


# # Generate LaTeX Report 

# In[17]:


os.system('/usr/bin/pdflatex -interaction nonstopmode ShortReport.tex')


# In[18]:


class PDF(object):
  def __init__(self, pdf, size=(200,200)):
    self.pdf = pdf
    self.size = size

  def _repr_html_(self):
    return '<iframe src={0} width={1[0]} height={1[1]}></iframe>'.format(self.pdf, self.size)

  def _repr_latex_(self):
    return r'\includegraphics[width=1.0\textwidth]{{{0}}}'.format(self.pdf)


# In[19]:


pdf_fn = jobinfo.archivePath.replace(user, '/user/' + user + '/files/MyData')
pdf_fn += '/'
pdf_fn += cur_dir.split('/')[-1]
pdf_fn += '/ShortReport.pdf'
print pdf_fn


# In[20]:


PDF(pdf_fn , (750,600))


# # Create Interactive Plots

# ### Pore water pressure

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
from matplotlib import gridspec
from ipywidgets import  interactive
import ipywidgets as widgets
import numpy as np


# In[ ]:


pwp = np.loadtxt('porePressure.out')


# In[ ]:


time = pwp[:,0]
pwp = np.delete(pwp, 0, 1)
uexcess = pwp - pwp[0, :]
uu = uexcess[0:len(time), 97]


# In[ ]:


nodes = np.loadtxt('nodesInfo.dat')
disp = np.loadtxt('displacement.out')
disp = np.delete(disp, 0, 1)
disp = (disp.transpose() - disp[:,0]).transpose()


# In[ ]:


acc = np.loadtxt('acceleration.out')
acc_input = acc[:,1]


# In[ ]:


ndof = 2
nnodes = nodes.shape[0]
maxdisp = np.amax(disp, axis=0)
mindisp = np.amin(disp, axis=0)
maxdisp = maxdisp.reshape(ndof, nnodes, order="F")
mindisp = mindisp.reshape(ndof, nnodes, order="F")


# In[ ]:


def pwpplot(timeStep):
    Step = int(timeStep / 0.01)-1;
    plt.subplot(211)
    plt.plot(time, uu)
    plt.plot(time[Step],uu[Step],'ro')
    plt.ylabel('pwp(kPa)')
    plt.grid()
    plt.subplot(212)
    plt.plot(time,acc_input)
    plt.plot(time[Step],acc_input[Step],'ro')
    plt.xlabel('time(s)')
    plt.ylabel('acceleration(g)')
    plt.grid()


# In[ ]:


interactive(pwpplot,timeStep = widgets.FloatSlider(min = 0.01, max = time[-1], step = 0.01))


# ### Displacement

# In[ ]:


gs = gridspec.GridSpec(2, 1, height_ratios=[6, 1]) 


# In[ ]:


def dispplot(timeStep):
    Step = int(timeStep / 0.01)-1;
    plt.figure(figsize=(7, 8))
    ax0 = plt.subplot(gs[0])
    ax0.plot(maxdisp[0, ::2], nodes[::2, 2], 'b--')
    ax0.plot(mindisp[0, ::2], nodes[::2, 2], 'b--')
    ax0.plot(disp[Step, ::4], nodes[::2, 2])
    plt.xlabel('displacement(m)')
    plt.ylabel('Elevation(m)')
    plt.grid()
    ax1 = plt.subplot(gs[1])
    ax1.plot(time,acc_input)
    ax1.plot(time[Step],acc_input[Step],'ro')
    plt.xlabel('time(s)')
    plt.ylabel('acceleration(g)')
    plt.grid()


# In[ ]:


interactive(dispplot,timeStep = widgets.FloatSlider(min = 0.01, max = time[-1], step = 0.01), continuous_update=False)


# In[ ]:





