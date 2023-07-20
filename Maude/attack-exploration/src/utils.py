
def get_domain_prefixes1(domain: str):
    """
    Returns all prefixes of the given domain.
    For example, on input 'www.example.com.' this returns ['', 'com.', 'example.com.', 'www.example.com.'].
    """
    labels = domain.split('.')

    current = ''
    prefixes = [current]
    for label in reversed(labels[:-1]):
        current = f'{label}.{current}'
        prefixes.append(current)

    return prefixes

def get_domain_prefixes(domains):
    """
    Returns all prefixes of all the given domains.
    """

    names = []
    for domain in domains:
        names += get_domain_prefixes1(domain)
    return list(set(names))
