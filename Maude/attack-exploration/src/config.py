from conversion_utils import name_to_maude
from zone import Zone, lookup
from actors import Nameserver, DelayedNameserver, Client

PATH_TO_PROJECT_DIR = '../../'

class Config:
    
    def __init__(self, clients, resolvers, nameservers, root_nameservers) -> None:
        self.clients = clients
        self.resolvers = resolvers
        self.nameservers = nameservers

        self.root_nameservers = root_nameservers

        self.monitor_address = 'mAddr'

    def add_client_with_queries(self, addr: str, queries, resolver=None):
        """
        Add a client with the given address and list of queries to the config.
        If resolver is not specified, the first resolver in the config is used.
        """

        if not resolver:
            resolver = self.resolvers[0]

        client = Client(addr, queries, resolver)
        self.clients.append(client)

    def add_nameservers_for_zone(self, zone: Zone, delay=0):
        """
        Adds the nameservers of a given zone to the configuration and adds the necessary delegations at the parent zone.
        Returns the addresses of the newly added nameservers.
        """

        # find zone's NS and glue records
        ns_records = lookup(zone.name, 'NS', zone.records)
        glue_records = []
        for ns_rec in ns_records:
            glue_records += lookup(ns_rec.rdata, 'A', zone.records)

        # add NS and glue records to parent zone
        zone.parent_zone.add_records(ns_records + glue_records)
        
        # create new nameserver for the zone
        addresses = []
        for glue_rec in glue_records:
            addr = glue_rec.rdata
            addresses.append(addr)
            if delay > 0:
                nameserver = DelayedNameserver(addr, [zone], delay)
            else:
                nameserver = Nameserver(addr, [zone])
            self.nameservers.append(nameserver)

        return addresses

    def find_zones(self, name: str):
        """
        Returns all zones with the given name present at any nameserver in the config.
        """

        zones = []
        for nameserver in self.nameservers:
            for zone in nameserver.zones:
                if zone.name == name:
                    zones.append(zone)
        return zones

    def get_records(self):
        """
        Returns all records present in any zone of any nameserver in the config.
        """

        records = []
        for nameserver in self.nameservers:
            for zone in nameserver.zones:
                records += zone.records
        return records

    def get_owner_names(self):
        """
        Returns the owner names of all records present in the configuration. The list does not contain duplicates.
        """

        names = map(lambda rec: rec.owner, self.get_records())
        return list(set(names))

    def to_maude_prob(self, param_dict) -> str:
        """
        Converts the configuration to a Maude representation for the probabilistic model.
        """

        res = '\n'.join((
                f'load {PATH_TO_PROJECT_DIR}src/probabilistic-model/dns',
                f'load {PATH_TO_PROJECT_DIR}src/probabilistic-model/sampler',
                f'load {PATH_TO_PROJECT_DIR}test/probabilistic-model/test_helpers',
                f'load {PATH_TO_PROJECT_DIR}src/probabilistic-model/properties',
                f'load {PATH_TO_PROJECT_DIR}attacker-models/probabilistic-model/attacker'

                '\n--- This maude file has been created automatically from the Python representation.\n',

                'mod TEST is\n',
                'inc SAMPLER + APMAUDE + DNS + TEST-HELPERS + PROPERTIES + ATTACKER .\n\n'
        ))

        res += self._to_maude_common_definitions(param_dict)

        res += '--- Initial configuration\n'
        res += 'op initConfig : -> Config .\n'
        res += 'eq initConfig = run(initState, limit) .\n\n'

        res += 'eq initState = { 0.0 | nil }\n'

        res += '  --- Start messages\n'
        for client in self.clients:
            res += f'  [id, to {client.address} : start, 0]\n'
        res += self._to_maude_actors()
        res += '  .\n\n'

        res += 'endm\n'
        
        return res

    def to_maude_nondet(self, param_dict) -> str:
        """
        Converts the configuration to a Maude representation for the non-deterministic model.
        """

        res = '\n'.join((
                f'load {PATH_TO_PROJECT_DIR}src/nondet-model/dns',
                f'load {PATH_TO_PROJECT_DIR}test/nondet-model/test_helpers',

                '\n--- This maude file has been created automatically from the Python representation.\n',

                'mod TEST is\n',
                'inc DNS + TEST-HELPERS .\n\n'
        ))

        res += self._to_maude_common_definitions(param_dict)

        res += '--- Initial configuration\n'
        res += 'op initConfig : -> Config .\n'
        res += 'eq initConfig =\n'
        res += '  --- Start messages\n'
        for client in self.clients:
            res += f'  (to {client.address} : start)\n'
        res += self._to_maude_actors()
        res += '  .\n\n'

        res += 'endm\n'
        
        return res

    def to_maude_nondet_no_client(self, param_dict) -> str:
        """
        Converts the configuration to a Maude representation for the non-deterministic model,
        with a non-deterministic query that is generated in Maude using rewrite rules.
        """

        res = '\n'.join((
                f'load {PATH_TO_PROJECT_DIR}src/nondet-model/dns',
                f'load {PATH_TO_PROJECT_DIR}test/nondet-model/test_helpers',
                f'load {PATH_TO_PROJECT_DIR}src/common/label_graph',
                f'load {PATH_TO_PROJECT_DIR}model-checking/preds',

                '\n--- This maude file has been created automatically from the Python representation.\n',

                'mod TEST is\n',
                'inc DNS + TEST-HELPERS + LABEL-GRAPH .\n',
                'pr DNS-PREDS .\n',
                'inc MODEL-CHECKER .\n',
                'inc LTL-SIMPLIFIER .\n\n',
        ))

        res += self._to_maude_common_definitions(param_dict)

        # the config does not contain the client actor, so we need to declare its address explicitly
        res += 'op cAddr : -> Address .\n'

        res += '--- Initial configuration\n'
        res += 'op initConfigWithoutClient : -> Config .\n'
        res += 'eq initConfigWithoutClient =\n'
        res += '  --- Start messages\n'
        res += f'  (to cAddr : start)\n'
        res += self._to_maude_actors()
        res += '  .\n\n'

        res += 'endm\n'
        
        return res

    def _to_maude_common_definitions(self, param_dict) -> str:
        res = 'eq monitorQueryLog? = true .\n\n'

        for param, val in param_dict.items():
            res += f'eq {param} = {str(val).lower()} .\n'

        res += '\n'

        res += self._get_addr_ops() + '\n'
        res += self._get_sbelt() + '\n'
        res += self._to_maude_zones()
        return res

    def _to_maude_zones(self) -> str:
        res = '--- Zone files\n'
        for zone in self._get_zones():
            res += zone.to_maude() + '\n\n'
        return res

    def _to_maude_actors(self) -> str:
        res = '  --- Monitor\n'
        res += f'  initMonitor({self.monitor_address})\n'

        res += '  --- Clients\n'
        for client in self.clients:
            res += '  ' + client.to_maude() + '\n'

        res += '  --- Resolvers\n'
        for resolver in self.resolvers:
            res += '  ' + resolver.to_maude() + '\n'

        res += '  --- Nameservers\n'
        for nameserver in self.nameservers:
            res += '  ' + nameserver.to_maude() + '\n'
        return res

    def _get_zones(self):
        """
        Returns all zones present in any name servers (without duplicates).
        """
        return set([zone for zonelist in map(lambda ns: ns.zones, self.nameservers) for zone in zonelist])

    def _get_actor_addresses(self):
        addrs = [self.monitor_address]
        for client in self.clients:
            addrs.append(client.address)
        for resolver in self.resolvers:
            addrs.append(resolver.address)
        for nameserver in self.nameservers:
            addrs.append(nameserver.address)
        return addrs
        
    def _get_addr_ops(self) -> str:
        res = '--- Actor addresses\n'
        res += f'ops ' + ' '.join(self._get_actor_addresses()) + ' : -> Address .\n'
        return res

    def _get_sbelt(self) -> str:
        res = '--- "SBELT": fallback if there are no known name servers\n'
        res += 'op sb : -> ZoneState .\n'
        
        res += 'eq sb = < root ('
        res += ', '.join(f'{name_to_maude(name)} |-> {self.root_nameservers[name]}' \
            for name in self.root_nameservers)
        res += ') > .\n'

        return res
