#!/usr/bin/env python3
import os
import re
import string
import subprocess

import model_resolver

# May depend on the system running maude
MAUDE = "maude"  # /usr/bin/maude/maude.linux64
ADDRESS_INTERMEDIARY = "'intermediary . 'com . root"
TARGET_ANS = "'target-ans . 'com . root"
FAKE_LABEL = "'fake"


def check_folder_exists(folder_name):
    """Check if the folder exists, if not create it. Takes care of intermediary folders."""
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)


def check_lists_size(list_of_lists):
    """Raises a ValueError if the lists don't have all the same size."""
    first_length = len(list_of_lists[0])
    if not all(len(list_values) == first_length for list_values in list_of_lists):
        raise ValueError("The lists found don't have the same size ! ")


def check_number_labels(labels, resolver_model):
    """Checks the current number of labels. If higher than the limit, resets it to the limit."""
    if labels > resolver_model.qmin_limit:
        labels = resolver_model.qmin_limit
        print("QMIN limit of {} reached, more labels won't improve the amplification.".format(
            str(resolver_model.qmin_limit)))

    return labels


def check_cname_chain_length(cname_chain_length, resolver_model):
    """Checks the current length of the cname chain. If higher than the limit, resets it to the limit."""
    if cname_chain_length > resolver_model.cname_limit:
        cname_chain_length = resolver_model.cname_limit
        print("CNAME chain limit of {} reached, longer chain won't improve the amplification".format(
            str(resolver_model.cname_limit)))

    return cname_chain_length


def check_dname_chain_length(dname_chain_length, resolver_model):
    """Checks the current length of the dname chain. If higher than the limit, resets it to the limit."""
    if dname_chain_length > resolver_model.cname_limit:
        dname_chain_length = resolver_model.cname_limit
        print("DNAME chain limit of {} reached, longer chain won't improve the amplification".format(
            str(resolver_model.cname_limit)))

    return dname_chain_length


def check_subqueries(ns_del, resolver_model):
    """Checks the current number of subqueries, here we take into account only ns delegation.If higher than the
    limit, resets it to the limit."""
    if ns_del > resolver_model.max_subqueries:
        ns_del = resolver_model.max_subqueries
        print(
            "Maximum number of subqueries of {} has been reached, more NS delegations won't improve the amplification".format(
                str(resolver_model.max_subqueries)))

    return ns_del


def check_variables(labels, chain_length, nb_delegations, chain_type, resolver_model):
    labels = check_number_labels(labels, resolver_model)
    if "CNAME" in chain_type:
        chain_length = check_cname_chain_length(chain_length, resolver_model)
    else:
        chain_length = check_dname_chain_length(chain_length, resolver_model)
    nb_delegations = check_subqueries(nb_delegations, resolver_model)

    return labels, chain_length, nb_delegations


def run_file(maude_file):
    """Run the file with maude and return the output summary."""

    # Tricky to find the path of maude using its alias, the easier would have been '/usr/bin/maude/maude.linux64'

    cmd = ['/bin/bash', '-i', '-c'] + [MAUDE + " " + maude_file]
    # Input containing carriage return is needed to artificially trigger the command
    p = subprocess.run(cmd, check=True, capture_output=True, text=True, input="quit\n")
    out = p.stdout


    index = out.find("rewrite in TEST : msg")
    if index == -1:
        index = out.find("rewrite in TEST : num")

    if index == -1:
        index = out.find("rewrite in TEST : max")

    if index == -1:
        index = out.find("rewrite in TEST : avg")

    if index == -1:
        raise ValueError("No values has been found in the summary. ABORT ...")

    # Filter to get only the last part which starts with the messages counts and
    # amplification factors
    out = out[index:]

    print(out)
    return out


############################################################################################################################################################################################
# USEFUL FOR SUB+CCV_QMIN


def intermediary_nsdelegations_to_target(nb_delegations=10,
                                         address_to_be_delegated="'del . 'intermediary . 'com . root",
                                         target_address=TARGET_ANS, nb_labels=1):
    """Creates the delegations to the target_address and returns the records to be written inside the intermediary zone.
    Used for Subqueries+CCV+QMIN."""

    record = ""
    for lab in reversed(range(nb_labels - 1)):
        record += FAKE_LABEL + str(lab) + " . "

    ns_records_text_in_intermediary = "\t--- Malicious delegation\n"
    ns_records_to_target = []

    model_address_in_target = record + "'zz{} . " + target_address
    model_record = "\t\t< " + address_to_be_delegated + ", ns, testTTL, " + model_address_in_target + " >\n"

    for i in range(nb_delegations):
        ns_records_text_in_intermediary += model_record.format(i)
        ns_records_to_target.append(model_address_in_target.format(i))

    return ns_records_text_in_intermediary, ns_records_to_target


# Create the records that lead to use QMIN feature
def records_with_labels(previous_suffix, previous_suffix_number, nb_labels=10,
                        target_address=TARGET_ANS):
    record = ""
    if previous_suffix is None:
        # The suffix is also counted as a label, so here we remove one to nb_labels
        for lab in reversed(range(nb_labels - 1)):
            record += FAKE_LABEL + str(lab) + " . "
        record += "'a" + str(previous_suffix_number) + " . "
        record += target_address
    else:
        for lab in reversed(range(0, nb_labels - 1)):
            record += FAKE_LABEL + str(lab) + " . "
        record += "'" + chr(ord(previous_suffix) + 1) + str(previous_suffix_number) + " . " + target_address
    return record


def target_cname_chain(ns_records_to_target, chain_length=10, nb_labels=10, target_address=TARGET_ANS):
    records_in_target = ""
    model_record = "< {current} , cname, testTTL, {next} >"
    for index, ns_del in enumerate(ns_records_to_target):
        records_in_target += "\n\n"

        # When the chain is null, need to have a record pointing to somewhere else
        if chain_length <= 0:
            # Record must be cname, otherwise obfuscation will occur and more queries will be sent
            model_a_rec = "< {current} , cname, testTTL, {next} >"
            next = " 'a . 'com . root"
            records_in_target += "\t\t" + model_a_rec.format(current=ns_del, next=next) + "\n"
        else:
            # First record
            next = records_with_labels(nb_labels=nb_labels, previous_suffix=None, previous_suffix_number=index)
            records_in_target += "\t\t" + model_record.format(current=ns_del, next=next) + "\n"

            # Remove one from the chain length as we already have the first record right above, and remove another one because the resolver will ask the last cname record and this may bypass the cname limit

            for _ in range(chain_length - 1):
                current = next
                # Find the last suffix
                last_suffix = re.findall(r"[a-z]+\d+", current)[-1]

                previous_suffix = re.findall(r"[a-z]+", last_suffix)[0]
                previous_suffix_number = re.findall(r"\d+", last_suffix)[0]
                next = records_with_labels(previous_suffix=previous_suffix,
                                           previous_suffix_number=previous_suffix_number,
                                           nb_labels=nb_labels, target_address=target_address)
                records_in_target += "\t\t" + model_record.format(current=current, next=next) + "\n"

    return records_in_target


############################################################################################################################################################################################
# Useful Subqueries CCV + delay

def standalone_cname_scrubbing_delay(nb_labels, cname_chain_length, target_address=TARGET_ANS,
                                     nb_delegations=1):
    query_from_client = "op q : -> Query .\n"

    labels_text = ""
    if nb_labels != 0:
        for lab in reversed(range(nb_labels - 1)):
            labels_text += FAKE_LABEL + str(lab) + " . "

    query_from_client += "eq q = query(1, " + labels_text + " 'a . 'target-ans . 'com . root, a) ."

    cname_chain_in_target = standalone_cname_chain_in_target(nb_labels=nb_labels, cname_chain_length=cname_chain_length,
                                                             target_address=TARGET_ANS,
                                                             nb_delegations=nb_delegations)

    return query_from_client, cname_chain_in_target


def cname_chain_val_delay(nb_chains, cname_chain_length, target_address):
    query_from_client = "op q : -> Query .\n"
    query_from_client += "eq q = query(1, 'zz0 . 'target-ans . 'com . root, a) ."

    cname_chain_in_target = target_cname_chain(ns_records_to_target=["'zz0 . 'target-ans . 'com . root"],
                                               chain_length=cname_chain_length - 1, nb_labels=0,
                                               target_address=target_address)

    return query_from_client, cname_chain_in_target


def unchained_cname_chains(nb_labels=0, cname_chain_length=17, address_intermediary=ADDRESS_INTERMEDIARY,
                           target_address=TARGET_ANS, ):
    cname_chain_target = ""
    cname_chain_intermediary = ""
    alphabet = list(string.ascii_letters)

    model_record = "< {current} , cname, testTTL, {next} >"
    labels_text = ""
    for lab in reversed(range(nb_labels - 1)):
        labels_text += FAKE_LABEL + str(lab) + " . "

    current = labels_text + "'" + alphabet[0] + " . " + target_address
    next = labels_text + "'" + alphabet[1] + " . " + address_intermediary

    cname_chain_target += "\t\t" + model_record.format(current=current, next=next) + "\n"

    # Start with target
    for c in range(0, cname_chain_length - 1):
        current = next

        if c % 2 == 1:
            next = labels_text + "'" + alphabet[c + 2] + " . " + address_intermediary
            cname_chain_target += "\t\t" + model_record.format(current=current, next=next) + "\n"
        else:
            next = labels_text + "'" + alphabet[c + 2] + " . " + target_address
            cname_chain_intermediary += "\t\t" + model_record.format(current=current, next=next) + "\n"

    return cname_chain_intermediary, cname_chain_target


def simple_cname_chain(ns_records_to_target, cname_chain_length=17, address_intermediary=ADDRESS_INTERMEDIARY,
                       target_address=TARGET_ANS, ):
    cname_chain_target = ""
    cname_chain_intermediary = ""

    model_record = "< {current} , cname, testTTL, {next} >"

    return create_simple_chain_with_model(model_record, cname_chain_length, ns_records_to_target)


# Useful for CNAME Scrubbing
def standalone_cname_chain_in_target(nb_labels=0, cname_chain_length=17, target_address=TARGET_ANS,
                                     nb_delegations=1):
    cname_chain_in_target = ""

    model_record = "< {current} , cname, testTTL, {next} > \n"
    last_record = "\t\t < {last} , a, testTTL, addrNScom > \n"

    labels_text = ""
    if nb_labels != 0:
        for lab in reversed(range(nb_labels - 1)):
            labels_text += FAKE_LABEL + str(lab) + " . "

    alphabet = string.ascii_letters

    # According to the number of delegations
    for i in range(0, nb_delegations):
        current = labels_text + "'" + alphabet[0] + " . " + target_address
        next = labels_text + "'" + alphabet[1] + str(i) + " . " + target_address

        # If the chain length is 1 -> we just add an a record
        if cname_chain_length == 0:
            return last_record.format(last=current)

        cname_chain_in_target += "\t\t" + model_record.format(current=current, next=next) + "\n"

        for c in range(0, cname_chain_length - 1):
            current = next
            next = labels_text + "'" + alphabet[c + 2] + str(i) + " . " + target_address
            cname_chain_in_target += "\t\t" + model_record.format(current=current, next=next) + "\n"

        cname_chain_in_target += last_record.format(last=next) + "\n"

    return cname_chain_in_target


####################################################
# Useful for Subqueries unchained with DNAME Chain


# Create the delegations to the target_address and return the records to be written in maude
def dname_intermediary_nsdelegations_to_target(nb_labels=0, nb_del=10,
                                               address_to_be_delegated="'del . 'intermediary . 'com . root",
                                               target_address=TARGET_ANS):
    ns_records_text = "\t--- Malicious delegation\n"
    ns_records_to_target = []
    labels = ""
    if nb_labels != 0:
        for lab in reversed(range(nb_labels - 1)):
            labels += FAKE_LABEL + str(lab) + " . "

    model_record_target = "'sub . " + labels + " 'a{} . " + target_address
    model = "\t\t< " + address_to_be_delegated + ", ns, testTTL, " + model_record_target + " >\n"
    for i in range(1, nb_del + 1):
        ns_records_text += model.format(i)
        ns_records_to_target.append(model_record_target.format(i))

    return ns_records_text, ns_records_to_target


def simple_dname_chain(ns_records_to_target, dname_chain_length=17,
                       target_address=TARGET_ANS):
    dname_chain_target = ""
    dname_chain_intermediary = ""

    model_record = "< {current} , dname, testTTL, {next} >"
    return create_simple_chain_with_model(model_record, dname_chain_length, ns_records_to_target)


def create_simple_chain_with_model(model_record, chain_length, ns_records_to_target,
                                   address_intermediary=ADDRESS_INTERMEDIARY,
                                   target_address=TARGET_ANS):
    '''Create a chain according to the model received either CNAME OR DNAME.
    For DNAME, it takes care to remove the first prefix : 'sub . 'a1 -> removes the first prefix and adjusts the letter for the next record.
    For CNAME, it should receive 'zz{i} . target' -> it will change the "zz" by "a" and keep the number i for the subsequent records.
    '''

    alphabet = string.ascii_lowercase
    if "dname" in model_record:
        alphabet = alphabet[1:]

    dcname_chain_target = ""
    dcname_chain_intermediary = ""
    # Index number
    for index, ns_del in enumerate(ns_records_to_target):

        dcname_chain_target += "\n\n"
        dcname_chain_intermediary += "\n\n"

        # First two records
        # Remove the prefix of the record
        second_prefix_index = [m.start() for m in re.finditer(r"[']\D{1,2}\d", ns_del)][0]

        truncated_record = ns_del[second_prefix_index:]
        index_of_number = [m.start() for m in re.finditer(r"\d", truncated_record)][0]
        # Here we remove the prefix -> as we will only work with the second one for DNAME
        if "dname" in model_record:
            truncated_record[index_of_number - 3:]

        # replace a by b
        (start_index_of_number, end_index_of_number) = \
            [(m.start(), m.end()) for m in re.finditer(r"\d+", truncated_record)][0]
        next = "'" + alphabet[0] + truncated_record[
                                   start_index_of_number: end_index_of_number] + " . " + address_intermediary

        dcname_chain_target += "\t\t" + model_record.format(current=truncated_record, next=next) + "\n"

        for c in range(chain_length - 1 - 1):
            current = next
            (start_index_of_number, end_index_of_number) = [(m.start(), m.end()) for m in re.finditer(r"\d+", current)][
                0]

            if c % 2 == 1:
                next = "'" + alphabet[c + 1] + current[
                                               start_index_of_number: end_index_of_number] + " . " + address_intermediary
                dcname_chain_target += "\t\t" + model_record.format(current=current, next=next) + "\n"
            else:
                next = "'" + alphabet[c + 1] + current[
                                               start_index_of_number: end_index_of_number] + " . " + target_address
                dcname_chain_intermediary += "\t\t" + model_record.format(current=current, next=next) + "\n"

    return dcname_chain_intermediary, dcname_chain_target


def dname_chain_val(ns_records_to_target, nb_label=0, dname_chain_length=17,
                    target_address=TARGET_ANS):
    dname_chain_target = ""

    model_record = "< {current} , dname, testTTL, {next} >"

    # The ns records have all the first prefix starting with 'a'
    alphabet = string.ascii_lowercase[1:]
    labels_text = ""
    if nb_label != 0:
        for lab in reversed(range(nb_label - 1)):
            labels_text += FAKE_LABEL + str(lab) + " . "
    # Index number
    for index, ns_del in enumerate(ns_records_to_target):

        dname_chain_target += "\n\n"

        # Remove "'sub . "
        truncated_record = ns_del[7:]

        # index_of_chain = re.findall(r"\d+", truncated_record)[0]

        # replace a by b ,truncated record[2:4] is the number
        next = "'" + alphabet[0] + truncated_record[2:4] + " . " + target_address
        if nb_label != 0:
            number = re.search(r"'a(\d+)", ns_del).group(1)
            next = labels_text + "'" + alphabet[0] + number + " . " + target_address

        dname_chain_target += "\t\t" + model_record.format(current=truncated_record, next=next) + "\n"

        # Remove one from the chain length as we already have the first record right above, and remove another one because the resolver will ask the last cname record and this may bypass the cname limit
        for c in range(dname_chain_length - 1 - 1):
            current = next
            next = "'" + alphabet[c + 1] + current[2:]
            if nb_label != 0:
                # Find numbers directly after some text starting with "'"
                pattern = re.compile(r"'[a-z]+(\d+)")
                list_indices_with_number = [(m.start(), m.end()) for m in pattern.finditer(current)]
                # Find the last indices
                number_index = list_indices_with_number[-1]
                next = current[:number_index[0]] + "'" + alphabet[c + 1] + current[number_index[1] - 1:]

            dname_chain_target += "\t\t" + model_record.format(current=current, next=next) + "\n"

    return dname_chain_target


def dname_chain(dname_chain_length, address_to_be_delegated, target_address, nb_label):
    pass


def ns_del_and_dname_chain(nb_label=0, dname_chain_length=17, nb_del=10,
                           address_to_be_delegated="'del . 'intermediary . 'com . root",
                           target_address=TARGET_ANS):
    ns_records_text, ns_records_to_target = dname_intermediary_nsdelegations_to_target(nb_label, nb_del,
                                                                                       address_to_be_delegated,
                                                                                       target_address)

    if nb_label > 0:
        dname_intermediary, dname_target = dname_chain(dname_chain_length, nb=nb_label)
    else:
        dname_intermediary, dname_target = simple_dname_chain(ns_records_to_target,
                                                              dname_chain_length=dname_chain_length)

    return ns_records_text, dname_intermediary, dname_target


def ns_del_and_dname_chain_scrubbing(nb_label=0, dname_chain_length=17, nb_del=10,
                                     address_to_be_delegated="'del . 'intermediary . 'com . root",
                                     target_address=TARGET_ANS):
    ns_records_text, ns_records_to_target = \
        dname_intermediary_nsdelegations_to_target(nb_label, nb_del, address_to_be_delegated, target_address)

    dname_target = \
        dname_chain_val(nb_label=nb_label, ns_records_to_target=ns_records_to_target,
                        dname_chain_length=dname_chain_length, target_address=TARGET_ANS)

    return ns_records_text, dname_target


################################################################################
## FOR THE PLOTS

def search_missing_attributes(filename, missing_attributes, ns_del, chain_type, name_chain_length, nb_labels):
    match = re.search(r"(\d+)nsdel", filename)
    if match is None:
        print("Missing attribute is the number of delegations. This is the number that is variable\n")
        missing_attributes.append("ns_del")
    else:
        ns_del = match.group(1)

    if chain_type == "CNAME":
        match = re.search(r"(\d+)cnamelength", filename)
        if match is None:
            print("Missing attribute is the length of the CNAME chain. This is the number that is variable\n")
            missing_attributes.append("cname_chain_length")
        else:
            name_chain_length = match.group(1)
    else:
        # DNAME
        match = re.search(r"(\d+)dnamelength", filename)
        if match is None:
            print("Missing attribute is the length of the DNAME chain. This is the number that is variable\n")
            missing_attributes.append("dname_chain_length")
        else:
            name_chain_length = match.group(1)

    match = re.search(r"(\d+)labels", filename)
    if match is None:
        print("Missing attribute is the number of labels. This is the number that is variable\n")
        missing_attributes.append("nb_labels")
    else:
        nb_labels = match.group(1)

    return missing_attributes, ns_del, name_chain_length, nb_labels


def search_missing_attributes_cname(filename, missing_attributes, ns_del, cname_chain_length, nb_labels):
    return search_missing_attributes(filename, missing_attributes, ns_del, "CNAME", cname_chain_length, nb_labels)


def search_missing_attributes_dname(filename, missing_attributes, ns_del, dname_chain_length, nb_labels):
    return search_missing_attributes(filename, missing_attributes, ns_del, "DNAME", dname_chain_length, nb_labels)


########
# For POWERDNS

def which_powerdns(scrubbing, qmin_deactivated):
    """Returns an instance of PowerDNS that corresponds to whether QMIN is enabled and scrubbing is activated."""
    if qmin_deactivated:
        if scrubbing:
            return model_resolver.PowerDNS4_7_0()
        return model_resolver.PowerDNS4_7_0_NO_CHAIN_VALIDATION()
    if scrubbing:
        return model_resolver.PowerDNS4_7_0_QMIN()
    return model_resolver.PowerDNS4_7_0_QMIN_NO_CHAIN_VALIDATION()


############################################################################################################################################################################################
# Functions used for conversion


# Remove the characters specific to Maude and the ending "root"
def address_to_zone_format(address):
    address = address.replace("'", "").replace(" ", "").replace(".root", "")
    return address


def convert_record_to_zone(record):
    record = record.strip().strip("<").strip(">")
    elements = record.split(",")

    res = f"{address_to_zone_format(elements[0]): <12} {'IN': ^12} {elements[1].upper(): ^12} {address_to_zone_format(elements[3]): ^12}"
    return res


def convert_maude_records_to_zones(records_txt):
    # We don't usually have A address target
    # Filter unwanted comments
    filtered = [record for record in records_txt.split("\n") if record.strip().startswith("<")]
    converted = "\n".join([convert_record_to_zone(record) for record in filtered])

    return converted


def example_convert():
    nb_del = 10
    address_to_be_delegated = "'del . 'intermediary . 'com . root"
    target_address = TARGET_ANS

    ns_records_text, ns_records_to_target = intermediary_nsdelegations_to_target(nb_del, address_to_be_delegated,
                                                                                 target_address)
    converted = convert_maude_records_to_zones(ns_records_text)
    print("NS DELEGATIONS CONVERTED \n" + converted)

    # CNAME CHAIN WITH number of labels, length of the chain, target_address
    cname_chains = target_cname_chain(ns_records_to_target, chain_length=10, nb_labels=10,
                                      target_address=TARGET_ANS)
    convert_cname = convert_maude_records_to_zones(cname_chains)
    print("\nCNAME CHAIN CONVERTED \n" + convert_cname)


if __name__ == "__main__":
    example_convert()
