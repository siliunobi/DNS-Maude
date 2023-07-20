#!/usr/bin/env python3
import os
import re
import time

import utils
from model_attack_file import CCV, CCV_QMIN, SubqueriesCCV_Delay, CCV_Delay, CCV_QMIN_Delay
from model_resolver import *
from utils import check_folder_exists, intermediary_nsdelegations_to_target, \
    target_cname_chain, run_file, cname_chain_val_delay, standalone_cname_scrubbing_delay
from watcher import Watcher

"""This file creates and runs files for the attacks Scrubbing +CNAME +QMIN delay.
Those are also called CNAME CHAIN VALIDATION + DELAY."""
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def main():

    scrubbing = True

    PATH_TO_MAIN_DIR = "../../../../.."

    qmin_folder = "qmin_disabled" if qmin_deactivated else "qmin_enabled"

    variants = [CCV_QMIN(), CCV_Delay(),CCV_QMIN_Delay()]  #  [CCV(), CCV_QMIN(), CCV_Delay(), CCV_QMIN_Delay()]

    RANGE_CNAME_LENGTH = range(1, 20+1)
    RANGE_NS_DELEGATIONS = [1]
    RANGE_NS_DELAY = range(0, 1700, 200)

    time1 = time.perf_counter()

    # Creation of the files that will be executed to obtain the results
    for variant in variants:
        # Here if we use sub+ccv, we need to set the number of labels to add to 1
        RANGE_LABELS = [0]  # range(10,11)

        # If qmin is enabled, we must change to a modified version of powerdns
        if type(variant) is CCV_Delay:
            # For delay, use Bind9_18_4() instead of Bind9_18_4_CNAME()
            resolver_models = [utils.which_powerdns(scrubbing, qmin_deactivated), Unbound1_16_0(), Unbound1_10_0(),
                               Bind9_18_4()]

        elif type(variant) is CCV_QMIN_Delay:
            resolver_models = [utils.which_powerdns(scrubbing, qmin_deactivated), Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0_CNAME_BYPASSED(),
                               Bind9_18_4()]
            RANGE_LABELS = [10]
        elif type(variant) is CCV_QMIN:
            resolver_models = [utils.which_powerdns(scrubbing, qmin_deactivated), Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0_CNAME_BYPASSED(),
                               Bind9_18_4()]
            RANGE_LABELS = [10]

        elif type(variant) is CCV:
            resolver_models = [utils.which_powerdns(scrubbing, qmin_deactivated), Unbound1_16_0(), Unbound1_10_0(),
                               Bind9_18_4()]

        print("Currently working with " + variant.name_attack)

        for resolver_model in resolver_models:
            print("#" * 50)
            print("\nResolver model : " + resolver_model.name)

            BASE_FOLDER = variant.folder + "/" + qmin_folder + "/" + resolver_model.folder + "/"
            check_folder_exists(BASE_FOLDER)

            watcher = Watcher()

            for labels in RANGE_LABELS:
                for ns_del in RANGE_NS_DELEGATIONS:

                    # Create/empty the measurement file, we fix the number of delegation and the length of the CNAME chain
                    result_path = "res_" + format(labels, '02d') + "labels_" + \
                                  format(ns_del, '02d') + "nsdel" + ".txt"

                    MEASUREMENTS_FOLDER = BASE_FOLDER + "results/" + "measurements/"
                    check_folder_exists(MEASUREMENTS_FOLDER)
                    relative_path = MEASUREMENTS_FOLDER + result_path

                    # Empty the result file
                    open(relative_path, 'w').close()

                    original_ns_del = ns_del
                    original_labels = labels

                    if type(variant) is CCV_Delay or type(variant) is CCV_QMIN_Delay:
                        # to check this
                        cname_chain_length = original_cname_chain_length = 20

                        for ns_delay in RANGE_NS_DELAY:
                            path = format(ns_del, '02d') + "nsdel_" + format(original_cname_chain_length,
                                                                             '02d') + "cnamelength_" + \
                                   format(ns_delay, '03d') + "ns_delay_" + \
                                   format(original_labels, '02d') + "labels" + ".maude"
                            print("Path of the file to be executed : " + path)

                            FILES_FOLDER = BASE_FOLDER + "files/"
                            check_folder_exists(FILES_FOLDER)
                            file_path = FILES_FOLDER + path

                            labels, cname_chain_length, ns_del = \
                                utils.check_variables(labels=labels, chain_length=cname_chain_length,
                                                      nb_delegations=ns_del, chain_type="CNAME",
                                                      resolver_model=resolver_model)

                            labels = original_labels

                            # Create the query from the client and the cname chain target to put in the target
                            query_from_client, cname_chain_in_target = \
                                utils.standalone_cname_scrubbing_delay(nb_labels=labels, cname_chain_length=cname_chain_length -1, target_address="'target-ans . 'com . root")

                            # There is no intermediary
                            whole = variant.whole_file(PATH_TO_MAIN_DIR, resolver_model, qmin_deactivated, ns_delay,
                                                       query_from_client, cname_chain_in_target)


                            # Write the text in a file
                            with open(file_path, "w+") as file:
                                file.write(whole)

                            # Run the file
                            out = run_file(file_path)

                            # Take the first value of amplification
                            amp = re.search(r"FiniteFloat: (\d+.\d+(e\+\d)?)", out).group(1)
                            print(amp)

                            print("=" * 30 + "\n")

                            # We write on each row a new value corresponding to the amplification factor
                            with open(relative_path, "a+") as file:
                                # Convert the scientific notation to float
                                file.write(str(float(amp)) + ",")

                    else:
                        # For CCV and CCVQMIN
                        for cname_chain_length in RANGE_CNAME_LENGTH:

                            # First create the path of the files that will be executed with the initial parameters
                            # those can be modified afterwards to satisfy to the limit of the resolvers
                            path = format(original_ns_del, '02d') + "nsdel_" + format(cname_chain_length,
                                                                             '02d') + "cnamelength_" + \
                                   format(original_labels, '02d') + "labels" + ".maude"
                            print("Path of the file to be executed : " + path)

                            FILES_FOLDER = BASE_FOLDER + "files/"
                            check_folder_exists(FILES_FOLDER)
                            file_path = FILES_FOLDER + path

                            # Implement the artificial limits
                            labels, cname_chain_length, ns_del = utils.check_variables(labels, cname_chain_length,
                                                                                       ns_del, "CNAME", resolver_model)

                            # Should not change anything as QMIN limit is enabled directly in the file
                            labels = original_labels

                            # Create the records leading to the target
                            query_from_client, cname_chain_in_target = utils.standalone_cname_scrubbing_delay(nb_labels=labels,cname_chain_length=cname_chain_length-1, target_address="'target-ans . 'com . root")

                            whole = variant.whole_file(PATH_TO_MAIN_DIR, resolver_model, qmin_deactivated,query_from_client, cname_chain_in_target)

                            # # Write the text in a file
                            with open(file_path, "w+") as file:
                                file.write(whole)

                            if not watcher.set_values_and_has_changed(nb_delegations=ns_del,
                                                                      cname_chain_length=cname_chain_length,
                                                                      variant_attack_name=variant.name_attack,
                                                                      nb_labels=labels):
                                with open(relative_path, "a+") as file:
                                    # Convert the scientific notation to float
                                    file.write(str(float(amp)) + ",")
                                # Continue as it obtains the same previous value
                                print("DID not need to run the file, as the same parameters are being used ")
                                continue

                            # Run the file
                            out = run_file(file_path)

                            # Take the first value of amplification
                            amp = re.search(r"FiniteFloat: (\d+.\d+(e\+\d)?)", out).group(1)
                            print(amp)

                            print("=" * 30 + "\n")

                            # We write on each row a new value corresponding to the amplification factor
                            with open(relative_path, "a+") as file:
                                # Convert the scientific notation to float
                                file.write(str(float(amp)) + ",")

            print(
                "Creating the file and measuring the results has been done for this resolver model.\n" + "#" * 30 + "\n")

    time2 = time.perf_counter()
    print("The files have been created and their execution has been measured in {:.3f} seconds !".format(time2 - time1))


if __name__ == "__main__":
    # QMIN deactivated
    qmin_deactivated = True
    main()

    # QMIN enabled
    qmin_deactivated = False
    main()
