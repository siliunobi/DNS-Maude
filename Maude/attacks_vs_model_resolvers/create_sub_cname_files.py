#!/usr/bin/env python3

import re
import time

import utils
from model_attack_file import SubqueriesUnchainedCNAME
from model_resolver import *
from utils import check_folder_exists, intermediary_nsdelegations_to_target, run_file, simple_cname_chain
from watcher import Watcher

"""This file creates and runs the attack Subqueries + Unchained, also called
Parallel NS + Unchained."""

PATH_TO_MAIN_DIR = "../../../../.."


def main():

    scrubbing = False
    # QMIN_DEACTIVATED = False

    qmin_folder = "qmin_disabled" if qmin_deactivated else "qmin_enabled"

    # Note here if unchained is used -> we need "no validation" for each resolver
    resolver_models = [Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(), utils.which_powerdns(scrubbing, qmin_deactivated), Bind9_18_4_NO_CHAIN_VALIDATION()]

    variants = [SubqueriesUnchainedCNAME()]

    # If QMIN is deactivated  [True]-> change PowerDNS4_7_0_QMIN_NO_CHAIN_VALIDATION to PowerDNS4_7_0_NO_CHAIN_VALIDATION

    RANGE_CNAME_LENGTH = [17]  #[9, 12, 17]  # range(17,18)
    RANGE_NS_DELEGATIONS = range(1, 11)

    # Here if we use sub+ccv, we need to set the number of labels to add to 1
    RANGE_LABELS = [0]  # range(10,11)

    time1 = time.perf_counter()

    # Creation of the files that will be executed to obtain the results
    for variant in variants:
        for resolver_model in resolver_models:
            print("#" * 50)
            print("\nResolver model : " + resolver_model.name)

            BASE_FOLDER = variant.folder + "/" + qmin_folder + "/" + resolver_model.folder + "/"
            check_folder_exists(BASE_FOLDER)

            watcher = Watcher()

            for labels in RANGE_LABELS:
                for cname_chain_length in RANGE_CNAME_LENGTH:

                    # Create/empty the measurement file, we fix the number of delegation and the length of the CNAME chain
                    result_path = "res_" + format(labels, '02d')+"labels_" + \
                                                  format(cname_chain_length, '02d')+"cnamelength" + ".txt"

                    MEASUREMENTS_FOLDER = BASE_FOLDER+"results/" + "measurements/"
                    check_folder_exists(MEASUREMENTS_FOLDER)
                    relative_path = MEASUREMENTS_FOLDER + result_path

                    # Empty the result file
                    open(relative_path, 'w').close()

                    original_cname_chain_length = cname_chain_length
                    original_labels = labels

                    for ns_del in RANGE_NS_DELEGATIONS:

                        # First create the path of the files that will be executed with the initial parameters
                        # those can be modified afterwards to satisfy to the limit of the resolvers
                        path = format(ns_del, '02d')+"nsdel_" + format(original_cname_chain_length, '02d')+"cnamelength_" + \
                         format(original_labels, '02d') + "labels" + ".maude"
                        print("Path of the file to be executed : "+path)

                        FILES_FOLDER = BASE_FOLDER + "files/"
                        check_folder_exists(FILES_FOLDER)
                        file_path = FILES_FOLDER + path

                        # Implement the artificial limits
                        labels, cname_chain_length, ns_del = \
                            utils.check_variables(labels=labels, chain_length=cname_chain_length,
                                                  nb_delegations=ns_del, chain_type="CNAME",
                                                  resolver_model=resolver_model)

                        # Create the records leading to the target
                        ns_records_text_in_intermediary, ns_records_to_target = intermediary_nsdelegations_to_target(
                            nb_delegations=ns_del, address_to_be_delegated="'del . 'intermediary . 'com . root", target_address="'target-ans . 'com . root")

                        cname_chain_intermediary, cname_chain_in_target = simple_cname_chain(ns_records_to_target=ns_records_to_target, cname_chain_length=cname_chain_length, address_intermediary="'intermediary . 'com . root", target_address="'target-ans . 'com . root", )

                        whole = variant.whole_file(PATH_TO_MAIN_DIR, resolver_model,qmin_deactivated, cname_chain_in_target, ns_records_text_in_intermediary, cname_chain_intermediary)

                        # Write the text in a file
                        with open(file_path, "w+") as file:
                            file.write(whole)

                        if not watcher.set_values_and_has_changed(nb_delegations=ns_del, cname_chain_length=cname_chain_length, variant_attack_name= variant.name_attack, nb_labels=labels):
                            # Add the previous value
                            with open(relative_path, "a+") as file:
                                file.write(str(float(amp))+",")

                            # Continue as it obtains the same previous value
                            print("DID not need to run the file, as the same parameters are being used...")
                            continue
                        # Run the file
                        out = run_file(file_path)

                        # Take the first value of amplification
                        amp = re.search(r"FiniteFloat: (\d+.\d+(e\+\d)?)", out).group(1)
                        print(amp)

                        # We write on each row a new value corresponding to the amplification factor
                        with open(relative_path, "a+") as file:
                            # Convert the scientific notation to float
                            file.write(str(float(amp))+",")

            print("Creating the file and measuring the results has been done for this resolver model.\n" + "#"*30 + "\n")

    time2 = time.perf_counter()
    print("The files have been created and their execution has been measured in {:.3f} seconds !".format(time2-time1))


if __name__ == "__main__":
    qmin_deactivated = True
    main()

    # QMIN enabled
    # qmin_deactivated = False
    # main()
