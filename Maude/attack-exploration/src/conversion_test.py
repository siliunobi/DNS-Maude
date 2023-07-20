import subprocess

from zone import Zone, Record
from actors import Resolver, Client, Nameserver
from config import Config
from query import Query
from conversion_utils import config_to_maude_file

def go():

    # root zone
    zoneRoot = Zone('', None,
        [
            # zone apex
            Record('', 'SOA', 3600, '...'),
            Record('', 'NS', 3600, 'a.root-servers.net.'),

            # delegations and glue
            Record('a.root-servers.net.', 'A', 3600, 'addrNSroot'),
            Record('com.', 'NS', 3600, 'ns.com.'),
            Record('ns.com.', 'A', 3600, 'addrNScom'),
        ])

    # com zone
    zoneCom = Zone('com.', zoneRoot,
        [
            Record('com.', 'SOA', 3600, '...'),
            Record('com.', 'NS', 3600, 'ns.com.'),
            Record('ns.com.', 'A', 3600, 'addrNScom'),

            # delegations and glue
            Record('example.com.', 'NS', 3600, 'ns.example.com.'),
            Record('ns.example.com.', 'A', 3600, 'addrNSexample'),
        ])

    # example.com zone
    zoneExample = Zone('example.com.', zoneCom,
        [ 
            Record('example.com.', 'SOA', 3600, '...'),
            Record('example.com.', 'NS', 3600, 'ns.example.com.'),
            Record('ns.example.com.', 'A', 3600, 'addrNSexample'),
            Record('www.example.com.', 'A', 3600, '1.2.3.4'),
        ])

    resolver = Resolver('rAddr')

    query = Query(1, 'www.example.com.', 'A')
    client = Client('cAddr', [query], resolver)

    nameserverRoot = Nameserver('addrNSroot', [zoneRoot])
    nameserverCom = Nameserver('addrNScom', [zoneCom])
    nameserverExample = Nameserver('addrNSexample', [zoneExample])

    root_nameservers = {'a.root-servers.net.': 'addrNSroot'}

    config = Config([client], [resolver], [nameserverRoot, nameserverCom, nameserverExample], root_nameservers)
    # print(config.to_maude_prob())
    # print(config.to_maude_nondet())

    filename = 'config.maude'
    config_to_maude_file(config, filename, 'probabilistic')
    # config_to_maude_file(config, filename, 'nondet')

    # Invoke Maude on the file and get output
    cmd = ['maude', '-no-advise', '-no-banner', filename]
    p = subprocess.Popen(cmd,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    out_raw, err_raw = p.communicate(b"rew initConfig .\n")
    out = out_raw.decode()
    err = err_raw.decode()

    print(out)

if __name__ == '__main__':
    go()

