
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

#############################################################################

from twisted.internet     import defer, interfaces, reactor
from twisted.names        import client, common, dns, resolve, cache
from twisted.names.server import DNSServerFactory
from zope.interface       import implements

import os
import my_twisted_dns_handler

#############################################################################

'''
import sys
from twisted.python import log
log.startLogging(sys.stdout)
'''

#############################################################################

class CustomResolver(common.ResolverBase):
  implements(interfaces.IResolver)
  
  def __init__(self):
    common.ResolverBase.__init__(self)
    self.shared   = {}
    self.upstream = client.Resolver(servers=[("8.8.8.8", 53),])
  
  def query(self, *args):
    if os.path.exists('do_reload_handler'):
      print 'reloading handler'
      reload(my_twisted_dns_handler)
    return my_twisted_dns_handler.query(self, query=args[0], address=args[1])
    
#############################################################################

class MyDNSServerFactory(DNSServerFactory):
  
  def __init__(self):
    self.custom = CustomResolver()
    DNSServerFactory.__init__(self, authorities=None,
                                    #caches=[cache.CacheResolver()], behaves a bit strange on non-existing domains
                                    clients=[self.custom])
    
  def handleQuery(self, message, protocol, address):
    query = message.queries[0]
    # add the address to the query    vvvvvvv
    return self.resolver.query(query, address).addCallback(
        self.gotResolverResponse, protocol, message, address
    ).addErrback(
        self.gotResolverError, protocol, message, address
    )

#############################################################################

factory  = MyDNSServerFactory()
protocol = dns.DNSDatagramProtocol(factory)
reactor.listenTCP(53, factory, interface='0.0.0.0')
reactor.listenUDP(53, protocol, interface='0.0.0.0')
reactor.run()

#############################################################################

