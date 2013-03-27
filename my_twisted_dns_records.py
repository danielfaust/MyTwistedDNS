
my_dns_file_content = [
  ('example.com', {
    dns.SOA: {'ans': [dns.Record_SOA(mname='ns1.example.com', rname='postmaster.example.com', serial=20130327160456, refresh=3600, retry=3600, expire=3600, minimum=3600, ttl=None),],},
    dns.A:   {'ans': [dns.Record_A('127.0.0.1', ttl=None),],},
    dns.NS:  {'ans': [dns.Record_NS('ns1.example.com', ttl=None),],},
    dns.MX:  {'ans': [dns.Record_MX(0, 'mail.example.com', ttl=None),],},
  }),
  ('ns1.example.com',  { dns.NS: {'ans': [dns.Record_NS('127.0.0.2', ttl=None),],},}),
  ('www.example.com',  { dns.A:  {'ans': [dns.Record_CNAME('example.com', ttl=None),],},}),
  ('mail.example.com', { dns.A:  {'ans': [dns.Record_A('127.0.0.3', ttl=None),],},}),
  ('serv.example.com', { dns.A:  {'ans': [dns.Record_A('127.0.0.3', ttl=None),],},}),
  ('ftp.example.com',  { dns.A:  {'ans': [dns.Record_CNAME('serv.example.com', ttl=None),],},}),
]