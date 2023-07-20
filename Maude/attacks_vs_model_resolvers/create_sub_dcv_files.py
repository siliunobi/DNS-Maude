#!/usr/bin/env python3
import re
import time

import utils
from model_attack_file import SubqueriesDNAME_Chain_validation, SubqueriesDNAMEChainVal_Delay, SubqueriesDCVQMINA
from model_resolver import Unbound1_10_0, Unbound1_16_0, Bind9_18_4, \
    Bind9_18_4_NO_CHAIN_VALIDATION, Unbound1_16_0_CNAME_BYPASSED, Unbound1_10_0_CNAME_BYPASSED
from watcher import Watcher

"""This file creates and runs the attack Subqueries+Scrubbing+DNAME and the version
with delay, also called Parallel NS + Scrubbing + DNAME."""


def main():
    PATH_TO_MAIN_DIR = "../../../../.."
    scrubbing = True
    # QMIN_DEACTIVATED = False

    RANGE_DNAME_LENGTH = [17]  # [1, 9, 10, 11, 12, 17]
    RANGE_NS_DELEGATIONS = range(1, 11)
    RANGE_LABELS = range(0, 1)
    RANGE_NS_DELAY = range(0, 1700, 200)

    print("Start of the creation of the files for DNAME attacks...\n")
    qmin_folder = "qmin_disabled" if qmin_deactivated else "qmin_enabled"

    # If QMIN is deactivated [TRUE] -> change PowerDNS4_7_0_QMIN to PowerDNS4_7_0
    time1 = time.perf_counter()

    # For chain_validation, use Bind9_18_4_NO_CHAIN_VALIDATION()()
    # For delay use Bind9_18_4
    variants = [SubqueriesDCVQMINA(), SubqueriesDNAME_Chain_validation(), SubqueriesDNAMEChainVal_Delay()]

    for variant in variants:

        RANGE_LABELS = [1]

        # If qmin is enabled, we must change to a modified version of powerdns
        if type(variant) is SubqueriesDNAMEChainVal_Delay:
            # For delay, use Bind9_18_4() instead of Bind9_18_4_CNAME()
            resolver_models = [utils.which_powerdns(scrubbing, qmin_deactivated), Unbound1_16_0(), Unbound1_10_0(),
                               Bind9_18_4()]
        elif type(variant) is  SubqueriesDNAME_Chain_validation:
            resolver_models = [utils.which_powerdns(scrubbing, qmin_deactivated), Unbound1_16_0(), Unbound1_10_0(),
                               Bind9_18_4_NO_CHAIN_VALIDATION()]
        elif type(variant) is SubqueriesDCVQMINA:
            resolver_models = [utils.which_powerdns(scrubbing, qmin_deactivated), Unbound1_10_0_CNAME_BYPASSED(),
                               Unbound1_16_0_CNAME_BYPASSED(), Bind9_18_4()]
            RANGE_LABELS = [10]


        print("Currently working with " + variant.name_attack)

        for resolver_model in resolver_models:
            print("#" * 50)
            print("\nResolver model : " + resolver_model.name)
            # Creation of the files that will be executed to obtain the results

            BASE_FOLDER = variant.folder + "/" + qmin_folder + "/" + resolver_model.folder + "/"
            utils.check_folder_exists(BASE_FOLDER)

            watcher = Watcher()

            for labels in RANGE_LABELS:

                for dname_chain_length in RANGE_DNAME_LENGTH:

                    # Create/empty the measurement file, we fix the number of delegation and the length of the CNAME chain
                    result_path = "res_" + format(labels, '02d') + "labels_" + \
                                  format(dname_chain_length, '02d') + "dnamelength" + ".txt"

                    MEASUREMENTS_FOLDER = BASE_FOLDER + "results/" + "measurements/"
                    utils.check_folder_exists(MEASUREMENTS_FOLDER)
                    relative_path = MEASUREMENTS_FOLDER + result_path

                    # Empty the result file
                    open(relative_path, 'w').close()

                    original_dname_chain_length = dname_chain_length
                    original_labels = labels

                    if type(variant) is  SubqueriesDNAMEChainVal_Delay:
                        ns_del = 1

                        for ns_delay in RANGE_NS_DELAY:
                            path = format(ns_del, '02d') + "nsdel_" + format(original_dname_chain_length,
                                                                             '02d') + "dnamelength_" + \
                                   format(ns_delay, '03d') + "ns_delay_" + \
                                   format(original_labels, '02d') + "labels" + ".maude"
                            print("Path of the file to be executed : " + path)

                            file_path = BASE_FOLDER + "files/" + path
                            utils.check_folder_exists(BASE_FOLDER + "files/")

                            # Implement artificially the limits
                            labels, dname_chain_length, ns_del = \
                                utils.check_variables(labels=labels, chain_length=dname_chain_length,
                                                      nb_delegations=ns_del, chain_type="DNAME",
                                                      resolver_model=resolver_model)

                            # Create the ns records for intermediary,
                            # the dname chains for the intermediary and the target
                            #### Removing 1 query here gives the same delays as the implementation
                            ns_records_text_in_intermediary, dname_chain_in_target = utils.ns_del_and_dname_chain_scrubbing(
                                dname_chain_length=dname_chain_length, nb_del=ns_del,
                                address_to_be_delegated="'del . 'intermediary . 'com . root",
                                target_address="'target-ans . 'com . root")

                            # unfortunately thebelow lines are only for cname chains
                            # queries = "op q : -> Query .\n"
                            # queries += f"eq q = unchainedQuery('target-ans . 'com . root, {dname_chain_length}, 0) .\n"
                            #
                            # content_target = f"unchainedRecords('target-ans . 'com . root, 'target-ans . 'com . root, {dname_chain_length}, 0, 0.0) ."

                            whole = variant.whole_file(PATH_TO_MAIN_DIR, ns_delay, resolver_model, qmin_deactivated,
                                                       dname_chain_in_target, ns_records_text_in_intermediary)

                            with open(file_path, "w+") as file:
                                file.write(whole)

                            # Here we don't need watcher as values are always changing
                            # Run the file
                            out = utils.run_file(file_path)

                            # Take the first value of delays
                            amp = re.search(r"FiniteFloat: (\d+.\d+(e\+\d)?)", out).group(1)
                            print(amp)

                            # We write on each row a new value corresponding to the amplification factor
                            with open(relative_path, "a+") as file:
                                # Convert the scientific notation to float
                                file.write(str(float(amp)) + ",")

                    else:

                        for ns_del in RANGE_NS_DELEGATIONS:

                            path = format(ns_del, '02d') + "nsdel_" + format(original_dname_chain_length,
                                                                             '02d') + "dnamelength_" + \
                                   format(original_labels, '02d') + "labels" + ".maude"
                            print("Path of the file to be executed : " + path)

                            FILES_FOLDER = BASE_FOLDER + "files/"
                            utils.check_folder_exists(FILES_FOLDER)

                            file_path = FILES_FOLDER + path

                            # Implement artificially the limits
                            labels, dname_chain_length, ns_del = \
                                utils.check_variables(labels=labels, chain_length=dname_chain_length,
                                                      nb_delegations=ns_del, chain_type="DNAME",
                                                      resolver_model=resolver_model)

                            # Create the ns records for intermediary,
                            # the dname chains in the target
                            ns_records_text_in_intermediary, dname_chain_in_target = \
                                utils.ns_del_and_dname_chain_scrubbing(nb_label=labels,
                                                                       dname_chain_length=dname_chain_length,
                                                                       nb_del=ns_del,
                                                                       address_to_be_delegated="'del . 'intermediary . 'com . root",
                                                                       target_address="'target-ans . 'com . root")

                            whole = variant.whole_file(PATH_TO_MAIN_DIR, resolver_model, qmin_deactivated,
                                                       dname_chain_in_target, ns_records_text_in_intermediary)

                            with open(file_path, "w+") as file:
                                file.write(whole)

                            if not watcher.set_values_and_has_changed(nb_delegations=ns_del,
                                                                      dname_chain_length=dname_chain_length,
                                                                      variant_attack_name=variant.name_attack,
                                                                      nb_labels=labels):
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
                                file.write(str(float(amp)) + ",")

    time2 = time.perf_counter()
    print("The files have been created and their execution has been measured in {:.3f} seconds !".format(time2 - time1))


if __name__ == "__main__":
    # QMIN deactivated
    qmin_deactivated = True
    main()

    # QMIN enabled
    qmin_deactivated = False
    main()
