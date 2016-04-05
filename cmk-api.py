#!/usr/bin/env python3
# A client for the check_mk / cmk API which is documented at https://mathias-kettner.de/checkmk_wato_webapi.html

import requests # http://docs.python-requests.org/en/master/
import json
import time
import yaml
import os
import sys
import logging
from subprocess import Popen, PIPE
from pprint import pprint
import re

def ReadConfig(configfile) :

    config = {}
    logging.debug('configfile %s', configfile)

    if not os.path.isfile(configfile):
        logging.critical("Configuration file %s not found.", configfile)
        exit(1)

    with open(configfile, 'r') as f:
        configfiledata = yaml.load(f)

    config["cmk_api_url"] = configfiledata.get('cmk_api_url')
    logging.debug('cmk_api_url=%s', config["cmk_api_url"])

    config["cmk_api_user"] = configfiledata.get('cmk_api_user')
    logging.debug('cmk_api_user=%s', config["cmk_api_user"])

    config["cmk_api_password"] = configfiledata.get('cmk_api_password')
    logging.debug('cmk_api_password=%s', config["cmk_api_password"])

    return config

def GetAllHosts(config) :
    url = config["cmk_api_url"] + "?action=get_all_hosts"
    response = requests.get(url, auth = (config["cmk_api_user"], config["cmk_api_password"]) )
    data=response.json()
    hosts = data['result'].keys()
    logging.info("Hosts %s", hosts)
    return hosts

def GetAllCmkAgentHosts(config) :
    url = config["cmk_api_url"] + "?action=get_all_hosts"
    response = requests.get(url, auth = (config["cmk_api_user"], config["cmk_api_password"]) )
    data=response.json()
    hosts = data['result'].keys()
    cmkHosts = []
    for host in hosts:
        if hasattr(data['result'][host]['attributes'], 'tag_agent') :
            tag_agent = json.dumps(data['result'][host]['attributes']['tag_agent'])
            if re.search("snmp|ping", tag_agent) :
                logging.debug("Skip host %s because of agent %s", host, tag_agent)
            else :
                logging.debug("Adding host %s while agent %s", host, tag_agent)
                cmkHosts.append(host)
        else :
            logging.debug("Adding host %s", host)
            cmkHosts.append(host)
    logging.info("cmkHosts %s", cmkHosts)
    return cmkHosts

def GetAllSnmpHosts(config) :
    url = config["cmk_api_url"] + "?action=get_all_hosts"
    response = requests.get(url, auth = (config["cmk_api_user"], config["cmk_api_password"]) )
    data=response.json()
    hosts = data['result'].keys()
    snmpHosts = []
    for host in hosts:
        if hasattr(data['result'][host]['attributes'], 'tag_agent') :
            tag_agent = json.dumps(data['result'][host]['attributes']['tag_agent'])
            if re.search("snmp", tag_agent) :
                logging.debug("Adding host %s because of agent %s", host, tag_agent)
                snmpHosts.append(host)
            else :
                logging.debug("Skip host %s because of agent %s", host, tag_agent)
        else :
            logging.debug("Skip host %s", host)
    logging.info("snmpHosts %s", snmpHosts)
    return snmpHosts

def DiscoverServices(config, host) :
    url = config["cmk_api_url"] + "?action=discover_services&mode=refresh"
    payload = 'request= { "hostname": "' + host + '" }'
    response = requests.post(url, auth=(config["cmk_api_user"], config["cmk_api_password"]), data=payload)
    response.raise_for_status()
    data=response.json()
    if data['result_code'] != 0 :
        logging.error("host %s result_code=%s %s", host, data['result_code'], data['result'])
        exit(1)
    logging.info(host + ": " + data['result'])

def ActivateChanges(config) :
    url = config["cmk_api_url"] + "?action=activate_changes"
    response = requests.get(url, auth=(config["cmk_api_user"], config["cmk_api_password"]))
    response.raise_for_status()
    data=response.json()
    if data['result_code'] != 0 :
        logging.error("host %s result_code=%s %s", host, data['result_code'], data['result'])
        exit(1)
    logging.debug(data['result'])
    logging.info("ActivateChanges: OK")

if __name__ == '__main__' :
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug level logging (default: info level)")
    parser.add_argument("--config", default='cmk-api-config.yaml', type=str, dest="config", help="Yaml config file (default: cmk-api-config.yaml)")
    parser.add_argument("--hosts", type=str, help="Comma separated list of hosts to work on")
    parser.add_argument("--allhosts", action="store_true", help="Work on all hosts")
    parser.add_argument("--allcmkhosts", action="store_true", help="Work on all hosts with agent type check_mk_agent")
    parser.add_argument("--allsnmphosts", action="store_true", help="Work on all hosts with agent type snmp")
    parser.add_argument("--discover", action="store_true", help="Discover services on hosts")
    parser.add_argument("--activate", action="store_true", help="Activate any pending changes")
    args = parser.parse_args()

    if args.debug:
        loglevel=logging.DEBUG
    else: 
        loglevel=logging.INFO
    logging.basicConfig(stream=sys.stderr, level=loglevel, format='%(asctime)s %(levelname)s %(message)s')

    config = ReadConfig(args.config)
    logging.debug("Config = %s", config)

    hosts = []

    if args.hosts:
        hosts = args.hosts.split(",")
        logging.info("Hosts %s", hosts)

    if args.allhosts:
        hosts = GetAllHosts(config)

    if args.allcmkhosts:
        hosts = GetAllCmkAgentHosts(config)

    if args.allsnmphosts:
        hosts = GetAllSnmpHosts(config)

    if args.discover:
        for host in hosts:
            DiscoverServices(config, host)

    if args.activate:
        ActivateChanges(config)

