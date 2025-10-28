#!/usr/bin/env python3

import sys
import dns.resolver
import multiprocessing 
import os 
import json
import ssl
from urllib.request import urlopen, HTTPError, URLError
import schedule
import time
import configparser
import datetime
import pprint
Curcent_key=0
from time import process_time
import threading

config = configparser.ConfigParser()
config.read('/etc/reflectorproxy.cfg')

import redis

#r = redis.Redis(
#    host=config['REDIS']['HOST'], port=config['REDIS']['PORT'],
#    username=config['REDIS']['USER'], # use your Redis user. More info https://redis.io/docs/management/security/acl/
#    password=config['REDIS']['PASSWORD'], # use your Redis password
#)

r = redis.Redis(host=config['REDIS']['HOST'], port=config['REDIS']['PORT'], decode_responses=True,password=config['REDIS']['PASSWORD'])

old_jsondata =""

#server urls
Servers =[]
#srver_nodes connected
Server_nodes = []

# Get json from all reflector nodes to build big node
def worker1(url,mode,return_dict,server_id): 
    # printing process id 
#    print("ID of process running worker1: {}".format(os.getpid())) 
    try:
      ctx = ssl.create_default_context()
      ctx.check_hostname = False
      ctx.verify_mode = ssl.CERT_NONE
      start = datetime.datetime.now()
      if mode == 1:
        json_url = urlopen('http://'+url+'/status',timeout=0.5)
      elif mode == 3:
        json_url = urlopen('http://'+url+'/reflector_proxy',timeout=0.3)
      else:
        json_url = urlopen('https://'+url+'/reflector_proxy',timeout=0.2,context=ctx)
      data = json.loads(json_url.read())
      end = datetime.datetime.now()
#      print(mode)
#      print(data.items())
      for nodes in data["nodes"]:
#        data["nodes"][nodes]["Reflector"] = url
        data["nodes"][nodes]["Reflector"]  = server_id[url]
    #  prints responces data for debug
    #data['proxyData'] = {}
    #data['proxyData']['ServerResponce'] = {}
    #data["proxyData"]['ServerResponce'][url] =  str((end - start))
    #print(data["proxyData"]['ServerResponce'][url])

      return_dict[url] = json.dumps(data)
    except:
      1+1
# Worker checks for  nr of nodes on reflector

def worker2(url,return_dict,server_id):


   global  json_url
   print(url)
   #try:
   if url != "":
     ctx = ssl.create_default_context()
     ctx.check_hostname = False
     ctx.verify_mode = ssl.CERT_NONE
     try:
       print("host " + url)
       start = datetime.datetime.now()
       json_url = urlopen('https://'+url+'/reflector_proxy',timeout=2,context=ctx)
       end = datetime.datetime.now()
       data = json.loads(json_url.read())
       nodes =  {}
       nodes['Len'] = (len(data['nodes']))
       nodes['Mode'] =2
       nodes['Response'] =  end -start
       nodes['id'] =server_id[url]  
       return_dict[str(url)] = nodes


#     except HTTPError as e:
#       print('HTTP Error code: ')
#     except URLError as e:
     except:
        try:
          start = datetime.datetime.now()
          json_url = urlopen('http://'+url+'/status',timeout=2,context=ctx)
          end = datetime.datetime.now()
          data = json.loads(json_url.read())
          nodes =  {}
          nodes['Len'] = (len(data['nodes']))
          nodes['Mode'] =1
          nodes['Response'] = end- start  
          nodes['id'] =server_id[url]

          return_dict[str(url)] = nodes
 #       except URLError as e:
        except: 
          try:
            start = datetime.datetime.now()
            json_url = urlopen('http://'+url+'/reflector_proxy',timeout=2,context=ctx)
            end = datetime.datetime.now()
            data = json.loads(json_url.read())
            nodes =  {}
            nodes['Len'] = (len(data['nodes']))
            nodes['Mode'] =3
            nodes['Response'] = end- start
            nodes['id'] =server_id[url]

            return_dict[str(url)] = nodes
#          except HTTPError as e:
#            print('HTTP Error code: 3 ')
          except:
            1+1




 #    except: 
 #      1+1

manager_server = multiprocessing.Manager()
return_dict_sever = manager_server.dict()




def Get_nr_of_nodes_refltors():
  global server_id
  for srv in Servers:
    # creating processes
    p = multiprocessing.Process(target=worker2,args=[str(srv),return_dict_sever,server_id])
    # starting processes
    p.start()
    # wait until processes are finished
    #p.join()



def create_status():
  # status page
  status_json = {}
  for srv in Servers:
    try:
      status_json[srv] = {}
      status_json[srv]['Mode'] =str(return_dict_sever[srv]['Mode'])
      status_json[srv]['Response'] =str(return_dict_sever[srv]['Response'])
      status_json[srv]['NrOfNodes'] =str(return_dict_sever[srv]['Len'])
    except:
      1+1
  r.set('PORTAL_PORXY_JSON_STATUS',json.dumps(status_json))


manager = multiprocessing.Manager()
return_dict = manager.dict()
p={}


def get_json_data_from_active_reflectors():
  global  old_jsondata
  global  return_dict
  global  server_id
  global  p
#¤  manager = multiprocessing.Manager()
#  return_dict = manager.dict()
  for srv in Servers:
    # creating processes

    try:
      if return_dict_sever[srv]['Len'] >0:

#         print(srv)
#         print(return_dict_sever[srv]['Len']) 
#         print(return_dict_sever[srv]['Mode'])
         try:
           if p[srv].is_alive() == False:
             p[srv] = multiprocessing.Process(target=worker1,args=[str(srv),return_dict_sever[srv]['Mode'],return_dict,server_id])
             # starting processes
             p[srv].start()


         except:
           p[srv] = multiprocessing.Process(target=worker1,args=[str(srv),return_dict_sever[srv]['Mode'],return_dict,server_id])
           # starting processes
           p[srv].start()
        # wait until processes are finished
        #p.join()
    except:
      1+1
      #print("No data to get colleted from node")

  # wait until processes are finished
#  for srv in Servers:
#    try:
#      p[srv].join()
#    except:
#      1+1


  data_out  ={}
  data_out['nodes'] = {}


  for server_merge in return_dict.values():
    data = json.loads(server_merge)
    data_out['nodes'] = {**data_out['nodes'], **data['nodes']}

  data_out['proxyData'] = {}
  data_out['proxyData']['Verson'] = "1.0"
  data_out['proxyData']['Protocol'] = "LONG,JSON,MQTT"
  data_out['proxyData']['Reflectors'] = {}
  for srv in Servers:
    # creating processes
    try:
      data_out['proxyData']['Reflectors'][srv] = {}
      data_out['proxyData']['Reflectors'][srv]['len'] = return_dict_sever[srv]['Len']
      data_out['proxyData']['Reflectors'][srv]['id'] = return_dict_sever[srv]['id']
    except:
      1+1





 # print("prosess:")
 # print(time.localtime().tm_sec)
  json_out =json.dumps(data_out, sort_keys=True) 
  # if data has changed sens e previus run do update tasks
  Outdata_to_redis(json_out)


def Get_srv_reflektor(url):

  answers = dns.resolver.resolve('_svxreflector._tcp.'+url,'SRV')
  for rdata in answers:
    rdata1  =str(rdata)
    x = rdata1.split(' ')
    Servers.append(x[3])

# if data has changed sens e previus run do update cache db
def Outdata_to_redis(json_out):
  global  old_jsondata
  global  Curcent_key
  if json_out != old_jsondata :

#    print("prosess:")
#    print(time.localtime().tm_sec)
    #print(json_out)
    Curcent_key = Curcent_key+1
    #SEND TO REDIS
    r.set('PORTAL_PORXY_JSON_CURRENT',json_out)
    r.set('PORTAL_PORXY_JSON_CURRENT_KEY',str(Curcent_key))
    r.publish('PORTAL_PORXY_JSON_CURRENT_KEY_LIVE',Curcent_key)
    r.publish('PORTAL_PORXY_JSON_LIVE',json_out)
  #print(Curcent_key) 
  #r.set('PORTAL_PROXY_JSON_KEY_' + str(Curcent_key-1), old_jsondata, ex=300)
    old_jsondata = json_out




try:
  if config['GLOBAL']['HOSTS'] !="":
     #print (config['GLOBAL']['HOSTS'])
     cofig_host= config['GLOBAL']['HOSTS']
     aditional_ = cofig_host.split(',')
     for serv in aditional_:
       print(serv)
       Servers.append(serv)
except: 
  1+1


Get_srv_reflektor(config['GLOBAL']['DNS_DOMAIN']);

print("Serverlist")
print(Servers)

server_id = {}
integer = 0
for srv in Servers:
  try:
    server_id[srv] = integer
    integer = integer +1
  except:
    integer = integer +1





#Get_nr_of_nodes_refltors()
#get_json_data_from_active_reflectors()

Get_nr_of_nodes_refltors()

schedule.every(30).seconds.do(Get_nr_of_nodes_refltors)
schedule.every(60).seconds.do(create_status)
schedule.every(0.2).seconds.do(get_json_data_from_active_reflectors)





while True:
    schedule.run_pending()
    time.sleep(0.1)
#    get_json_data_from_active_reflectors()


#data_out  ={}

#for server_merge in return_dict.values():
#  print (server_merge)
#   data = json.loads(server_merge)
#   data_out = {**data_out, **data}

#  data_out['nodes'].append(server_merge['nodes'])
#employee_list = {'employee_records':[]}

#data_out['proxyData'] = {}
#data_out['proxyData']['Verson'] = "1.0"
#data_out['proxyData']['Protocol'] = "LONG,JSON,MQTT"


#print(json.dumps(data_out))
#print(len(data_out))
