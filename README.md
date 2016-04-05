cmk-api-client
==============

A client for the Check_MK / CMK web api.


Dependencies
------------

You'll need a python3 interpreter and the following libraries:

 - [PyYAML](https://bitbucket.org/xi/pyyaml) (`pip install pyyaml`)
 - [Requests](http://docs.python-requests.org/en/latest/) (`pip install requests`)


Usage
-----

First copy `cmk-api-config.yaml.template` file to `cmk-api-config.yaml` and
fill in your CMK API URL (the URL ends with /webapi.py) as well as your API
user name and secret.

Then run the script as follows :

    usage: cmk-api.py [-h] [--debug] [--config CONFIG] [--hosts HOSTS]
                      [--allhosts] [--allcmkhosts] [--allsnmphosts] [--discover]
                      [--activate]

    optional arguments:
      -h, --help       show this help message and exit
      --debug          Enable debug level logging (default: info level)
      --config CONFIG  Yaml config file (default: cmk-api-config.yaml)
      --hosts HOSTS    Comma separated list of hosts to work on
      --allhosts       Work on all hosts
      --allcmkhosts    Work on all hosts with agent type check_mk_agent
      --allsnmphosts   Work on all hosts with agent type snmp
      --discover       Discover services on hosts
      --activate       Activate any pending changes

Examples
--------

    ./cmk-api.py --allcmkhosts --discover --activate
    ./cmk-api.py --hosts host1,host2,host3 --discover --activate

