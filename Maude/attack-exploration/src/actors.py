from conversion_utils import address_to_maude, querylist_to_maude

class Client:

    def __init__(self, address, queries, resolver) -> None:
        self.address = address
        self.queries = queries
        self.resolver = resolver

    def __str__(self) -> str:
        return f'< {self.address} : Client | queries: {self.queries}, resolver: {self.resolver.address}, ... >'

    def to_maude(self) -> str:
        res = f'< {address_to_maude(self.address)} : Client |\n'
        res += f'    queries: {querylist_to_maude(self.queries)},\n'
        res += f'    resolver: {address_to_maude(self.resolver.address)},\n'
        res += f'    notifyDone: nullAddr >'
        return res

class Resolver:

    def __init__(self, address) -> None:
        self.address = address

    def __str__(self) -> str:
        return f'< {self.address} : Resolver | ... >'

    def to_maude(self) -> str:
        res = f'< {address_to_maude(self.address)} : Resolver |\n'
        res += f'    cache: nilCache,\n'
        res += f'    nxdomainCache: nilNxdomainCache,\n'
        res += f'    nodataCache: nilNodataCache,\n'
        res += f'    sbelt: sb,\n'  # TODO: where is sb defined?
        res += f'    workBudget: emptyIN,\n'
        res += f'    blockedQueries: eptQSS,\n'
        res += f'    sentQueries: eptQSS >'
        return res

class Nameserver:

    def __init__(self, address, zones) -> None:
        self.address = address
        self.zones = zones

    def __str__(self) -> str:
        return f'< {self.address} : Nameserver | db: ({self.zones}), ... >'

    def to_maude(self) -> str:
        res = f'< {address_to_maude(self.address)} : Nameserver |\n'
        res += f'    db: ({" ".join(list(map(lambda z: z.maude_name(), self.zones)))}),\n'
        res += f'    queue: nilQueue >'
        return res

class DelayedNameserver:

    def __init__(self, address, zones, delay) -> None:
        self.address = address
        self.zones = zones
        self.delay = delay

    def __str__(self) -> str:
        return f'< {self.address} : DelayedNameserver | db: ({self.zones}), nsDelay: {self.delay}, ... >'

    def to_maude(self) -> str:
        res = f'< {address_to_maude(self.address)} : DelayedNameserver |\n'
        res += f'    db: ({" ".join(list(map(lambda z: z.maude_name(), self.zones)))}),\n'
        res += f'    nsDelay: {self.delay} >'
        return res
