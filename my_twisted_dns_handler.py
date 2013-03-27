
#############################################################################
##
## Copyright 2013 Daniel Faust
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
## http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
#############################################################################


####################################################################################
#       i m p o r t s
####################################################################################

import os
import socket
import datetime
import collections

from twisted.internet   import defer
from twisted.names.root import Resolver
from twisted.names      import dns, error

####################################################################################
#       h e l p e r s
####################################################################################

def compile_dns_records(dns_records):
  
  dns_records = collections.OrderedDict(dns_records)
  
  # create the in-addr.arpa records. that's why it is an ordered dict: the first A record found for a domain will define the domain for the address.
  _inverted = []
  for key, value in dns_records.items():
    if dns.A in value:
      _entry = value[dns.A]['ans'][0]
      if _entry.TYPE == dns.A:
        _address = socket.inet_ntoa(_entry.address)
        if _address not in _inverted:
          _inverted.append(_address)
          dns_records[".".join(reversed(_address.split("."))) + ".in-addr.arpa"] = {dns.PTR: {'ans': [dns.Record_PTR(key, ttl=None),],},}
  
  return dns_records

####################################################################################
#       r e l o a d i n g   o f   d n s   r e c o r d s
####################################################################################

def _get_records(resolver):
  
  user_request_reload_dns_records = False
  
  if 'records' not in resolver.shared:
  
    print 'loading records'
    user_request_reload_dns_records = True
  
  if os.path.exists('do_reload_records'):
    print 'reloading records'
    user_request_reload_dns_records = True
  
  if user_request_reload_dns_records:
    print "executing file my_twisted_dns_records.py"
    locals = {}
    execfile('my_twisted_dns_records.py', {'dns': dns}, locals)
    resolver.shared['records'] = compile_dns_records(locals['my_dns_file_content'])
  
  return resolver.shared['records']
  
####################################################################################
#       q u e r y
####################################################################################

def query(self, query, address, timeout=None):
  name    = str(query.name)
  type    = query.type
  cls     = dns.IN
  records = _get_records(self)
  now = datetime.datetime.now()
  print now.strftime('%A %H:%M:%S') + ' -- ' + address[0] + ' -- ' + str(dns.QUERY_TYPES[type]) + ' ' + str(name)
  if name in records:
    def _query(query, servers, timeout, filter):
      name = str(query.name)
      if type in records[name]:
        record = records[name][type]
        answers, authority, additional = record['ans'], [], []
        if 'aut' in record: authority  = record['aut']
        if 'add' in record: additional = record['add']
        response = dns.Message()
        for (section, data) in [(response.answers, answers), (response.authority, authority), (response.additional, additional)]:
          section.extend([dns.RRHeader(name, record.TYPE, getattr(record, 'CLASS', dns.IN), payload=record, auth=True) for record in data])
        #print 'does exist'
        return defer.succeed(response)
      else:
        #print 'doesn't exist'
        return defer.fail(error.DNSQueryRefusedError(name))
    resolver = Resolver([])
    resolver._query = _query
    d = resolver._lookup(name, cls, type, timeout)
    def display(ans, auth, add):
      # print ans, auth, add
      return (ans, auth, add)
    d.addCallback(lambda (ans, auth, add): display(ans, auth, add))
    return d
  else:
    #print 'not in record'
    return self.upstream.queryUDP([dns.Query(name, type, cls)]).addCallback(_results_passthrough)

def _results_passthrough(message):
  # print message.answers, message.authority
  return defer.succeed((message.answers, message.authority, []))

####################################################################################
