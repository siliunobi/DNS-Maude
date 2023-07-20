
def rtype_to_maude(rtype: str) -> str:
    return rtype.lower()

def address_to_maude(address: str) -> str:
    octets = address.split('.')
    return ' . '.join(octets)

def name_to_maude(name: str) -> str:
    labels = name.split('.')
    res = ''
    for label in labels:
        if res:
            res += ' . '
        res += label_to_maude(label)
    return res

def label_to_maude(label: str) -> str:
    if label == '*':
        return 'wildcard'
    if label == '':
        return 'root'
    else:
        return "'" + label

def querylist_to_maude(queries) -> str:
    if not queries:
        return 'nil'
    else:
        return ' '.join(map(lambda q: q.to_maude(), queries))

def soa_data(rdata) -> str:
    return f'soaData({rdata}.0)'

def addr_op_name_from_domain(domain: str) -> str:
    # ns.example.com -> addrNsExampleCom
    labels = domain.split('.')
    return 'addr' + ''.join(label.capitalize() for label in labels)

def config_to_maude_file(config, param_dict, filename='config.maude', model='probabilistic'):
    with open(filename, 'w') as file:
        if model == 'probabilistic':
            file.write(config.to_maude_prob(param_dict))
        elif model == 'nondet':
            file.write(config.to_maude_nondet(param_dict))
        elif model == 'nondet-no-client':
            file.write(config.to_maude_nondet_no_client(param_dict))
        else:
            raise ValueError(f'unsupported model: {model}')
