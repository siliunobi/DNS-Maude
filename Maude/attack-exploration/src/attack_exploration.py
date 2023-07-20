import copy
import datetime
import shutil
import subprocess
import re
import random
import sys

from zone import Record, Zone
from config import Config
from actors import Resolver, Nameserver
from random_zone import get_random_zones
from groot_ec import get_ec_queries
from conversion_utils import config_to_maude_file

CLIENT_ADDR = 'cAddr'
MAUDE_FILENAME = 'config.maude'
MAUDE_TIMEOUT = 20
MODEL_PARAMS = {
    'configTsuNAMEslistCircDep': True,
    'rsvTimeout?': True,
    'rsvTimeout': '100.0',
    'dropMsgsForNXActors?': True,
    # 'rsvMinCacheCredClient': 5,     # enable CNAME chain validation
    # 'rsvMinCacheCredResolver': 5,   # enable CNAME chain validation for resolver subqueries
    # 'maxMinimiseCount': 0,          # disable QNAME minimization
}

NUM_NODES_ATTACKER_ZONE = 6

# Whether names from the benign part of configuration should be used as targets for CNAME/DNAME/NS records
# (in addition to the names in the other attacker zones, which are always used)
USE_BENIGN_TARGET_NAMES = True

def test():
    config = get_benign_test_config()

    random_zones_threshold(config, ['attacker1.com.', 'attacker2.net.'], ['A'], 1, 20.0, 10, 'paf', victim_addrs=['rAddr'], paf_only_attacker_client=True)
    # random_zones_threshold(config, ['attacker1.com.'], ['A'], 1, 10.0, 10, 'paf', victim_addrs=['rAddr'], paf_only_attacker_client=True)
    # random_zones_threshold(config, ['attacker1.com.', 'attacker2.net.'], ['A'], 1, 250.0, 10, 'max_duration', delay=50.0)
    # random_zones_threshold(config, ['attacker1.com.'], ['A'], 1, 250.0, 10, 'max_duration', delay=50.0)

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

def random_zones_threshold(config: Config, attacker_zone_names, types, num_symbolic_labels,
    thresh, num_trials, metric, **kwargs):
    """
    Generates num_trials configurations, consisting of the given config and random attacker zones.
    Executes the model for each configuration and query equivalence class and determines for each execution whether the
    specified metric exceeded the given threshold.
    The metric can be one of:
      * paf: packet amplification factor
        required kwargs:
            'victim_addrs'
            'paf_only_attacker_client': Consider only the client (but not the nameservers) of the attacker for the
                amplification factor
      * max_duration: max query duration at the resolver
        required kwargs:
            'delay'
    """

    seed = random.randrange(sys.maxsize)
    random.seed(seed)
    print(f'Random seed is: {seed}\n')


    if USE_BENIGN_TARGET_NAMES:
        other_names = config.get_owner_names()
    else:
        other_names = []

    total_gt_thresh = 0
    total_failed = 0
    total_timeout = 0

    for _ in range(num_trials):
        # create deepcopy of config s.t. modifications do not propagate to later iterations
        config_copy = copy.deepcopy(config)

        # find parent zones of attacker zones
        parent_zones = []
        for attacker_zone_name in attacker_zone_names:

            # find parent zone of attacker zone
            # TODO: this assumes that the attacker zones are exactly one level below the parent zone
            parent_zone_name = attacker_zone_name.split('.', maxsplit=1)[1]
            parent_zones.append(config_copy.find_zones(parent_zone_name)[0])

        # obtain random attacker zones and add them to config (add a new nameserver)
        attacker_zones = get_random_zones(attacker_zone_names, parent_zones, NUM_NODES_ATTACKER_ZONE, other_names)

        if metric == 'paf':
            attacker_ns_addrs = []
            for attacker_zone in attacker_zones:
                print(attacker_zone)
                attacker_ns_addrs += config_copy.add_nameservers_for_zone(attacker_zone)

            # assemble the Maude rewrite command
            if kwargs['paf_only_attacker_client']:
                attacker_addrs = [CLIENT_ADDR]
            else:
                attacker_addrs = [CLIENT_ADDR] + attacker_ns_addrs

            attacker_addrs_maude = ' ; '.join(attacker_addrs)
            victim_addrs_maude = ' ; '.join(kwargs['victim_addrs'])
            maude_command = f'rew msgAmpFactor({attacker_addrs_maude}, {victim_addrs_maude}, initConfig) .\n'

        elif metric == 'max_duration':
            attacker_ns_addrs = []
            for attacker_zone in attacker_zones:
                print(attacker_zone)
                attacker_ns_addrs += config_copy.add_nameservers_for_zone(attacker_zone, delay=kwargs['delay'])

            # the Maude rewrite command
            maude_command = 'rew maxQueryDuration(initConfig) .\n'

        else:
            # invalid metric
            print(f'Invalid metric: {metric}')
            return

        # simulate execution for each equivalence class
        num_gt_thresh, num_failed, num_timeout = invoke_maude_ECs_threshold(config_copy, types,
            num_symbolic_labels, maude_command, thresh, metric)

        total_gt_thresh += num_gt_thresh
        total_failed += num_failed
        total_timeout += num_timeout

    print('\n\n=======================')
    print(f'Overall results for {metric}:')
    print(f'{total_gt_thresh} exceed threshold')
    print(f'{total_failed} FAILED')
    print(f'{total_timeout} TIMED OUT')
    print('=======================')

def invoke_maude_ECs_threshold(config: Config, types, num_symbolic_labels, maude_command, thresh, metric):
    """
    Generates the equivalence classes for the given config and invokes maude for each EC.
    Determines whether the result value exceeded the given threshold. If this is the case, or if the
    model got stuck, the Maude file is stored for later inspection.
    Returns a tuple consisting of the number of queries that achieved a result value > threshold, the number of failed
    queries, and number of timed out queries.
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')

    queries = get_ec_queries(config.get_records(), types, num_symbolic_labels)

    print('\n=======================')
    print(f'\n{len(queries)} query ECs')

    values_gt_thresh = []
    queries_gt_thresh = []
    queries_failed = []
    queries_timeout = []
    num_gt_thresh = 0
    num_failed = 0
    num_timeout = 0

    for query in queries:
        # create a deepcopy of the config, then add client with query
        config_with_query = copy.deepcopy(config)
        config_with_query.add_client_with_queries(CLIENT_ADDR, [query], None)

        result_str = invoke_maude_with_command(config_with_query, maude_command)

        if result_str == 'timeout':
            queries_timeout.append(query)
            num_timeout += 1
            print('T', end='', flush=True)

            # store maude file for later inspection
            dst_filename = f'../failure_configs/{timestamp}_timeout_{num_timeout}.maude'
            shutil.copy(MAUDE_FILENAME, dst_filename)

        elif result_str == 'parse_error':
            queries_failed.append(query)
            num_failed += 1
            print('F', end='', flush=True)

            # store maude file for later inspection
            dst_filename = f'../failure_configs/{timestamp}_failure_{num_failed}.maude'
            shutil.copy(MAUDE_FILENAME, dst_filename)

        else:
            # no error
            value = float(result_str)
            if value > thresh:
                values_gt_thresh.append(value)
                queries_gt_thresh.append(query)
                num_gt_thresh += 1
                print('X', end='', flush=True)

                # store maude file for later inspection
                dst_filename = f'../success_configs/{timestamp}_{num_gt_thresh}_{metric}_{value}.maude'
                shutil.copy(MAUDE_FILENAME, dst_filename)

            else:
                print('.', end='', flush=True) # simple progress indicator

    if num_gt_thresh:
        print('\nsuccessful queries:')
        for f, q in zip(values_gt_thresh, queries_gt_thresh):
            print(f'{f} with {q}')

    if num_failed:
        print(f'\nfailed queries:')
        for q in queries_failed:
            print(q)

    if num_timeout:
        print(f'\ntimed out queries:')
        for q in queries_timeout:
            print(q)

    print('\n=======================')

    return num_gt_thresh, num_failed, num_timeout

def invoke_maude_with_command(config: Config, maude_command: str):
    """
    Performs a single execution of the probabilistic Maude model for the given command.
    Returns the (real-valued) result, or the strings 'parse_error' or 'timeout', as applicable.
    """

    config_to_maude_file(config, MODEL_PARAMS, MAUDE_FILENAME, 'probabilistic')
    # config_to_maude_file(config, filename, 'nondet')

    # invoke Maude on the file and get output
    cmd = ['maude.linux64', '-no-advise', '-no-banner', MAUDE_FILENAME]
    p = subprocess.Popen(cmd,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )

    timeout = False
    try:
        out_raw, err_raw = p.communicate(maude_command.encode(), timeout=MAUDE_TIMEOUT)
    except subprocess.TimeoutExpired:
        timeout = True
        p.kill()
        out_raw, err_raw = p.communicate()

    out = out_raw.decode()
    err = err_raw.decode()

    # print(out)
    if err:
        print(err)

    if timeout:
        return 'timeout'

    # parse results
    res_matches = re.findall(r'^result FiniteFloat: (.+)', out, flags=re.MULTILINE)
    if len(res_matches) == 1:
        return res_matches[0]
    else:
        return 'parse_error'

if __name__ == '__main__':
    test()
