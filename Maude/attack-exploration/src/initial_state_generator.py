import copy
import subprocess
import re
import random
import sys

from zone import Record, Zone
from config import Config
from actors import Resolver, Nameserver
from random_zone import get_random_zones
from conversion_utils import config_to_maude_file

CLIENT_ADDR = 'cAddr'
MAUDE_FILENAME = 'config.maude'
MAUDE_TIMEOUT = 60
MODEL_PARAMS = {
    'configTsuNAMEslistCircDep': True,
    # 'rsvMinCacheCredClient': 5,     # enable CNAME chain validation
    # 'rsvMinCacheCredResolver': 5,   # enable CNAME chain validation for resolver subqueries
    # 'maxMinimiseCount': 0,          # disable QNAME minimization
}

NUM_NODES_NEW_ZONE = 6

# Whether names from the base part of configuration should be used as targets for CNAME/DNAME/NS records
# (in addition to the names in the other new zones, which are always used)
USE_BASE_TARGET_NAMES = True

def test():
    config = get_benign_test_config()

    generate_initial_config_without_client(config, ['generated.com.'])
    print(invoke_maude_model_checker('[] ~ propRewriteBlackhole'))

def get_benign_test_config() -> Config:
    """
    Returns a "benign" configuration for testing purposes.
    """

    # root zone
    zoneRoot = Zone('', None,
        [
            # zone apex
            Record('', 'SOA', 3600, '3600'),
            Record('', 'NS', 3600, 'a.root-servers.net.'),

            # delegations and glue
            Record('a.root-servers.net.', 'A', 3600, 'addrNSroot'),
            Record('com.', 'NS', 3600, 'ns.com.'),
            Record('ns.com.', 'A', 3600, 'addrNScom'),
            Record('net.', 'NS', 3600, 'ns.net.'),
            Record('ns.net.', 'A', 3600, 'addrNSnet'),
        ])

    # com zone
    zoneCom = Zone('com.', zoneRoot,
        [
            Record('com.', 'SOA', 3600, '3600'),
            Record('com.', 'NS', 3600, 'ns.com.'),
            Record('ns.com.', 'A', 3600, 'addrNScom'),

            # delegations and glue
            Record('example.com.', 'NS', 3600, 'ns.example.com.'),
            Record('ns.example.com.', 'A', 3600, 'addrNSexample'),
        ])

    zoneNet = Zone('net.', zoneRoot,
        [
            Record('net.', 'SOA', 3600, '3600'),
            Record('net.', 'NS', 3600, 'ns.net.'),
            Record('ns.net.', 'A', 3600, 'addrNSnet'),

            # delegations and glue
            Record('root-servers.net.', 'NS', 3600, 'a.root-servers.net.'),
            Record('a.root-servers.net.', 'A', 3600, 'addrNSroot'),
        ])

    zoneRootServers = Zone('root-servers.net.', zoneNet,
        [
            Record('root-servers.net.', 'SOA', 3600, '3600'),
            Record('root-servers.net.', 'NS', 3600, 'a.root-servers.net.'),
            Record('a.root-servers.net.', 'A', 3600, 'addrNSroot'),
        ])

    # example.com zone
    zoneExample = Zone('example.com.', zoneCom,
        [ 
            Record('example.com.', 'SOA', 3600, '3600'),
            Record('example.com.', 'NS', 3600, 'ns.example.com.'),
            Record('ns.example.com.', 'A', 3600, 'addrNSexample'),
            Record('www.example.com.', 'A', 3600, '1.2.3.4'),
            Record('*.example.com.', 'TXT', 3600, '...'),
        ])

    resolver = Resolver('rAddr')

    nameserverRoot = Nameserver('addrNSroot', [zoneRoot, zoneRootServers])
    nameserverCom = Nameserver('addrNScom', [zoneCom])
    nameserverNet = Nameserver('addrNSnet', [zoneNet])
    nameserverExample = Nameserver('addrNSexample', [zoneExample])

    root_nameservers = {'a.root-servers.net.': 'addrNSroot'}

    return Config([], [resolver], [nameserverRoot, nameserverCom, nameserverNet, nameserverExample], root_nameservers)

def generate_initial_config_without_client(base_config: Config, new_zone_names):
    """
    Creates an initial configuration without a client query, by generating random zones and adding them
    to the given base configuration.
    The resulting configuration is written to a Maude file.
    """

    seed = random.randrange(sys.maxsize)
    random.seed(seed)
    print(f'Random seed is: {seed}\n')


    if USE_BASE_TARGET_NAMES:
        other_names = base_config.get_owner_names()
    else:
        other_names = []

    # create deepcopy of config s.t. modifications do not propagate to later iterations
    config_copy = copy.deepcopy(base_config)

    # find parent zones of attacker zones
    parent_zones = []
    for new_zone_name in new_zone_names:

        # find parent zone
        # TODO: this assumes that the new zones are exactly one level below the parent zone
        parent_zone_name = new_zone_name.split('.', maxsplit=1)[1]
        parent_zones.append(config_copy.find_zones(parent_zone_name)[0])

    # obtain random attacker zones and add them to config (add a new nameserver)
    new_zones = get_random_zones(new_zone_names, parent_zones, NUM_NODES_NEW_ZONE, other_names)

    new_ns_addrs = []
    for new_zone in new_zones:
        print(new_zone)
        new_ns_addrs += config_copy.add_nameservers_for_zone(new_zone, delay=0)

    # write config to Maude file
    config_to_maude_file(config_copy, MODEL_PARAMS, MAUDE_FILENAME, 'nondet-no-client')

def invoke_maude_model_checker(property: str):
    """
    Invokes the Maude LTL model checker for the given property, using the initConfigWithNonDetQuery operator
    to search the query space. Note that the config (without client) should already be in the Maude file at
    MAUDE_FILENAME.
    The property should be given in the Maude LTL syntax, e.g., '[] ~ propRewriteBlackhole'.
    Returns one of the following strings:
     - 'true' if no counterexample was found
     - 'counterexample (newline) command was: ...' if a counterexample was found
     - 'timeout'
     - 'parse_error' if something else went wrong
    """

    # invoke Maude on the file and get output
    cmd = ['maude', '-no-advise', '-no-banner', MAUDE_FILENAME]
    p = subprocess.Popen(cmd,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )

    model_check_command = f'red modelCheck(initConfigWithNonDetQuery(initConfigWithoutClient, rAddr, cAddr), {property}) .'

    timeout = False
    try:
        out_raw, err_raw = p.communicate(model_check_command.encode(), timeout=MAUDE_TIMEOUT)
    except subprocess.TimeoutExpired:
        timeout = True
        p.kill()
        out_raw, err_raw = p.communicate()

    out = out_raw.decode()
    err = err_raw.decode()

    if err:
        print(err)

    if timeout:
        return 'timeout'

    # parse results
    out = out.replace('\n', ' ')
    res_matches = re.findall(r'^.+ result (.+)', out, flags=re.MULTILINE)
    if len(res_matches) == 1:
        if res_matches[0].startswith('Bool: true'):
            return 'true'
        else:
            return f'counterexample\ncommand was: {model_check_command}\n'
    else:
        return 'parse_error'

if __name__ == '__main__':
    test()
