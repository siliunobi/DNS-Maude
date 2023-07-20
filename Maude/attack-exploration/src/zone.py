from conversion_utils import address_to_maude, name_to_maude, rtype_to_maude, soa_data

class Zone:

    def __init__(self, name, parent_zone, records) -> None:
        self.name = name
        self.parent_zone = parent_zone
        self.records = records

    def __str__(self) -> str:
        res = f'Zone {self.name}' + (f' (parent: {self.parent_zone.name})' if self.parent_zone else '') + ' =\n'
        for record in self.records:
            res += f'  {record}\n'
        return res

    def add_records(self, records):
        self.records += records

    def maude_name(self):
        labels = self.name.split('.')
        return 'zone' + ''.join(label.capitalize() for label in labels)

    def to_maude(self):
        assert self.records, 'Zone has no records'

        res = f'op {self.maude_name()} : -> List{{Record}} .\n'
        res += f'eq {self.maude_name()} ='
        for record in self.records:
            res += f'\n  {record.to_maude()}'
        res += ' .'
        return res

class Record:
    """A DNS resource record"""

    def __init__(self, owner, rtype, ttl, rdata) -> None:
        self.owner = owner
        self.rtype = rtype
        self.ttl = ttl
        self.rdata = rdata

    def __str__(self) -> str:
        return f'< {self.owner}, {self.rtype}, {self.ttl}, {self.rdata} >'

    def to_maude(self):
        # convert rdata
        if self.rtype == 'A':
            rdata_maude = address_to_maude(self.rdata)
        elif self.rtype in ['NS', 'CNAME', 'DNAME']:
            rdata_maude = name_to_maude(self.rdata)
        elif self.rtype == 'SOA':
            rdata_maude = soa_data(self.rdata)
        else:
            rdata_maude = 'nullAddr' # dummy value

        return f'< {name_to_maude(self.owner)}, {rtype_to_maude(self.rtype)}, ' + \
            f'{self.ttl}.0, {rdata_maude} >'

def lookup(owner, rtype, records):
    """
    Returns all records in the given list with the given owner name and type.
    """
    result = []
    for record in records:
        if record.owner == owner and record.rtype == rtype:
            result.append(record)
    return result

