#!/usr/bin/env python3
import re
import time

import utils
from model_resolver import Unbound1_10_0_NO_CHAIN_VALIDATION,  Unbound1_16_0_NO_CHAIN_VALIDATION, PowerDNS4_7_0_NO_CHAIN_VALIDATION, PowerDNS4_7_0_QMIN_NO_CHAIN_VALIDATION, Bind9_18_4_NO_CHAIN_VALIDATION
from model_attack_file import SubqueriesUnchainedDNAME
from watcher import Watcher

"""This file creates and runs the attack Subqueries + Unchained + DNAME, also
called Parallel NS + Unchained + DNAME."""


def main():

    scrubbing = False
    # QMIN_DEACTIVATED = False
    PATH_TO_MAIN_DIR = "../../../../.."

    RANGE_DNAME_LENGTH = [17]
    RANGE_NS_DELEGATIONS = range(1, 11)
    RANGE_LABELS = range(0, 1)

    print("Start of the creation of the files for DNAME attacks...\n")

    resolver_models = [Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(),
                       utils.which_powerdns(scrubbing, qmin_deactivated), Bind9_18_4_NO_CHAIN_VALIDATION()]

    # If QMIN is deactivated -> change PowerDNS4_7_0_QMIN_NO_CHAIN_VALIDATION to PowerDNS4_7_0_NO_CHAIN_VALIDATION
    qmin_folder = "qmin_disabled" if qmin_deactivated else "qmin_enabled"

    time1 = time.perf_counter()

    variants = [SubqueriesUnchainedDNAME()]
    for variant in variants:

        print("Currently working with " + variant.name_attack)

        for resolver_model in resolver_models:
            print("#" * 50)
            print("\nResolver model : " + resolver_model.name)

            BASE_FOLDER = variant.folder + "/" + qmin_folder + "/" + resolver_model.folder + "/"
            utils.check_folder_exists(BASE_FOLDER)

            watcher = Watcher()

            print(BASE_FOLDER)

            for labels in RANGE_LABELS:

                for dname_chain_length in RANGE_DNAME_LENGTH:

                    # Create/empty the measurement file, we fix the number of delegation and the length of the CNAME chain
                    result_path = "res_" + format(labels, '02d')+"labels_" + \
                                                  format(dname_chain_length, '02d')+"dnamelength" + ".txt"

                    MEASUREMENTS_FOLDER = BASE_FOLDER+"results/" + "measurements/"
                    utils.check_folder_exists(MEASUREMENTS_FOLDER)
                    relative_path = MEASUREMENTS_FOLDER + result_path

                    # Empty the result file
                    open(relative_path, 'w').close()

                    original_dname_chain_length = dname_chain_length
                    original_labels = labels

                    for ns_del in RANGE_NS_DELEGATIONS:

                        path = format(ns_del, '02d')+"nsdel_" + format(original_dname_chain_length, '02d')+"dnamelength_" + \
                         format(original_labels, '02d') + "labels" + ".maude"
                        print("Path of the file to be executed : "+path)

                        FILES_FOLDER = BASE_FOLDER + "files/"
                        file_path = FILES_FOLDER + path
                        utils.check_folder_exists(FILES_FOLDER)

                        # Implement the artificial limits
                        labels, dname_chain_length, ns_del = \
                            utils.check_variables(labels=labels, chain_length=dname_chain_length,
                                                  nb_delegations=ns_del, chain_type="DNAME",
                                                  resolver_model=resolver_model)
                        
                        # Create the ns records for intermediary,
                        # the dname chains for the intermediary and the target
                        ns_records_text_in_intermediary, dname_intermediary, dname_chain_in_target = utils.ns_del_and_dname_chain(
                            dname_chain_length=dname_chain_length, nb_del=ns_del, address_to_be_delegated="'del . 'intermediary . 'com . root", target_address="'target-ans . 'com . root")

                        whole = variant.whole_file(PATH_TO_MAIN_DIR, resolver_model, qmin_deactivated, dname_chain_in_target, ns_records_text_in_intermediary, dname_intermediary)

                        with open(file_path, "w+") as file:
                            file.write(whole)

                        if not watcher.set_values_and_has_changed(nb_delegations=ns_del, dname_chain_length=dname_chain_length, variant_attack_name= variant.name_attack, nb_labels=labels):
                            with open(relative_path, "a+") as file:
                                # Convert the scientific notation to float
                                file.write(str(float(amp)) + ",")
                            # Continue as it obtains the same previous value
                            print("DID not need to run the file, as the same parameters are being used ")
                            continue
                        # Run the file
                        out = utils.run_file(file_path)

                        # Take the first value of amplification
                        amp = re.search(r"FiniteFloat: (\d+.\d+(e\+\d)?)", out).group(1)
                        print(amp)

                        # We write on each row a new value corresponding to the amplification factor
                        with open(relative_path, "a+") as file:
                            # Convert the scientific notation to float
                            file.write(str(float(amp))+",")

    time2 = time.perf_counter()
    print("The files have been created and their execution has been measured in {:.3f} seconds !".format(time2-time1))


if __name__ == "__main__":
    # QMIN deactivated
    qmin_deactivated = True
    main()

    # QMIN enabled
    qmin_deactivated = False
    main()
