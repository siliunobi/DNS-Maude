
from conversion_utils import name_to_maude, rtype_to_maude

class Query:

    def __init__(self, id, qname, qtype) -> None:
        self.id = id
        self.qname = qname
        self.qtype = qtype

    def __str__(self) -> str:
        return f'query({self.id}, {self.qname}, {self.qtype})'

    def to_maude(self) -> str:
        return f'query({self.id}, {name_to_maude(self.qname)}, {rtype_to_maude(self.qtype)})'
