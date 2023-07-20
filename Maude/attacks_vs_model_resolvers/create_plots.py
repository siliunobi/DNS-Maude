#!/usr/bin/env python3
import os
import time

import matplotlib.pyplot as plt
import numpy as np

import utils
from model_resolver import *


def create_plots(list_values, filename, folder_figures, implementation, attack_name):
    x = range(1, len(list_values) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = \
        utils.search_missing_attributes_cname(filename, missing_attributes, ns_del, cname_chain_length, nb_labels)

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
    ax.set_ylim(0, 1700)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        'Amplification factor c/nameserver with {attack} \n Fixed values : {vars} \n Resolver model: {impl}, workBudget: {budget}'.format(
            attack=attack_name, vars=vars, impl=implementation.name, budget=implementation.workBudget), fontsize=11)

    # ax.set_title('Amplification factor c/res with Sub+CCV+QMIN \n Fixed values : #Del={}, CNAME_length={}'.format(str(ns_del), str(cname_chain_length)), fontsize = 12)
    # fig.set_yticks([float(i) for i in list_values])

    ax.grid()
    ax.plot(x, list_values, marker='o', c='g')

    plot_path = folder_figures + "fig_" + filename.split(".")[0] + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)
        # print("removed plot")

    def max_point_annot(x, y, ax=None):
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

    max_point_annot(x, list_values)

    fig.savefig(plot_path)
    plt.close()


def main():
    resolvers_model = [Unbound1_10_0(), Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0(), Unbound1_16_0_CNAME_BYPASSED(),
                       PowerDNS4_7_0()]

    qmin_folder = "qmin_enabled/"
    attack_folder = "sub-ccv-qmin-a/" + qmin_folder
    attack_folders = [attack_folder]
    print("Start of creation of the plots  for the attack {}....".format(attack_folder[:-1]))

    time1 = time.perf_counter()

    for attack_folder in attack_folders:
        for resolver_model in resolvers_model:

            FOLDER_RESULTS = attack_folder + "{}/results/".format(resolver_model.folder)
            FOLDER_RESULTS_MEASUREMENTS = FOLDER_RESULTS + "measurements/"
            FOLDER_RESULTS_FIGURES = FOLDER_RESULTS + "figures/"

            utils.check_folder_exists(FOLDER_RESULTS)
            utils.check_folder_exists(FOLDER_RESULTS_MEASUREMENTS)
            utils.check_folder_exists(FOLDER_RESULTS_FIGURES)

            for filename in os.listdir(FOLDER_RESULTS_MEASUREMENTS):
                f = os.path.join(FOLDER_RESULTS_MEASUREMENTS, filename)
                # checking if it is a new_file
                if os.path.isfile(f):
                    new_file = open(f, "r")
                    for row in new_file:
                        list_values = row.split(",")[:-1]
                    new_file.close()
                    print("new_file " + f)
                    create_plots([float(i) for i in list_values], filename, FOLDER_RESULTS_FIGURES, resolver_model,
                                 attack_folder[:-1])

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


if __name__ == "__main__":
    main()
