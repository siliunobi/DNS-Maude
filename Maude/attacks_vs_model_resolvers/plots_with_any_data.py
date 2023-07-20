#!/usr/bin/env python3

import csv
import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from create_sub_ccv_qmin_files import *
from utils import *
from plot_utils import save_high_quality, text_plot_qmin
from pathlib import Path

'''This file is used to plot my resolver models curves against the real implementation curves.'''

DATA_L_FOLDER = "data/l/"
DATA_J_FOLDER = "data/j/"


def read_to_float(filename):
    """Reads files and converts the values to float"""
    with open(filename, "r") as f:
        values = f.readlines()[0][:-1].split(",")
        values = [float(i) for i in values]

    return values


def read_test_j_files(filename, resolver_name, target_value, order_name):

    df = pd.read_csv(filename)
    # print(df.head)
    resolver = df.loc[df['resolver'] == resolver_name]
    # print(str(type(resolver)))
    resolver = resolver.sort_values(by=order_name)
    return resolver[target_value].astype(float).to_list()


def read_j_files(filename, resolver_name, target_value, order_name):
    """Read the files created by the local testbed of j.
Requires the specific name of the resolver, the kind of value we want ('y' corresponds to the number of queries
or time, and the way we order the values according to ('x') or the number of the delegations or the delays."""
    df = pd.read_csv(filename)

    resolver = df.loc[df['hue'] == resolver_name]
    resolver = resolver.sort_values(by=order_name)

    return resolver[target_value].astype(float).to_list()


def c():
    print("hello")
    implementation_names = ["Model Unbound1_10_0", "Unbound1_10_0", "Model Unbound1_16_0", "Unbound1_16_0",
                            "Model PowerDNS4_7_0", "PowerDNS4_7_0"]
    # Values for all resolvers models and real implementation using CNAME_length 17,, NB_labels 10, and a range of NS delegation [1,10]
    values_model_unb1_10 = [82.0, 164.0, 246.0, 328.0, 410.0, 492.0, 574.0, 656.0, 738.0, 820.0]
    values_model_unb1_16 = [112.0, 224.0, 336.0, 448.0, 560.0, 672.0, 672.0, 672.0, 672.0, 672.0]
    values_model_pdns4_7 = [99.0, 99.0, 99.0, 99.0, 99.0, 99.0, 99.0, 99.0, 99.0, 99.0]

    fields = []
    rows = []

    with open("old_data.csv") as csv_file:
        csv_read = csv.reader(csv_file, delimiter=",")

        fields = next(csv_read)

        for row in csv_read:
            rows.append(row)

    rows = rows[0:10]

    index_u1_16 = 1  # fields.find("Unbound 1.10.0")
    values_unb1_16 = [float(row[index_u1_16]) for row in rows]
    print(values_unb1_16)
    index_u1_10 = 5  # fields.find("Unbound 1.16.0")
    values_unb1_10 = [float(row[index_u1_10]) for row in rows]
    index_pdns = 9  # fields.find("PowerDNS 4.7.0 with IPv6 enabled")
    values_pdns4_7 = [float(row[index_pdns]) for row in rows]

    print(implementation_names)
    list_list_values = [values_model_unb1_10, values_unb1_10, values_model_unb1_16, values_unb1_16,
                        values_model_pdns4_7, values_pdns4_7]

    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 10

    ax.set_xlabel("Number of delegaions", fontsize=12)
    ax.set_ylabel('Amplification factor', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 1700)

    # fixed_vars = {"ns_del" : "#Del={}".format(str(ns_del)), "cname_chain_length" : "CNAME_length={}".format(str(cname_chain_length)), "nb_labels" : "#Labels={}".format(str(nb_labels))}
    fixed = ["CNAME_length={}".format(str(cname_chain_length)), "#Labels={}".format(str(nb_labels))]
    vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title('Amplification factor c/nameserver with Sub+CCV+QMIN \n Fixed values : {vars}'.format(vars=vars),
                 fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = "fig_combined_with_old_data.jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)
        # print("removed plot")

    plt.legend(implementation_names)

    plt.savefig(plot_path)
    plt.close()


def plot_subccvqmin_unbound1_10_0():
    implementation_names = ["Model Unbound 1.10.0, cname limit disabled", "Unbound 1.10.0"]

    values_model_unb1_10_without_climit = [162.0, 324.0, 486.0, 648.0, 810.0, 972.0, 1134.0, 1296.0, 1458.0, 1620.0]
    values_real_unb1_10_aaaa = []

    fields = []
    rows = []

    with open("old_data.csv") as csv_file:
        csv_read = csv.reader(csv_file, delimiter=",")

        fields = next(csv_read)

        for row in csv_read:
            rows.append(row)

    rows = rows[0:10]

    values_real_unb1_10_aaaa = [float(row[5]) for row in rows]

    print(implementation_names)
    list_list_values = [values_model_unb1_10_without_climit, values_real_unb1_10_aaaa]

    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 10

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('Amplification factor', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 1700)

    # fixed_vars = {"ns_del" : "#Del={}".format(str(ns_del)), "cname_chain_length" : "CNAME_length={}".format(str(cname_chain_length)), "nb_labels" : "#Labels={}".format(str(nb_labels))}
    fixed = ["CNAME_length={}".format(str(cname_chain_length)), "#Labels={}".format(str(nb_labels))]
    vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title('Amplification factor c/nameserver with Sub+CCV+QMIN \n Fixed values : {vars}'.format(vars=vars),
                 fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = "fig_subccvqmin_unbound1_10_0.jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

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

    plt.legend(implementation_names)

    plt.savefig(plot_path)
    plt.close()


def plot_subccvqmin_unbound1_16_0():
    implementation_names = ["Model Unbound 1.16.0, cname limit disabled", "Unbound 1.16.0"]

    with open("sub-ccv-qmin-a/unbound1_16_0_cname_bypassed/results/measurements/res_10labels_17cnamelength.txt") as f:
        values_model_unb1_16_without_climit = f.readlines()[0][:-1].split(",")
        values_model_unb1_16_without_climit = [float(i) for i in values_model_unb1_16_without_climit]

    # values_model_unb1_16_without_climit = [162.0,324.0,486.0,648.0,810.0,972.0,972.0,972.0,972.0,972.0]
    values_real_unb1_16_aaaa = []

    fields = []
    rows = []

    with open(DATA_L_FOLDER + "subccvqmin_data.csv") as csv_file:
        csv_read = csv.reader(csv_file, delimiter=",")

        fields = next(csv_read)

        for row in csv_read:
            rows.append(row)

    rows = rows[0:10]

    values_real_unb1_16_aaaa = [float(row[1]) for row in rows]

    print(implementation_names)
    list_list_values = [values_model_unb1_16_without_climit, values_real_unb1_16_aaaa]

    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 10

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 1700)

    # fixed_vars = {"ns_del" : "#Del={}".format(str(ns_del)), "cname_chain_length" : "CNAME_length={}".format(str(cname_chain_length)), "nb_labels" : "#Labels={}".format(str(nb_labels))}
    fixed = ["CNAME_length={}".format(str(cname_chain_length)), "#Labels={}".format(str(nb_labels))]
    vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title('Queries sent to victim nameserver with Sub+CCV+QMIN \n Fixed values : {vars}'.format(vars=vars),
                 fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = "fig_subccvqmin_unbound1_16_0.jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

    plt.legend(implementation_names)

    plt.savefig(plot_path)
    plt.close()


def plot_subccvqmin():
    '''Recreates the figure 7.5'''

    list_markers = itertools.cycle(("x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-"))  # ":"))
    list_colors = itertools.cycle(("red", "red", "b", "b", "orange", "orange"))

    implementation_names = ["Model Unbound 1.10.0, cname limit disabled", "Unbound 1.10.0",
                            "Model Unbound 1.16.0, cname limit disabled", "Unbound 1.16.0", "Model PowerDNS 4.7.0",
                            "PowerDNS 4.7.0"]

    values_model_u1_10 = read_to_float(
        "sub-ccv-qmin-a/unbound1_10_0_cname_bypassed/results/measurements/res_10labels_17cnamelength.txt")
    # [9.0,18.0,27.0,36.0,45.0,54.0,63.0,72.0,81.0,90.0]#[10.0,20.0,30.0,40.0,50.0,60.0,70.0,80.0,90.0,100.0]

    values_model_u1_16 = read_to_float(
        "sub-ccv-qmin-a/unbound1_16_0_cname_bypassed/results/measurements/res_10labels_17cnamelength.txt")

    # values_model_u1_16 = [12.0,24.0,36.0,48.0,60.0,72.0,72.0,72.0,72.0,72.0]#[13.0,26.0,39.0,52.0,65.0,78.0,78.0,78.0,78.0,78.0]

    values_model_pdns4_7 = read_to_float(
        "sub-ccv-qmin-a/powerDNS4_7_0/results/measurements/res_10labels_17cnamelength.txt")

    fields = []
    rows = []

    with open(DATA_L_FOLDER + "subqueries_cname_validation_qmin_L.csv") as csv_file:
        csv_read = csv.reader(csv_file, delimiter=",")

        fields = next(csv_read)

        for row in csv_read:
            rows.append(row)

    rows = rows[0:10]

    print(fields)

    # Implementation values
    values_u1_10 = [float(row[fields.index("Unbound 1.10.0 (to example.com nameserver)")]) for row in rows]
    values_u1_16 = [float(row[fields.index("Unbound 1.16.0 (to example.com nameserver)")]) for row in rows]
    values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0 with IPv6 enabled (to example.com nameserver)")]) for row
                      in rows]

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7]

    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 10

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 1800)

    # fixed_vars = {"ns_del" : "#Del={}".format(str(ns_del)), "cname_chain_length" : "CNAME_length={}".format(str(cname_chain_length)), "nb_labels" : "#Labels={}".format(str(nb_labels))}
    fixed = ["CNAME_length={}".format(str(cname_chain_length)), "#Labels={}".format(str(nb_labels))]
    vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+CCV+QMIN \n Fixed values : {vars} \n Reproduction of Figure 7.5'.format(
            vars=vars), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    plot_path = "fig_sub_ccv_qmin_resolver_model_7-5.jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

    plt.legend(implementation_names)
    print(list_list_values)
    plt.savefig(plot_path)
    plt.close()


def plot_subccvdelay_powerdns():

    attack_folder = "sub-ccv-delay"
    list_markers = itertools.cycle(("x", "d", "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-", ":"))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))

    implementation_names = ["Model PowerDNS 4.7.0", "L Model PowerDNS", "PowerDNS 4.7.0", "MODEL CNAME limit + 1"]

    values_model_pdns4_7 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")]

    values_model_mod = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/powerDNS4_7_0_mod/results/measurements/res_00labels_17cnamelength.txt")]

    fields = []
    rows = []

    with open(DATA_L_FOLDER + "delayed_cname_validation.csv") as csv_file:
        csv_read = csv.reader(csv_file, delimiter=",")

        fields = next(csv_read)

        for row in csv_read:
            rows.append(row)

    rows = rows[0:10]

    print(fields)

    # Beware "chain length 9, Model" is "Model; chain length 9"
    values_model_pdns4_7_L = [
        float(row[fields.index("Model; chain length 12 with overall timeout 12secs (corrected; seconds)")]) for row in
        rows]

    # Implementation values
    values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0")]) for row in rows]

    list_list_values = [values_model_pdns4_7, values_model_pdns4_7_L, values_pdns4_7, values_model_mod]

    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Artificial delay (ms or time unit)", fontsize=12)
    ax.set_ylabel('Duration of the query (s)', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 15)

    # fixed_vars = {"ns_del" : "#Del={}".format(str(ns_del)), "cname_chain_length" : "CNAME_length={}".format(str(cname_chain_length)), "nb_labels" : "#Labels={}".format(str(nb_labels))}
    fixed = ["CNAME_length={}".format(str(cname_chain_length)), "#Labels={}".format(str(nb_labels))]
    vars = ", ".join(fixed)
    ax.set_title(
        'Duration of queries sent to victim nameserver with Sub+CCV+Delay (slow DNS) \n Fixed values : {vars}'.format(
            vars=vars), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    plot_path = "fig_sub_ccv_delay_powerdns.jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

    plt.legend(implementation_names)
    print(list_list_values)
    plt.savefig(plot_path)
    plt.close()

    del fig


# SUBQUERIES UNCHAINED CNAME
def plot_sub_unchained_cname_models():
    attack_folder = SubqueriesUnchainedCNAME().folder
    list_markers = itertools.cycle(("x", "d",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    implementation_names = ["Model Unbound 1.10.0", "L Model Unbound 1.10.0", "Model Unbound 1.16.0",
                            "L Model Unbound 1.16.0", "Model PowerDNS 4.7.0", "L Model PowerDNS 4.7.0"]
    # No need for  "Model BIND 9.18.4", "L Model BIND 9.18.4"] as there was no model of this

    values_model_u1_10 = [i for i in read_to_float(
        attack_folder + "/unbound1_10_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_u1_16 = [i for i in read_to_float(
        attack_folder + "/unbound1_16_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_pdns4_7 = [i for i in read_to_float(
        attack_folder + "/powerDNS4_7_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")]
    # values_model_bind = [i for i in read_to_float(attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")]

    fields = []
    rows = []

    with open(DATA_L_FOLDER + "subqueries_unchained.csv") as csv_file:
        csv_read = csv.reader(csv_file, delimiter=",")

        fields = next(csv_read)

        for row in csv_read:
            rows.append(row)

    rows = rows[0:10]

    print(fields)

    values_model_u1_10_L = [float(row[fields.index("Model; chain length 9 (to example.com nameserver)")]) for row in
                                rows]
    values_model_u1_16_L = [
        float(row[fields.index("Model maxFetch(6); chain length 12 (to example.com nameserver)")]) for row in rows]
    values_model_pdns4_7_L = [
        float(row[fields.index("Model work limit 100; chain length 11 (to example.com nameserver)")]) for row in rows]

    # No values for BIND resolver for the attack subqueries unchaied + Cname
    # values_model_bind_L = [0 for i in range(len(rows))]

    list_list_values = [values_model_u1_10, values_model_u1_10_L, values_model_u1_16, values_model_u1_16_L,
                        values_model_pdns4_7, values_model_pdns4_7_L]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 110)


    vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+Unchained with CNAME \n using MODELS; Fixed values : {vars} \n and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_unchained_cname_models"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_unchained_cname():
    '''Plots my models versus the real implementations.
    Recreates the figure 7.2'''

    # attack_folder = "sub-unchained-cname"
    # QMIN_DEACTIVATED = True
    attack_folder = SubqueriesUnchainedCNAME().folder
    list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.0"
    if QMIN_DEACTIVATED:
        powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")
    values_model_bind = read_to_float(
        attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")

    if QMIN_DEACTIVATED:
        j_file = DATA_J_FOLDER + "/subquery+CNAME/data.csv"
        values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
        values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
        values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
        values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')
    else:
        fields = []
        rows = []

        with open(DATA_L_FOLDER + "subqueries_unchained.csv") as csv_file:
            csv_read = csv.reader(csv_file, delimiter=",")

            fields = next(csv_read)

            for row in csv_read:
                rows.append(row)

        rows = rows[0:10]

        print(fields)

        values_u1_10 = [float(row[fields.index("Unbound 1.10.0 with IPv6 disabled (to example.com nameserver)")]) for
                        row in rows]
        values_u1_16 = [float(row[fields.index("Unbound 1.16.0 with IPv6 disabled (to example.com nameserver)")]) for
                        row in rows]
        values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0 (to example.com nameserver)")]) for row in rows]
        values_bind = [float(row[fields.index("BIND 9.18.4 with IPv6 disabled (to example.com nameserver)")]) for row in
                       rows]

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind, values_bind]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 110)


    vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+Unchained with CNAME \n Fixed values : {vars}and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_unchained_cname_7-2"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


# SUBQUERIES + CNAME SCRUBBING
def plot_sub_cname_scrubbing_models():
    # QMIN_DEACTIVATED = True
    attack_folder = SubqueriesCCV().folder
    list_markers = itertools.cycle(("x", "p"))  # "P", "p"))#"*"))#,"s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
    list_colors = itertools.cycle(("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green"))

    implementation_names = ["Model Unbound 1.10.0", "L Unbound 1.10.0", "Model Unbound 1.16.0",
                            "L Unbound 1.16.0", "Model PowerDNS 4.7.0",
                            "L PowerDNS 4.7.0"]  # , "Model BIND 9.18.4", "BIND 9.18.4"]  #["Model Unbound 1.10.0", "L Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "L Unbound 1.16.0", "Unbound 1.16.0", "Model PowerDNS 4.7.0", "L PowerDNS 4.7.0", "PowerDNS 4.7.0"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")

    fields = []
    rows = []

    with open(DATA_L_FOLDER + "subqueries_cname_validation_L.csv") as csv_file:
        csv_read = csv.reader(csv_file, delimiter=",")

        fields = next(csv_read)

        for row in csv_read:
            rows.append(row)

    rows = rows[0:10]

    print(fields)

    # Beware "chain length 9, Model" is "Model; chain length 9"
    values_model_u1_10_L = [float(row[fields.index("Model; chain length 9 (to example.com nameserver)")]) for row in
                                rows]
    values_model_u1_16_L = [
        float(row[fields.index("Model maxFetch(6); chain length 12 (to example.com nameserver)")]) for row in rows]
    values_model_pdns4_7_L = [
        float(row[fields.index("Model work limit 100; chain length 11 (to example.com nameserver)")]) for row in rows]

    # Real implementation values
    # values_u1_10 = [float(row[fields.index("Unbound 1.10.0 with IPv6 disabled (to example.com nameserver)")]) for row in rows]
    # values_u1_16 = [float(row[fields.index("Unbound 1.16.0 with IPv6 disabled (to example.com nameserver)")]) for row in rows]
    # values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0 (to example.com nameserver)")]) for row in rows]

    list_list_values = [values_model_u1_10, values_model_u1_10_L, values_model_u1_16, values_model_u1_16_L,
                        values_model_pdns4_7,
                        values_model_pdns4_7_L]  # [values_model_u1_10, values_model_u1_10_L, values_u1_10, values_model_u1_16, values_model_u1_16_L, values_u1_16, values_model_pdns4_7, values_model_pdns4_7_L, values_pdns4_7]

    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 200)


    vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+CNAME scrubbing \n Fixed values : {vars} and {qmin}\n Reproduction of Figure 7.4'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_cname_scrubbing_models"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    # plot_path = "fig_sub_ccv_L_resolver_model_7-4.jpg"
    # if os.path.exists(plot_path):
    #     os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_cname_scrubbing():
    '''Recreates the figure 7.4'''

    attack_folder = SubqueriesCCV().folder
    list_markers = itertools.cycle(("x", "p"))  # "P", "p"))#"*"))#,"s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-."))  # ,":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.0"
    if QMIN_DEACTIVATED:
        powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4",
                            "BIND 9.18.4"]  # ["Model Unbound 1.10.0", "L Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "L Unbound 1.16.0", "Unbound 1.16.0", "Model PowerDNS 4.7.0", "L PowerDNS 4.7.0", "PowerDNS 4.7.0"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_bind9_18_4 = read_to_float(
        attack_folder + "/bind9_18_4_cname/results/measurements/res_00labels_17cnamelength.txt")

    if QMIN_DEACTIVATED:

        j_file = DATA_J_FOLDER + "subquery+CNAME+scrubbing/data.csv"
        values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
        values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
        values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
        values_bind9_18_4 = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')
    else:
        fields = []
        rows = []

        with open(DATA_L_FOLDER + "subqueries_cname_validation_L.csv") as csv_file:
            csv_read = csv.reader(csv_file, delimiter=",")

            fields = next(csv_read)

            for row in csv_read:
                rows.append(row)

        rows = rows[0:10]

        print(fields)
        #
        # # Beware "chain length 9, Model" is "Model; chain length 9"
        # values_model_u1_10_L  = [float(row[fields.index("Model; chain length 9 (to example.com nameserver)")]) for row in rows]
        # values_model_u1_16_L  = [float(row[fields.index("Model maxFetch(6); chain length 12 (to example.com nameserver)")]) for row in rows]
        # values_model_pdns4_7_L = [float(row[fields.index("Model work limit 100; chain length 11 (to example.com nameserver)")]) for row in rows]

        # Real implementation values
        values_u1_10 = [float(row[fields.index("Unbound 1.10.0 with IPv6 disabled (to example.com nameserver)")]) for
                        row in rows]
        values_u1_16 = [float(row[fields.index("Unbound 1.16.0 with IPv6 disabled (to example.com nameserver)")]) for
                        row in rows]
        values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0 (to example.com nameserver)")]) for row in rows]
        values_bind9_18_4 = [float(row[fields.index("BIND 9.18.4 with IPv6 disabled (to example.com nameserver)")]) for
                             row in rows]

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind9_18_4, values_bind9_18_4]

    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 200)


    vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)

    ax.set_title(
        '# Queries sent to victim nameserver with Sub+CNAME scrubbing \n Fixed values : {vars} and {qmin}\n Reproduction of Figure 7.4'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_cname_scrubbing_7-4"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

    # plot_path = "fig_sub_ccv_L_resolver_model_7-4.jpg"
    # if os.path.exists(plot_path):
    #     os.remove(plot_path)
    #     #print("removed plot")



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


# SUBQUERIES + CNAME SCRUBBING + DELAY
def plot_sub_cname_scrubbing_delay_models():
    '''Plots my models for Subqueries + CNAME scrubbing + Delay vs L'''
    '''It looks like in the previous models QMIN was enabled -> if disabled, it affects the results.'''

    attack_folder = SubqueriesCCV_Delay().folder
    # attack_folder = "sub-ccv-delay"

    list_markers = itertools.cycle(("x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-"))  # " :"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    implementation_names = ["Model Unbound 1.16.0", "L Unbound 1.16.0", "Model PowerDNS 4.7.0",
                            "L PowerDNS 4.7.0", "Model BIND 9.18.4",
                            "L BIND 9.18.4"]  # "Model Unbound 1.10.0", "Unbound 1.10.0"] <- there was no value computed

    # values_model_u1_10 = read_to_float(attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17dnamelength.txt")
    # [9.0,18.0,27.0,36.0,45.0,54.0,63.0,72.0,81.0,90.0]#[10.0,20.0,30.0,40.0,50.0,60.0,70.0,80.0,90.0,100.0]

    values_model_u1_16 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_pdns4_7 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_bind9_18_4 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/bind9_18_4/results/measurements/res_00labels_17cnamelength.txt")]

    fields = []
    rows = []

    with open(DATA_L_FOLDER + "delayed_cname_validation.csv") as csv_file:
        csv_read = csv.reader(csv_file, delimiter=",")

        fields = next(csv_read)

        for row in csv_read:
            rows.append(row)

    rows = rows[0:10]

    print(fields)

    # Beware "chain length 9, Model" is "Model; chain length 9"
    # values_model_u1_10_L  = [float(row[fields.index("Model; chain length 9 (to example.com nameserver)")]) for row in rows]
    values_model_u1_16_L = [float(row[fields.index("Model; chain length 12 (corrected; seconds)")]) for row in rows]
    values_model_pdns4_7_L = [
        float(row[fields.index("Model; chain length 12 with overall timeout 12secs (corrected; seconds)")]) for row in
        rows]
    values_model_bind9_18_4_L = [float(row[fields.index("Model; chain length 17 (corrected; seconds)")]) for row in
                                     rows]

    # Implementation values
    # values_u1_10 = [float(row[fields.index("Unbound 1.10.0 (to example.com nameserver)")]) for row in rows]
    values_u1_16 = [float(row[fields.index("Unbound 1.16.0")]) for row in rows]
    values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0")]) for row in rows]
    values_bind9_18_4 = [float(row[fields.index("BIND 9.18.4")]) for row in rows]

    list_list_values = [values_model_u1_16, values_model_u1_16_L, values_model_pdns4_7, values_model_pdns4_7_L,
                        values_model_bind9_18_4,
                        values_model_bind9_18_4_L]  # [values_model_u1_16,  values_u1_16, values_model_pdns4_7, values_pdns4_7, values_bind9_18_4, values_bind9_18_4]

    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Artificial delay (ms or time unit)", fontsize=12)
    ax.set_ylabel('Duration of the query (s)', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 25)


    vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        'Duration of queries sent to victim nameserver with Sub+CNAME scrubbing+Delay (slow DNS) \n Fixed values : {vars}\n and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_cname_scrubbing_delay_models"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    # plot_path = "fig_sub_ccv_delay_L_resolver_model.jpg"
    # if os.path.exists(plot_path):
    #     os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_cname_scrubbing_delay():
    '''Recreates the figure 7.8'''

    attack_folder = SubqueriesCCV_Delay().folder
    list_markers = itertools.cycle(("x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-"))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.0"
    if QMIN_DEACTIVATED:
        powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.16.0", "Unbound 1.16.0", "Model PowerDNS 4.7.0", powerdns_version,
                            "Model BIND 9.18.4",
                            "BIND 9.18.4"]  # "Model Unbound 1.10.0", "Unbound 1.10.0", there was no value computed

    values_model_u1_10 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17cnamelength.txt")][0:8]
    values_model_u1_16 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17cnamelength.txt")][0:8]
    values_model_pdns4_7 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")][0:8]
    values_model_bind9_18_4 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/bind9_18_4/results/measurements/res_00labels_17cnamelength.txt")][0:8]

    if QMIN_DEACTIVATED:
        j_file = DATA_J_FOLDER + "slowDNS+CNAME+scrubbing/data.csv"
        values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
        values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
        values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
        values_bind9_18_4 = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')
    else:
        fields = []
        rows = []

        with open(DATA_L_FOLDER + "delayed_cname_validation.csv") as csv_file:
            csv_read = csv.reader(csv_file, delimiter=",")

            fields = next(csv_read)

            for row in csv_read:
                rows.append(row)

        rows = rows[0:10]

        print(fields)

        # Beware "chain length 9, Model" is "Model; chain length 9"
        # values_model_u1_10_L  = [float(row[fields.index("Model; chain length 9 (to example.com nameserver)")]) for row in rows]
        # values_model_u1_16_L  = [float(row[fields.index("Model; chain length 12 (corrected; seconds)")]) for row in rows]
        # values_model_pdns4_7_L = [float(row[fields.index("Model; chain length 12 with overall timeout 12secs (corrected; seconds)")]) for row in rows]
        # values_model_bind9_18_4_L = [float(row[fields.index("Model; chain length 17 (corrected; seconds)")]) for row in rows]

        # Implementation values
        # values_u1_10 = [float(row[fields.index("Unbound 1.10.0 (to example.com nameserver)")]) for row in rows]
        qmin = ""
        # if not QMIN_DEACTIVATED:
        # qmin = " with QMIN"
        values_u1_16 = [float(row[fields.index("Unbound 1.16.0" + qmin)]) for row in rows]
        values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0" + qmin)]) for row in rows]
        values_bind9_18_4 = [float(row[fields.index("BIND 9.18.4" + qmin)]) for row in rows]

    list_list_values = [values_model_u1_16, values_u1_16, values_model_pdns4_7, values_pdns4_7, values_model_bind9_18_4,
                        values_bind9_18_4]  # [values_model_u1_16,  values_u1_16, values_model_pdns4_7, values_pdns4_7, values_bind9_18_4, values_bind9_18_4]
    if QMIN_DEACTIVATED:
        list_list_values = [values_model_u1_10] + [values_u1_10] + list_list_values
        implementation_names = ["Model Unbound 1.10.0"] + ["Unbound 1.10.0"] + implementation_names

    x = range(0, 1700, 200)
    if QMIN_DEACTIVATED:
        x = range(0, 1500, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Artificial delay (ms or time unit)", fontsize=12)
    ax.set_ylabel('Duration of the query (s)', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 25)


    vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        'Duration of queries sent to victim nameserver with\n Sub+CNAME scrubbing+Delay (slow DNS) \n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    print(list_list_values)
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_cname_scrubbing_delay"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig

def plot_sub_cname_scrubbing_qmin_delay():

    QMIN_DEACTIVATED = False
    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = SubqueriesCCVQMINA_Delay().folder + "/" + qmin_folder
    list_markers = itertools.cycle(("x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-"))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.0"
    if QMIN_DEACTIVATED:
        powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.16.0", "Unbound 1.16.0", "Model PowerDNS 4.7.0", powerdns_version,
                            "Model BIND 9.18.4",
                            "BIND 9.18.4"]  # "Model Unbound 1.10.0", "Unbound 1.10.0", there was no value computed

    values_model_u1_10 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_10_0_cname_bypassed/results/measurements/res_10labels_17cnamelength.txt")][0:8]
    values_model_u1_16 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_16_0_cname_bypassed/results/measurements/res_10labels_17cnamelength.txt")][0:8]
    values_model_pdns4_7 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_10labels_17cnamelength.txt")][0:8]
    values_model_bind9_18_4 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/bind9_18_4/results/measurements/res_10labels_17cnamelength.txt")][0:8]

    if QMIN_DEACTIVATED:
        j_file = DATA_J_FOLDER + "slowDNS+CNAME+scrubbing/data.csv"
        values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
        values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
        values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
        values_bind9_18_4 = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')
    else:
        fields = []
        rows = []

        with open(DATA_L_FOLDER + "delayed_cname_validation.csv") as csv_file:
            csv_read = csv.reader(csv_file, delimiter=",")

            fields = next(csv_read)

            for row in csv_read:
                rows.append(row)

        rows = rows[0:10]

        print(fields)

        # Beware "chain length 9, Model" is "Model; chain length 9"
        # values_model_u1_10_L  = [float(row[fields.index("Model; chain length 9 (to example.com nameserver)")]) for row in rows]
        # values_model_u1_16_L  = [float(row[fields.index("Model; chain length 12 (corrected; seconds)")]) for row in rows]
        # values_model_pdns4_7_L = [float(row[fields.index("Model; chain length 12 with overall timeout 12secs (corrected; seconds)")]) for row in rows]
        # values_model_bind9_18_4_L = [float(row[fields.index("Model; chain length 17 (corrected; seconds)")]) for row in rows]

        # Implementation values
        # values_u1_10 = [float(row[fields.index("Unbound 1.10.0 (to example.com nameserver)")]) for row in rows]
        qmin = ""
        # if not QMIN_DEACTIVATED:
        # qmin = " with QMIN"
        values_u1_16 = [float(row[fields.index("Unbound 1.16.0" + qmin)]) for row in rows][0:8]
        values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0" + qmin)]) for row in rows][0:8]
        values_bind9_18_4 = [float(row[fields.index("BIND 9.18.4" + qmin)]) for row in rows][0:8]

    list_list_values = [values_model_u1_16, values_u1_16, values_model_pdns4_7, values_pdns4_7, values_model_bind9_18_4,
                        values_bind9_18_4]  # [values_model_u1_16,  values_u1_16, values_model_pdns4_7, values_pdns4_7, values_bind9_18_4, values_bind9_18_4]
    if QMIN_DEACTIVATED:
        list_list_values = [values_model_u1_10] + [values_u1_10] + list_list_values
        implementation_names = ["Model Unbound 1.10.0"] + ["Unbound 1.10.0"] + implementation_names

    x = range(0, 1500, 200)
    if QMIN_DEACTIVATED:
        x = range(0, 1500, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Artificial delay (ms or time unit)", fontsize=12)
    ax.set_ylabel('Duration of the query (s)', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 300)

    vars = "CNAME_length={}".format(str(cname_chain_length))  
    ax.set_title(
        'Duration of queries sent to victim nameserver with\n Sub+CNAME scrubbing+Delay (slow DNS) \n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    print(list_list_values)
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_cname_scrubbing_delay"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)
    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig

# SUBQUERIES UNCHAINED DNAME
def plot_sub_unchained_dname_models():
    # attack_folder = "sub-unchained-dname"
    attack_folder = SubqueriesUnchainedDNAME().folder
    list_markers = itertools.cycle(("x", "d",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    implementation_names = ["D-Model Unbound 1.10.0", "C-Model Unbound 1.10.0", "D-Model Unbound 1.16.0",
                            "C-Model Unbound 1.16.0", "D-Model PowerDNS 4.7.0", "C-Model PowerDNS 4.7.0",
                            "D-Model BIND 9.18.4", "C-Model BIND 9.18.4"]
    # No need for  "Model BIND 9.18.4", "L Model BIND 9.18.4"] as there was no model of this

    # DNAME values
    values_model_u1_10 = [i for i in read_to_float(
        attack_folder + "/unbound1_10_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_u1_16 = [i for i in read_to_float(
        attack_folder + "/unbound1_16_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_pdns4_7 = [i for i in read_to_float(
        attack_folder + "/powerDNS4_7_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_bind = [i for i in read_to_float(
        attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")]

    # CNAME values
    attack_folder = SubqueriesUnchainedCNAME().folder
    values_model_u1_10_cname = [i for i in read_to_float(
        attack_folder + "/unbound1_10_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_u1_16_cname = [i for i in read_to_float(
        attack_folder + "/unbound1_16_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_pdns4_7_cname = [i for i in read_to_float(
        attack_folder + "/powerDNS4_7_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_bind_cname = [i for i in read_to_float(
        attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")]

    list_list_values = [values_model_u1_10, values_model_u1_10_cname, values_model_u1_16, values_model_u1_16_cname,
                        values_model_pdns4_7, values_model_pdns4_7_cname, values_model_bind, values_model_bind_cname]
    # No need  values_model_bind, values_model_bind_L]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 110)

    vars = "DNAME/CNAME_length={}".format(str(cname_chain_length))
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+Unchained with CNAME/DNAME \n using MODELS; Fixed values : {vars} \n and {qmin}; D=DNAME, C=CNAME'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    attack_folder = SubqueriesUnchainedDNAME().folder
    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_unchained_dname_models"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_dname_scrubbing_models():
    # attack_folder = "sub-unchained-dname"
    attack_folder = SubqueriesDNAME_Chain_validation().folder
    list_markers = itertools.cycle(("x", "d",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    implementation_names = ["Model Unbound 1.10.0", "CNAME Model Unbound 1.10.0", "Model Unbound 1.16.0",
                            "CNAME Model Unbound 1.16.0", "Model PowerDNS 4.7.0", "CNAME Model PowerDNS 4.7.0",
                            "Model BIND 9.18.4", "CNAME Model BIND 9.18.4"]
    # No need for  "Model BIND 9.18.4", "L Model BIND 9.18.4"] as there was no model of this

    # DNAME values
    values_model_u1_10 = [i for i in read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_u1_16 = [i for i in read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_pdns4_7 = [i for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_bind = [i for i in read_to_float(
        attack_folder + "/bind9_18_4/results/measurements/res_00labels_17dnamelength.txt")]

    # CNAME values
    attack_folder = SubqueriesCCV().folder
    values_model_u1_10_cname = [i for i in read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_u1_16_cname = [i for i in read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_pdns4_7_cname = [i for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_bind_cname = [i for i in read_to_float(
        attack_folder + "/bind9_18_4/results/measurements/res_00labels_17cnamelength.txt")]

    list_list_values = [values_model_u1_10, values_model_u1_10_cname, values_model_u1_16, values_model_u1_16_cname,
                        values_model_pdns4_7, values_model_pdns4_7_cname, values_model_bind, values_model_bind_cname]
    # No need  values_model_bind, values_model_bind_L]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 400)

    vars = "DNAME/CNAME_length={}".format(str(cname_chain_length))
    ax.set_title(
        '# Queries sent to victim nameserver with Sub with DNAME/CNAME scrubbing \n using MODELS; Fixed values : {vars} \n and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    attack_folder = SubqueriesDNAME_Chain_validation().folder
    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_dname_scrubbing_models"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_dname_scrubbing_delays_models():
    attack_folder = SubqueriesDNAMEChainVal_Delay().folder
    list_markers = itertools.cycle(("x", "d",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    implementation_names = ["D-Model Unbound 1.10.0", "C-Model Unbound 1.10.0", "D-Model Unbound 1.16.0",
                            "C-Model Unbound 1.16.0", "D-Model PowerDNS 4.7.0", "C-Model PowerDNS 4.7.0",
                            "D-Model BIND 9.18.4", "C-Model BIND 9.18.4"]
    # No need for  "Model BIND 9.18.4", "L Model BIND 9.18.4"] as there was no model of this

    # DNAME values
    values_model_u1_10 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_u1_16 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_pdns4_7 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17dnamelength.txt")]
    values_model_bind = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/bind9_18_4/results/measurements/res_00labels_17dnamelength.txt")]

    # CNAME values
    attack_folder = SubqueriesCCV_Delay().folder
    values_model_u1_10_cname = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_u1_16_cname = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_pdns4_7_cname = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")]
    values_model_bind_cname = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/bind9_18_4/results/measurements/res_00labels_17cnamelength.txt")]

    list_list_values = [values_model_u1_10, values_model_u1_10_cname, values_model_u1_16, values_model_u1_16_cname,
                        values_model_pdns4_7, values_model_pdns4_7_cname, values_model_bind, values_model_bind_cname]
    # No need  values_model_bind, values_model_bind_L]

    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Artificial delay (ms or time unit)", fontsize=12)
    ax.set_ylabel('Duration of the query (s)', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 55)

    vars = "DNAME/CNAME_length={}".format(str(cname_chain_length)) 
    ax.set_title(
        'Duration of queries sent to victim nameserver\n with Sub+DNAME scrubbing+Delay (slow DNS)\n Fixed values : {vars} and {qmin}; D=DNAME, C=CNAME'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    attack_folder = SubqueriesDNAMEChainVal_Delay().folder
    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_dname_scrubbing_delay_models"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_unchained_dname():
    '''Plots  models versus the real implementations.
    Only makes sense of QMIN is deactivated'''

    attack_folder = SubqueriesUnchainedDNAME().folder
    list_markers = itertools.cycle(("x", "d",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.0"
    if QMIN_DEACTIVATED:
        powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")
    values_model_bind = read_to_float(
        attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")


    j_file = DATA_J_FOLDER + "subquery+DNAME/data.csv"
    values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
    values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
    values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
    values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind, values_bind]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    dname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 110)

    vars = "DNAME_length={}".format(str(dname_chain_length))  # ", ".join(fixed)

    ax.set_title(
        '# Queries sent to victim nameserver with Sub+Unchained with DNAME \n Fixed value(s) : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_unchained_dname"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)
        
    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_dname_scrubbing():
    attack_folder = SubqueriesDNAME_Chain_validation().folder
    list_markers = itertools.cycle(("x", "p"))  # "P", "p"))#"*"))#,"s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-."))  # ,":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.0"
    if QMIN_DEACTIVATED:
        powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4",
                            "BIND 9.18.4"]  # ["Model Unbound 1.10.0", "L Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "L Unbound 1.16.0", "Unbound 1.16.0", "Model PowerDNS 4.7.0", "L PowerDNS 4.7.0", "PowerDNS 4.7.0"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_bind9_18_4 = read_to_float(
        attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")

    if QMIN_DEACTIVATED:
        j_file = DATA_J_FOLDER + "subquery+DNAME+scrubbing/data.csv"
        values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
        values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
        values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
        values_bind9_18_4 = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')
    else:

        fields = []
        rows = []

        with open(DATA_L_FOLDER + "subqueries_cname_validation_L.csv") as csv_file:
            csv_read = csv.reader(csv_file, delimiter=",")

            fields = next(csv_read)

            for row in csv_read:
                rows.append(row)

        rows = rows[0:10]
        
        # Real implementation values
        values_u1_10 = [float(row[fields.index("Unbound 1.10.0 with IPv6 disabled (to example.com nameserver)")]) for
                        row in rows]
        values_u1_16 = [float(row[fields.index("Unbound 1.16.0 with IPv6 disabled (to example.com nameserver)")]) for
                        row in rows]
        values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0 (to example.com nameserver)")]) for row in rows]
        values_bind9_18_4 = [float(row[fields.index("BIND 9.18.4 with IPv6 disabled (to example.com nameserver)")]) for
                             row in rows]

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind9_18_4, values_bind9_18_4]

    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    dname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 200)
    
    vars = "DNAME_length={}".format(str(dname_chain_length)) 
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+DNAME scrubbing \n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_dname_scrubbing"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_dname_scrubbing_delay():
    attack_folder = SubqueriesDNAMEChainVal_Delay().folder
    list_markers = itertools.cycle(("x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-"))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.0"
    if QMIN_DEACTIVATED:
        powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4",
                            "BIND 9.18.4"]  # there was no value computed

    values_model_u1_10 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17dnamelength.txt")][0:8]
    values_model_u1_16 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17dnamelength.txt")][0:8]
    values_model_pdns4_7 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17dnamelength.txt")][0:8]
    values_model_bind9_18_4 = [i / 10 ** 3 for i in read_to_float(
        attack_folder + "/bind9_18_4/results/measurements/res_00labels_17dnamelength.txt")][0:8]

    if QMIN_DEACTIVATED:
        j_file = DATA_J_FOLDER + "slowDNS+DNAME+scrubbing/data.csv"
        values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
        values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
        values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
        values_bind9_18_4 = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')
    else:
        fields = []
        rows = []

        with open(DATA_L_FOLDER + "delayed_cname_validation.csv") as csv_file:
            csv_read = csv.reader(csv_file, delimiter=",")

            fields = next(csv_read)

            for row in csv_read:
                rows.append(row)

        rows = rows[0:10]

        print(fields)

        qmin = ""
        # if not QMIN_DEACTIVATED:
        # qmin = " with QMIN"
        values_u1_16 = [float(row[fields.index("Unbound 1.16.0" + qmin)]) for row in rows]
        values_pdns4_7 = [float(row[fields.index("PowerDNS 4.7.0" + qmin)]) for row in rows]
        values_bind9_18_4 = [float(row[fields.index("BIND 9.18.4" + qmin)]) for row in rows]

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind9_18_4, values_bind9_18_4]

    x = range(0, 1700, 200)
    if QMIN_DEACTIVATED:
        x = range(0, 1500, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    dname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Artificial delay (ms or time unit)", fontsize=12)
    ax.set_ylabel('Duration of the query (s)', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 30)

    vars = "DNAME_length={}".format(str(dname_chain_length))

    ax.set_title(
        'Duration of queries sent to victim nameserver \n with Sub+DNAME scrubbing+Delay (slow DNS) \n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_dname_scrubbing_delay"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def main():
    # c()
    # plot_subccvqmin_unbound1_10_0()
    # plot_subccvqmin_unbound1_16_0()

    # '''Recreates the figure 7.5'''
    # plot_subccvqmin()
    #
    # plot_sub_cname_scrubbing_delay_models()()
    #
    # '''Recreates the figure 7.8'''
    # plot_sub_cname_scrubbing_delay()
    #
    # '''Combines  model, l', and the resolver of PowerDNS'''
    # plot_subccvdelay_powerdns()

    # If we change here -> we have to change in each attack file ->
    global QMIN_DEACTIVATED
    QMIN_DEACTIVATED = False

    # '''Plots models for Subqueries Unchained + CNAME vs L'''
    # plot_sub_unchained_cname_models()
    # '''Plots my models versus the real implementations.
    # Recreates the figure 7.2'''
    # plot_sub_unchained_cname()
    #
    # '''Plots my models for Subqueries + CNAME scrubbing vs L'''
    # plot_sub_cname_scrubbing_models()
    # '''Recreates the figure 7.4'''
    # plot_sub_cname_scrubbing()
    #
    # '''Plots my models for Subqueries + CNAME scrubbing + Delay vs L'''
    # plot_sub_cname_scrubbing_delay_models()
    # '''Recreates the figure 7.8'''
    # plot_sub_cname_scrubbing_delay()
    #
    # # DNAME PART
    # '''Plots my models for Subqueries Unchained + DNAME vs mine for CNAME'''
    # plot_sub_unchained_dname_models()
    #
    # '''Plots my models for Subqueries + DNAME scrubbing vs mine for CNAME scrubbing'''
    # plot_sub_dname_scrubbing_models()
    #
    # '''Plots my models for Subqueries + DNAME scrubbing + delays vs mine for CNAME scrubbing + delays'''
    # plot_sub_dname_scrubbing_delays_models()

    # plot_sub_unchained_dname()
    #
    # plot_sub_dname_scrubbing_models()
    # plot_sub_dname_scrubbing()
    #
    # plot_sub_dname_scrubbing_delay()


    QMIN_DEACTIVATED = True

    # plot_sub_unchained_cname()
    plot_sub_cname_scrubbing()
    plot_sub_cname_scrubbing_delay()
    '''Plots models versus the real implementations.
    Only makes sense of QMIN is disabled'''
    # plot_sub_unchained_dname()
    plot_sub_dname_scrubbing()
    plot_sub_dname_scrubbing_delay()


def plot_subquery_unchained_cname_qminenabled():
    '''Plots my models versus the real implementations.
      With QMIN enabled but not used'''

    QMIN_DEACTIVATED = False
    attack_folder = "test-copy/latest_attack_with_qmin_enabled/sub-unchained-cname"  # SubqueriesUnchainedCNAME().folder
    list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")
    values_model_bind = read_to_float(
        attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17cnamelength.txt")

    j_file = DATA_J_FOLDER + "subquery+CNAME+qminEnabled/data.csv"
    values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
    values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
    values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
    values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind, values_bind]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 110)


    vars = "CNAME_length={}".format(str(cname_chain_length)) 
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+Unchained with CNAME \n Fixed values : {vars}and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_unchained_cname"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_subquery_unchained_dname_qminenabled():
    '''Plots my models versus the real implementations.
      With QMIN enabled but not used'''

    QMIN_DEACTIVATED = False
    attack_folder = "test-copy/latest_attack_with_qmin_enabled/sub-unchained-dname"  # SubqueriesUnchainedCNAME().folder
    list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")
    values_model_bind = read_to_float(
        attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")

    j_file = DATA_J_FOLDER + "subquery+DNAME+qminEnabled/data.csv"
    values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
    values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
    values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
    values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind, values_bind]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 210)


    vars = "DNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+Unchained with DNAME \n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_unchained_dname"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_subquery_scrubbing_cname_qminenabled():
    '''Plots my models versus the real implementations.
      With QMIN enabled but not used'''

    # attack_folder = "sub-unchained-cname"
    QMIN_DEACTIVATED = False
    attack_folder = "test-copy/latest_attack_with_qmin_enabled/sub-ccv"  # SubqueriesUnchainedCNAME().folder
    list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_bind = read_to_float(attack_folder + "/bind9_18_4/results/measurements/res_00labels_17cnamelength.txt")

    j_file = DATA_J_FOLDER + "subquery+CNAME+scrubbing+qminEnabled/data.csv"
    values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
    values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
    values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
    values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind, values_bind]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 410)


    vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+Scrubbing with CNAME \n Fixed values : {vars}and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_scrubbing_cname"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_sub_scrub_cname_qmin():
    '''Plots my models versus the real implementations.
      Taking care of qmin'''

    # attack_folder = "sub-unchained-cname"
    # QMIN_DEACTIVATED = False
    for QMIN_DEACTIVATED in [True, False]:

        qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
        attack_folder = SubqueriesCCVQMINA().folder + "/" + qmin_folder
        list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
        list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
        list_colors = itertools.cycle(
            ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

            powerdns_version = "PowerDNS 4.7.3"
        implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                                "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

        values_model_u1_10 = read_to_float(
            attack_folder + "/unbound1_10_0_cname_bypassed/results/measurements/res_10labels_17cnamelength.txt")
        values_model_u1_16 = read_to_float(
            attack_folder + "/unbound1_16_0_cname_bypassed/results/measurements/res_10labels_17cnamelength.txt")
        values_model_pdns4_7 = read_to_float(
            attack_folder + "/powerDNS4_7_0/results/measurements/res_10labels_17cnamelength.txt")
        values_model_bind = read_to_float(attack_folder + "/bind9_18_4/results/measurements/res_10labels_17cnamelength.txt")

        if QMIN_DEACTIVATED:
            spec_folder = ""
        else:
            spec_folder = "+qminEnabled"
        j_file = DATA_J_FOLDER + "subquery+CNAME+scrubbing" + spec_folder + "/data.csv"
        values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
        values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
        values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
        values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')

        list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                            values_pdns4_7, values_model_bind, values_bind]

        x = range(1, 11)
        fig = plt.figure()
        ax = fig.add_subplot()

        cname_chain_length = 17
        nb_labels = 0

        ax.set_xlabel("Number of delegations", fontsize=12)
        ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

        ax.set_xlim(0, 11)
        ax.set_ylim(0, 1800)

        # fixed_vars = {"ns_del" : "#Del={}".format(str(ns_del)), "cname_chain_length" : "CNAME_length={}".format(str(cname_chain_length)), "nb_labels" : "#Labels={}".format(str(nb_labels))}
        # fixed = ["CNAME_length={}".format(str(cname_chain_length)), "#Labels={}".format(str(nb_labels))]
        vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
        # RElated to the previous : find from the filename what are the fixed attributes
        ax.set_title(
            '# Queries sent to victim nameserver with Sub+Scrubbing with CNAME \n Fixed values : {vars} and {qmin}'.format(
                vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

        ax.grid()
        for list_values in list_list_values:
            ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

        check_folder_exists(attack_folder + "/comparison/")
        plot_path = attack_folder + "/comparison/" + "fig_sub_scrub_cname_" + qmin_folder
        plot_path_jpg = plot_path + ".jpg"
        if os.path.exists(plot_path):
            os.remove(plot_path)

        plt.legend(implementation_names)
        print(list_list_values)

        plt.savefig(plot_path_jpg)
        save_high_quality(plt, plot_path)

        plt.close()
        del fig

def plot_sub_scrub_dname_qmin():
    '''Plots my models versus the real implementations.
      Taking care of qmin'''

    # attack_folder = "sub-unchained-cname"
    # QMIN_DEACTIVATED = False
    for QMIN_DEACTIVATED in [True, False]:

        qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
        attack_folder = SubqueriesDCVQMINA().folder + "/" + qmin_folder
        list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
        list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
        list_colors = itertools.cycle(
            ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

            powerdns_version = "PowerDNS 4.7.3"
        implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                                "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

        values_model_u1_10 = read_to_float(
            attack_folder + "/unbound1_10_0_cname_bypassed/results/measurements/res_10labels_17dnamelength.txt")
        values_model_u1_16 = read_to_float(
            attack_folder + "/unbound1_16_0_cname_bypassed/results/measurements/res_10labels_17dnamelength.txt")
        values_model_pdns4_7 = read_to_float(
            attack_folder + "/powerDNS4_7_0/results/measurements/res_10labels_17dnamelength.txt")
        values_model_bind = read_to_float(attack_folder + "/bind9_18_4/results/measurements/res_10labels_17dnamelength.txt")

        if QMIN_DEACTIVATED:
            spec_folder = ""
        else:
            spec_folder = "+qminEnabled"

        number_values = len(values_model_u1_16)
        j_file = DATA_J_FOLDER + "subquery+DNAME+scrubbing" + spec_folder + "/data.csv"
        values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')[:number_values]
        values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')[:number_values]
        values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')[:number_values]
        values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')[:number_values]

        list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                            values_pdns4_7, values_model_bind, values_bind]

        x = range(1, 11)
        fig = plt.figure()
        ax = fig.add_subplot()

        dname_chain_length = 17
        nb_labels = 0

        ax.set_xlabel("Number of delegations", fontsize=12)
        ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

        ax.set_xlim(0, 11)
        ax.set_ylim(0, 1800)

        # fixed_vars = {"ns_del" : "#Del={}".format(str(ns_del)), "cname_chain_length" : "CNAME_length={}".format(str(cname_chain_length)), "nb_labels" : "#Labels={}".format(str(nb_labels))}
        # fixed = ["CNAME_length={}".format(str(cname_chain_length)), "#Labels={}".format(str(nb_labels))]
        vars = "DNAME_length={}".format(str(dname_chain_length))  # vars = ", ".join(fixed)
        # RElated to the previous : find from the filename what are the fixed attributes
        ax.set_title(
            '# Queries sent to victim nameserver with Sub+Scrubbing with DNAME + QMIN \n Fixed values : {vars} and {qmin}'.format(
                vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

        ax.grid()
        for list_values in list_list_values:
            ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

        check_folder_exists(attack_folder + "/comparison/")
        plot_path = attack_folder + "/comparison/" + "fig_sub_scrub_dname_" + qmin_folder
        plot_path_jpg = plot_path + ".jpg"
        if os.path.exists(plot_path):
            os.remove(plot_path)

        plt.legend(implementation_names)
        print(list_list_values)

        plt.savefig(plot_path_jpg)
        save_high_quality(plt, plot_path)

        plt.close()
        del fig



def plot_subquery_scrubbing_dname_qminenabled():
    """Plots my models versus the real implementations.
      With QMIN enabled but not used"""

    # attack_folder = "sub-unchained-cname"
    QMIN_DEACTIVATED = False
    attack_folder = "test-copy/latest_attack_with_qmin_enabled/sub-dcv"  # SubqueriesUnchainedCNAME().folder
    list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_bind = read_to_float(
        attack_folder + "/bind9_18_4_no_chain_val/results/measurements/res_00labels_17dnamelength.txt")

    j_file = DATA_J_FOLDER + "subquery+DNAME+scrubbing+qminEnabled/data.csv"
    values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
    values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
    values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
    values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind, values_bind]

    x = range(1, 11)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 410)


    vars = "DNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    ax.set_title(
        '# Queries sent to victim nameserver with Sub+Scrubbing with DNAME \n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_scrubbing_dname"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)



    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_subquery_scrubbing_cname_delay_qminenabled():
    '''Plots my models versus the real implementations.
      With QMIN enabled but not used'''

    # attack_folder = "sub-unchained-cname"
    QMIN_DEACTIVATED = False
    attack_folder = "test-copy/latest_attack_with_qmin_enabled/sub-ccv-delay"  # SubqueriesUnchainedCNAME().folder
    list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17cnamelength.txt")
    values_model_bind = read_to_float(attack_folder + "/bind9_18_4/results/measurements/res_00labels_17cnamelength.txt")

    j_file = DATA_J_FOLDER + "slowDNS+CNAME+scrubbing+qminEnabled/data.csv"
    values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
    values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
    values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
    values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind, values_bind]

    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Delay in Time unit (or ms)", fontsize=12)
    ax.set_ylabel('Time', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 1500)


    vars = "CNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title('Duration of queries with slowDNS + CNAME \n Fixed values : {vars} and {qmin}'.format(vars=vars,
                                                                                                       qmin=text_plot_qmin(
                                                                                                           QMIN_DEACTIVATED)),
                 fontsize=11)

    ax.grid()
    print(list_list_values)
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_scrubbing_cname_delay"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


def plot_subquery_scrubbing_dname_delay_qminenabled():
    '''Plots my models versus the real implementations.
      With QMIN enabled but not used'''

    # attack_folder = "sub-unchained-cname"
    QMIN_DEACTIVATED = False
    attack_folder = "test-copy/latest_attack_with_qmin_enabled/sub-dcv-delay"  # SubqueriesUnchainedCNAME().folder
    list_markers = itertools.cycle(("x", "p",))  # "p", "*"))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("--", "-.",))  # ":"))
    list_colors = itertools.cycle(
        ("tab:blue", "tab:blue", "tab:orange", "tab:orange", "tab:green", "tab:green", "tab:red", "tab:red"))

    powerdns_version = "PowerDNS 4.7.3"
    implementation_names = ["Model Unbound 1.10.0", "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0",
                            "Model PowerDNS 4.7.0", powerdns_version, "Model BIND 9.18.4", "BIND 9.18.4"]

    values_model_u1_10 = read_to_float(
        attack_folder + "/unbound1_10_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_u1_16 = read_to_float(
        attack_folder + "/unbound1_16_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_pdns4_7 = read_to_float(
        attack_folder + "/powerDNS4_7_0/results/measurements/res_00labels_17dnamelength.txt")
    values_model_bind = read_to_float(attack_folder + "/bind9_18_4/results/measurements/res_00labels_17dnamelength.txt")

    j_file = DATA_J_FOLDER + "slowDNS+DNAME+scrubbing+qminEnabled/data.csv"
    values_u1_10 = read_j_files(j_file, 'unbound-1.10.0', 'y', 'x')
    values_u1_16 = read_j_files(j_file, 'unbound-1.16.0', 'y', 'x')
    values_pdns4_7 = read_j_files(j_file, 'powerDNS-4.7.3', 'y', 'x')
    values_bind = read_j_files(j_file, 'bind-9.18.4', 'y', 'x')

    list_list_values = [values_model_u1_10, values_u1_10, values_model_u1_16, values_u1_16, values_model_pdns4_7,
                        values_pdns4_7, values_model_bind, values_bind]

    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    cname_chain_length = 17
    nb_labels = 0

    ax.set_xlabel("Delay in Time unit (or ms)", fontsize=12)
    ax.set_ylabel('Time', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 1500)


    vars = "DNAME_length={}".format(str(cname_chain_length))  # vars = ", ".join(fixed)
    ax.set_title(
        'Duration of queries with slowDNS + CNAME with DNAME \n Fixed values : {vars} and {qmin}'.format(vars=vars,
                                                                                                         qmin=text_plot_qmin(
                                                                                                             QMIN_DEACTIVATED)),
        fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, color=next(list_colors), linestyle=next(list_linestyle), marker=next(list_markers))

    check_folder_exists(attack_folder + "/comparison/")
    plot_path = attack_folder + "/comparison/" + "fig_sub_scrubbing_dname_delay"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)

    plt.legend(implementation_names)
    print(list_list_values)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    del fig


if __name__ == "__main__":
    # plot_subquery_unchained_cname_qminenabled()
    # plot_subquery_unchained_dname_qminenabled()
    # # plot_subquery_scrubbing_cname_qminenabled()
    # plot_subquery_scrubbing_dname_qminenabled()
    # plot_subquery_scrubbing_cname_delay_qminenabled()
    # plot_subquery_scrubbing_dname_delay_qminenabled()
    # main()
    # print(read_test_j_files("test-copy/test_j.csv", "bind", "Number of queries", order_name="NS"))
    # Comparison plots
    # plot_sub_scrub_cname_qmin()
    # plot_sub_scrub_dname_qmin()
    plot_sub_cname_scrubbing_qmin_delay()