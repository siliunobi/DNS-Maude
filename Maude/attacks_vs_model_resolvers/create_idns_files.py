#!/usr/bin/env python3
import os, sys
import subprocess
import re
import time

from utils import *
from model_resolver import *
from model_attack_file import *


# Create the chained delegations and return the records ? what is the max number
def chained_ns_delegations(starting_query,nb_chained_del=10, nb_labels=0,nb_del_to_target=0,target_address="'target-ans . 'com . root"):
    ns_records_text = "\t--- Deep delegation\n"

    reg = re.search(r"([']\D+)(\d+)", starting_query)
    prefix = reg.group(1)
    number = int(reg.group(2))
    # Keep the address of the attacker nameserver
    end_of_query = starting_query.replace(prefix+str(number)+" . ", "")
    # print("Prefix : " + prefix +"; NUmber :"+ str(number))
    # print("End of query : "+end_of_query)
    model = "\t\t< "+ "{current} , ns, testTTL, "
    model_record_itself= "{prefix}{number}" +" . "+ end_of_query
    current_query = starting_query

    count_to_target= 0

    for i in range(nb_chained_del):
        number+=1
        ns_records_text += model.format(current=current_query) + model_record_itself.format(prefix=prefix,number=str(number))+" >\n"

        for j in range(nb_del_to_target):
            ns_records_text += model.format(current=current_query) + f"'a{count_to_target} . " + target_address + " >\n"
            count_to_target+=1

        prefix_labels = ""
        for k in reversed(range(nb_labels)):
            prefix_labels += "'fake"+str(k)+" . "
        current_query = prefix_labels + model_record_itself.format(prefix=prefix,number= str(number))


    return ns_records_text

PATH_TO_MAIN_DIR = "../../../../.."


start_text = '''
mod TEST is
  inc SAMPLER + APMAUDE + DNS + PROPERTIES .

  op testTTL : -> Float .
  eq testTTL = 3600.0 .

  {}
 '''

continue_text = '''

  op q : -> Query .
  eq q = query(1, 'sub1 . 'attacker . 'com . root, a) .

  ops mAddr cAddr rAddr : -> Address .

  --- "SBELT": fallback if there are no known name servers
  op sb : -> ZoneState .
  eq sb = < root ('a . 'root-servers . 'net . root |-> addrRoot) > .

  ops addrRoot addrNScom addrNSattacker : -> Address .

  op cache : -> Cache .
  eq cache =
    cacheEntry(< 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >, 1)
    cacheEntry(< 'attacker . 'com . root, ns, testTTL, 'ns . 'attacker . 'com . root >, 1)
    cacheEntry(< 'ns . 'attacker . 'com . root, a, testTTL, addrNSattacker >, 1) .


  ops zoneRoot zoneCom zoneAttacker : -> List{Record} .
  eq zoneRoot =
    --- authoritative data
    < root, soa, testTTL, soaData(testTTL) > --- dummy value
    < root, ns, testTTL, 'a . 'root-servers . 'net . root >

    --- non-authoritative data
    < 'a . 'root-servers . 'net . root, a, testTTL, addrRoot >
    < 'com . root, ns, testTTL, 'ns . 'com . root >
    < 'ns . 'com . root, a, testTTL, addrNScom > . --- glue

  eq zoneCom =
    --- authoritative data
    < 'com . root, soa, testTTL, soaData(testTTL) >
    < 'com . root, ns, testTTL, 'ns . 'com . 'root >
    < 'ns . 'com . root, a, testTTL, addrNScom >

    --- non-authoritative data
    < 'attacker . 'com . root, ns, testTTL, 'ns . 'attacker . 'com . root >
    < 'ns . 'attacker . 'com . root, a, testTTL, addrNSattacker > . --- glue
'''

# Here we may not need the target
target_text = '''
  eq zoneTargetANS =
    --- authoritative data
    < 'target-ans . 'com . root, soa, testTTL, soaData(testTTL) >
    < 'target-ans . 'com . root, ns, testTTL, 'ns . 'target-ans . 'com . root >
    < 'ns . 'target-ans . 'com . root, a, testTTL, addrNStargetANS >
    {}
    .
'''


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

MAUDE = 'maude.linux64'

# NUMBER_LOOPS = 1

NB_DELEGATIONS_TO_TARGET = 3
RANGE_CHAINED_DELEGATIONS = range(1,11)
# Actually we don't need the cname as we don't create such records
# RANGE_CNAME_LENGTH = [1]#range(1,2)

RANGE_LABELS = range(1,11)

paths = []

def main():

    print("Start of the creation of the files for iDNS attacks...\n")


    resolver_models = [Unbound1_10_0(), Unbound1_16_0(), PowerDNS4_7_0()]

    QUERY = "'sub1 . 'attacker . 'com . root"
    time1 = time.perf_counter()

    # Needed for the plot unfortunately
    cname_chain_length = 0
    original_cname_chain_length = 0

    variants = [IDNSVariant1(), IDNSVariant2(), IDNSVariant3()]#, "variant2", "variant3"]
    for variant in variants :

        print("Currently working with "+ variant.name_attack)

        for resolver_model in resolver_models:
            print("#" * 50)
            print("\nResolver model : " + resolver_model.name)
            # Creation of the files that will be executed to obtain the results

            BASE_DIR = "attacks_vs_model_resolvers/"
            BASE_FOLDER = variant.folder + "/" + resolver_model.folder + "/"
            check_folder_exists(BASE_FOLDER)

            print(BASE_FOLDER)

            for labels in RANGE_LABELS:

                # Create the measurement file, we fix the number of delegation and the length of the CNAME chain
                result_path = "res_" + format(labels, '02d')+"labels_" + format(cname_chain_length, '02d')+"cnamelength" + ".txt"
                # "res_" + format(ns_del, '02d')+"nsdel_" + format(cname_chain_length, '02d')+"cnamelength" + ".txt"
                relative_path = BASE_FOLDER +"results/"+ "measurements/"+ result_path
                check_folder_exists(BASE_FOLDER +"results/"+ "measurements/")

                # Empty the result file
                open(relative_path, 'w').close()

                original_labels = labels

                # We count the number of delegation
                for ns_chained_del in RANGE_CHAINED_DELEGATIONS:


                    path = format(ns_chained_del, '02d')+"nsdel_" + format(original_cname_chain_length, '02d')+"cnamelength_" + \
                     format(original_labels, '02d') + "labels" + ".maude"
                    print("Path of the file to be executed : "+path)
                    paths.append(path)

                    file_path = BASE_FOLDER + "files/"+path
                    check_folder_exists(BASE_FOLDER + "files/")

                    labels = check_number_labels(labels, resolver_model)


                    # It is the same as maxFetchParam with maxFetch enabled, but here it is explicit
                    # It's a double check, we do not create more NS delegations as there is a maximum
                    # number of subqueries that can be created by the resolver
                    if ns_chained_del > resolver_model.max_subqueries:
                        ns_chained_del = resolver_model.max_subqueries
                        print("Maximum number of subqueries has been reached, more NS delegations won't improve the amplification")


                    # If there is a target, we need to create a chained ns delegation + other ns delegation to the target
                    if len(variant.target_text) != 0:
                        ns_records_text = chained_ns_delegations(nb_chained_del=ns_chained_del, starting_query= QUERY, nb_labels=labels, nb_del_to_target = NB_DELEGATIONS_TO_TARGET)
                    else:
                        ns_records_text = chained_ns_delegations(nb_chained_del=ns_chained_del, starting_query= QUERY, nb_labels=labels)

                    # print("NS DELE : "+ ns_records_text)

                    whole = variant.imports.format(PATH_TO_MAIN_DIR=PATH_TO_MAIN_DIR) + variant.description + variant.start_text.format(resolver_model.config_text()) + variant.continue_text + variant.target_text + variant.attacker_text.format(ns_records_text) + variant.end_text + variant.print_text

                    with open(file_path, "w+") as file:
                        file.write(whole)

                    # Run the file
                    out = utils.run_file(file_path)


                    # Take the first value of amplification : STILL TO IMPROVE THIS
                    # So far the first value is msgAmpFactor(cAddr, rAddr)
                    amp = re.search(r"FiniteFloat: (\d+.\d+(e\+\d)?)", out).group(1)
                    print(amp)


                    # We write on each row a new value corresponding to the amplification factor
                    with open(relative_path, "a+") as file:
                        # Convert the scientific notation to float
                        file.write(str(float(amp))+",")


    time2 = time.perf_counter()
    print("The files have been created and their execution has been measured in {:.3f} seconds !".format(time2-time1))



# Should I delete the files created to get the measurements ?
# Maybe because there are quite some creation_sub_ccv_qmin_files
# Be careful about the parallel processes should try to be smart

# Change the description at the beginning of the file



if __name__ == "__main__":
    main()
