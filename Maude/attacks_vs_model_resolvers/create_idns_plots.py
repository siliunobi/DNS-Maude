#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt
import time
import numpy as np
import re
from model_resolver import *
from model_attack_file import *
import utils
import plot_utils

implementation_name = "GENERAL"
configWorkBudget = "5000"
FOLDER_RESULTS = "creation_idns/" + "results/"
FOLDER_RESULTS_MEASUREMENTS = FOLDER_RESULTS + "measurements/"


def create_plots(list_values, filename, implementation, variant, folder_results):
    x = range(1, len(list_values) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, dname_chain_length, nb_labels = \
        utils.search_missing_attributes_cname(filename,
                                              missing_attributes,
                                              ns_del,
                                              cname_chain_length,
                                              nb_labels)

    try:
        assert (len(missing_attributes) == 1)
    except:
        print("Number of missing attributes is not correct.\n Aborting ... ")
        return

    x_labels = {"ns_del": "# Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('Amplification factor', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 100)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        'Amplification factor c/{victim} with {name_attack} \n Fixed values : {vars} \n Resolver: {impl}, workBudget: {budget}'.format(
            victim=variant.victim, name_attack=variant.name_attack, vars=vars, impl=implementation.name,
            budget=implementation.workBudget), fontsize=11)

    # ax.set_title('Amplification factor c/res with Sub+CCV+QMIN \n Fixed values : #Del={}, CNAME_length={}'.format(str(ns_del), str(cname_chain_length)), fontsize = 12)
    # fig.set_yticks([float(i) for i in list_values])

    ax.grid()
    ax.plot(x, list_values, marker='o', c='g')

    utils.check_folder_exists(folder_results + "figures/")
    plot_path = folder_results + "figures/" + "fig_" + filename.split(".")[0] + ".jpg"

    if os.path.exists(plot_path):
        os.remove(plot_path)
        # print("removed plot")

    def annot_max(x, y, ax=None):
        xmax = x[np.argmax(y)]
        ymax = max(y)
        text = "Max : x={:.0f}, y={:.2f}".format(xmax, ymax)
        if not ax:
            ax = plt.gca()
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops = dict(arrowstyle="->")
        kw = dict(xycoords='data', textcoords="axes fraction",
                  arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
        ax.annotate(text, xy=(xmax, ymax), xytext=(0.60, 0.96), **kw)

    annot_max(x, list_values)

    fig.savefig(plot_path)
    plt.close()


def create_combined_plots(list_list_values, filename, implementation_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    match = re.search(r"(\d+)nsdel", filename)
    if match is None:
        print("Missing attribute is the number of delegations. This is the number that is variable\n")
        missing_attributes.append("ns_del")
    else:
        ns_del = match.group(1)

    match = re.search(r"(\d+)cnamelength", filename)
    if match is None:
        print("Missing attribute is the length of the CNAME chain. This is the number that is variable\n")
        missing_attributes.append("cname_chain_length")
    else:
        cname_chain_length = match.group(1)

    match = re.search(r"(\d+)labels", filename)
    if match is None:
        print("Missing attribute is the number of labels. This is the number that is variable\n")
        missing_attributes.append("nb_labels")
    else:
        nb_labels = match.group(1)

    try:
        assert (len(missing_attributes) == 1)
    except:
        print("Number of missing attributes is not correct.\n Aborting ... ")
        return

    x_labels = {"ns_del": "Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('Amplification factor', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 100)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    # The victim is dependent on the variant chosen first -> so victim here is generic
    ax.set_title('Amplification factor c/victim with Sub+CCV+QMIN \n Fixed values : {vars}'.format(vars=vars),
                 fontsize=11)

    # ax.set_title('Amplification factor c/res with Sub+CCV+QMIN \n Fixed values : #Del={}, CNAME_length={}'.format(str(ns_del), str(cname_chain_length)), fontsize = 12)
    # fig.set_yticks([float(i) for i in list_values])

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_" + filename.split(".")[0] + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)
        # print("removed plot")

    def max_point_annot(x, y, name, frac, ax=None):
        xmax = x[np.argmax(y)]
        ymax = max(y)
        text = "{}\nMax at {:.2f}".format(name, ymax)
        if not ax:
            ax = plt.gca()
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops = dict(arrowstyle="->")
        kw = dict(xycoords='data', textcoords="axes fraction",
                  arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
        ax.annotate(text, xy=(xmax, ymax), xytext=(0.30, max(0.96 - frac, 0.3)), **kw)

    for i in range(0, len(implementation_names)):
        list_values = list_list_values[i]
        max_point_annot(x, list_values, implementation_names[i], i / len(list_list_values))

    plt.legend(implementation_names)

    plt.savefig(plot_path)
    plt.close()

    del fig


def main():
    implementations = [ModelResolver(), Unbound1_10_0(), Unbound1_16_0(), PowerDNS4_7_0()]

    variants = [IDNSVariant1(), IDNSVariant2(), IDNSVariant3()]
    variants_folder = []

    print("Start of creation of the plots  ....")
    time1 = time.perf_counter()

    for implementation in implementations:

        for variant in variants:
            FOLDER_RESULTS = variant.folder + "/" + implementation.folder + "/results/"
            FOLDER_RESULTS_MEASUREMENTS = FOLDER_RESULTS + "measurements/"
            utils.check_folder_exists(FOLDER_RESULTS_MEASUREMENTS)

            for filename in os.listdir(FOLDER_RESULTS_MEASUREMENTS):
                f = os.path.join(FOLDER_RESULTS_MEASUREMENTS, filename)
                # checking if it is a file
                if os.path.isfile(f):
                    file = open(f, "r")
                    for row in file:
                        list_values = row.split(",")[:-1]
                    file.close()
                    print("f " + f + " values : ")  # + list_values)
                    create_plots([float(i) for i in list_values], filename, implementation, variant, FOLDER_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_combined():
    time1 = time.perf_counter()
    implementations = [ModelResolver(), Unbound1_10_0(), Unbound1_16_0(), PowerDNS4_7_0()]
    variants = [IDNSVariant1(), IDNSVariant2(), IDNSVariant3()]

    for variant in variants:

        print("VICTIM + " + variant.victim)

        FOLDER_COMBINED_RESULTS = variant.folder + "/combined/"
        utils.check_folder_exists(FOLDER_COMBINED_RESULTS)

        print("#" * 20 + "\n")
        print("Start of the creation of the combined plots for the attack {} ....\n".format(variant.name_attack))

        implementation_names = [imp.folder for imp in implementations]

        FOLDERS_RESULTS = [variant.folder + "/" + "{}/results/".format(name) for name in implementation_names]
        FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
        for i in range(0, len(implementations)):
            utils.check_folder_exists(FOLDERS_RESULTS[i])
            utils.check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

        # Look for all the measurements files in the first resolver folder
        for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
            files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

            # Check that the same files exist in the other resolvers' folders
            if not all(os.path.isfile(f) for f in files):
                print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
                continue

            list_list_values = plot_utils.extract_values_from_files(files)

            # Check that all the lists have the same size
            utils.check_lists_size(list_list_values)

            lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

            create_combined_plots(lists_to_float, filename, implementation_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


if __name__ == "__main__":
    main()
    main_combined()
