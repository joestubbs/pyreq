#!/usr/bin/env python
# coding: utf-8

# In[9]:


get_ipython().system('pip install --user kubernetes')


# In[1]:


from kubernetes import client, config


# In[2]:


# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()


# In[ ]:




