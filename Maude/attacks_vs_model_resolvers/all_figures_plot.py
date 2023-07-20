#!/usr/bin/env python3

import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

from create_sub_ccv_qmin_files import *
from utils import *

DATA_J_FOLDER = "data/j/"


def save_figure(plt, filename):
    save_to_jpg(plt, filename)
    # save_to_eps(plt, filename)
    # save_to_svg(plt, filename)
    save_to_pdf(plt, filename)


def save_to_jpg(plt, filename):
    new_filename = filename + '.jpg'
    if os.path.exists(new_filename):
        os.remove(new_filename)
    plt.savefig(new_filename, format='jpg', bbox_inches="tight")


def save_to_svg(plt, filename):
    new_filename = filename + '.svg'
    if os.path.exists(new_filename):
        os.remove(new_filename)
    plt.savefig(new_filename, format='svg', dpi=1200, bbox_inches="tight")


def save_to_pdf(plt, filename):
    new_filename = filename + '.pdf'
    if os.path.exists(new_filename):
        os.remove(new_filename)
    plt.savefig(new_filename, format='pdf', bbox_inches="tight")


def save_to_eps(plt, filename):
    new_filename = filename + '.eps'
    if os.path.exists(new_filename):
        os.remove(new_filename)
    plt.savefig(new_filename, format='eps', bbox_inches="tight")


def read_to_float(filename):
    '''Reads files and converts the values to float'''
    with open(filename, "r") as f:
        values = f.readlines()[0][:-1].split(",")
        values = [float(i) for i in values]

    return values


def read_to_sec(filename):
    '''Reads files concerning the attacks with delay and converts the values to float, then to seconds. The values stored are in milliseconds.'''
    values = read_to_float(filename)
    return [val / 10 ** 3 for val in values]


def get_filename(path_to_resolver, dname=False):
    if dname:
        return path_to_resolver + "/results/measurements/res_00labels_17dnamelength.txt"
    return path_to_resolver + "/results/measurements/res_00labels_17cnamelength.txt"


def read_j_files(filename, resolver_name, target_value, order_name):
    df = pd.read_csv(filename)
    resolver = df.loc[df['hue'] == resolver_name]
    resolver = resolver.sort_values(by=order_name)

    return resolver[target_value].astype(float).to_list()


def get_values_j(folder_name_attack, resolver_name_j):
    '''Returns the list of list of values of all resolvers for an attack whose name is the folder'''
    list_list_values = []
    for res_name in resolver_name_j:
        list_list_values.append(
            read_j_files(folder_name_attack + "/data.csv", resolver_name=res_name, target_value="y",
                         order_name="x"))

    return list_list_values

def get_new_values_j(folder_name_attack, resolver_name_j, sorting_type):
    '''Returns the list of list of values of all resolvers for an attack whose name is the folder'''
    list_list_values = []
    for res_name in resolver_name_j:
        filename = folder_name_attack + "/data.csv"
        df = pd.read_csv(filename)

        resolver = df.loc[df['resolver'] == res_name]
        resolver = resolver.sort_values(by=sorting_type)
        values = resolver["result"].astype(float).to_list()
        print("VALUES")
        print(values)
        list_list_values.append(values)

    return list_list_values


def get_values_attack_model(attack, resolvers_folders):
    list_list_values = []
    attack_folder = attack.folder + "/"

    dname = "dname" in attack.name_attack.lower()
    print(attack.name_attack.lower())

    if "slowdns" in attack.name_attack.lower():
        # use read_to_sec
        for folder in resolvers_folders:
            filename = get_filename(attack_folder + folder, dname=dname)
            if not os.path.isfile(filename):
                print("The file doesn't exist. PASS ")
                continue
            # Only takes delay until 1400
            list_list_values.append(read_to_sec(filename)[0:8])
    else:
        for folder in resolvers_folders:
            filename = get_filename(attack_folder + folder, dname=dname)
            print(filename)
            if not os.path.isfile(filename):
                print("The file doesn't exist. PASS ")
                continue
            print("FILE exists :" + ", ".join([str(val) for val in read_to_float(filename)]))
            list_list_values.append(read_to_float(filename))

    return list_list_values

def get_values_attack_model_with_filename(attack, resolvers_folders, filename2):
    list_list_values = []
    attack_folder = attack.folder + "/"

    dname = "dname" in attack.name_attack.lower()
    print(attack.name_attack.lower())

    if "slowdns" in attack.name_attack.lower() or "delay" in attack.name_attack.lower():
        # use read_to_sec
        for folder in resolvers_folders:
            filename = attack_folder + folder + "/results/measurements/" + filename2 + ".txt" # get_filename(attack_folder + folder, dname=dname)
            print(filename)
            if not os.path.isfile(filename):
                print("The file doesn't exist. PASS ")
                continue
                # Only takes delay until 1400
            list_list_values.append(read_to_sec(filename)[0:8])
    else:
        for folder in resolvers_folders:
            filename = attack_folder + folder + "/results/measurements/"+ filename2 + ".txt"
            print(filename)
            if not os.path.isfile(filename):
                print("The file doesn't exist. PASS ")
                continue
            print("FILE exists :" + ", ".join([str(val) for val in read_to_float(filename)]))
            list_list_values.append(read_to_float(filename))

    return list_list_values

def get_new_values_attack_model(attack, resolvers_folders):
    list_list_values = []
    attack_folder = attack.folder + "/"

    dname = "dname" in attack.name_attack.lower()
    print(attack.name_attack.lower())

    if "slowdns" in attack.name_attack.lower():
        # use read_to_sec
        for folder in resolvers_folders:
            filename = attack_folder + folder + "/results/measurements/res_10labels_01nsdel.txt"
            if not os.path.isfile(filename):
                print("The file doesn't exist. PASS ")
                continue
            # Only takes delay until 1400
            list_list_values.append(read_to_sec(filename)[0:8])
    else:
        for folder in resolvers_folders:
            filename = attack_folder + folder + "/results/measurements/res_10labels_01nsdel.txt"
            print(filename)
            if not os.path.isfile(filename):
                print("The file doesn't exist. PASS ")
                continue
            print("FILE exists :" + ", ".join([str(val) for val in read_to_float(filename)]))
            list_list_values.append(read_to_float(filename))

    return list_list_values

def subplot_attack(ax, title, add_labels, list_list_values_model, list_list_values_attack, list_linestyle, list_colors,
                   list_markers, fillstyle, attack, names_lines):
    fontsize = 9

    if "slowdns" in attack.name_attack.lower():
        ax.set_ylabel("Duration (s)", fontsize=fontsize)
        ax.set_xlim(0, 1.5)
        ax.set_ylim(0, 25)
        x = np.arange(0, 1.5, 0.2)
        ax.set_xticks(x)
        ax.set_yticks([0, 5, 10, 15, 20, 25])
        if add_labels:
            ax.set_xlabel("Delay (s)", fontsize=fontsize)
        if "slowDNS+CNAME+Scrubbing+QMIN" == attack.name_attack:
            ax.set_ylim(0, 276)
            ax.set_yticks(list(range(0, 276, 25)))
    else:
        ax.set_ylabel("# Queries", fontsize=fontsize)
        ax.set_xlim(0, 11)
        # Adjust the y-limit
        if "scrubbing" in attack.name_attack.lower():
            ax.set_ylim(0, 200)
        else:
            ax.set_ylim(0, 200)
        x = range(1, len(list_list_values_model[0]) + 1)
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.set_yticks([0, 50, 100, 150, 200])
        if "cname+scrubbing+qmin" == attack.name_attack.lower():
            fontsize = 9
            ax.set_ylim(0, 210)
            ax.set_xlim(0,21)
            ax.set_xticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])

        if add_labels:
            if "cname+scrubbing+qmin" == attack.name_attack.lower():
                ax.set_xlabel("Length of the CNAME chain", fontsize=fontsize)
            else:
                ax.set_xlabel("# Delegations", fontsize=fontsize)

    if not add_labels:
        ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=False)

    ax.set_title(title, fontsize=fontsize + 1, loc='center', wrap=False, )  # fontweight="bold")
    ax.grid(linestyle='dotted', linewidth=0.5)
    # ax.xaxis.grid(False)  # vertical lines
    # Reduce the size of the ticks labels
    ax.tick_params(axis='both', which='major', labelsize=fontsize)
    ax.tick_params(axis='both', which='minor', labelsize=fontsize)

    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # ax.grid()
    for index, list_values in enumerate(list_list_values_model):
        print([str(val) for val in list_values])
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        # Reduce the line width of solid
        linewidth = 0.7 if linestyle == "-" or linestyle == "-." else 1.0

        ax.plot(x, list_values, label=names_lines[2 * index], color=color, linewidth=linewidth,
                linestyle=linestyle, ) # marker=marker,)

        ax.plot(x, list_list_values_attack[index], label=names_lines[2 * index + 1], color=color, linestyle='None',
                linewidth=linewidth, fillstyle=fillstyle, marker=marker, markersize=7, )

def subplot_attack_v2(ax, title, add_labels_xaxis, list_list_values_model, list_list_values_attack, list_linestyle, list_colors,
                      list_markers, fillstyle, attack, names_lines, xlim, ylim, fontsize=13):
    # fontsize = 13

    if "slowdns" in attack.name_attack.lower() or "delay" in attack.name_attack.lower():
        ax.set_ylabel("Duration (s)", fontsize=fontsize)
        ax.set_xlim(0, xlim)
        ax.set_ylim(0, ylim)
        x = np.arange(0, 1.5, 0.2)
        ax.set_xticks(x)

        if add_labels_xaxis:
            ax.set_xlabel("Delay (s)", fontsize=fontsize-1)
    else:
        ax.set_ylabel("# Queries", fontsize=fontsize-1)
        ax.set_xlim(0, xlim)
        # Adjust the y-limit
        if "scrubbing" in attack.name_attack.lower():
            ax.set_ylim(0, ylim)
        else:
            ax.set_ylim(0, ylim)
        x = range(1, len(list_list_values_model[0]) + 1)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        if "cname+scrubbing+qmin" == attack.name_attack.lower():
            ax.set_xticks([0, 4, 8, 12, 16, 20])

        if add_labels_xaxis:
            if "cname+scrubbing+qmin" == attack.name_attack.lower():
                ax.set_xlabel("Length of the CNAME chain", fontsize=fontsize-1)
            else:
                ax.set_xlabel("# Delegations", fontsize=fontsize-1)

    if not add_labels_xaxis:
        ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=False)

    # ax.text(15, -0.10,title)
    if "slowdns" in attack.name_attack.lower() or "delay" in attack.name_attack.lower():
        ax.set_title(title, fontsize=fontsize + 2, loc='center', y=-0.28, wrap=False, )  # fontweight="bold")
    else:
        ax.set_title(title, fontsize=fontsize + 2, loc='center', y=-0.35, wrap=False, )  # fontweight="bold")
    ax.grid(linestyle='dotted', linewidth=0.5)
    # Remove vertical lines
    ax.xaxis.grid(False)
    # Reduce the size of the ticks labels
    ax.tick_params(axis='both', which='major', labelsize=fontsize-2)
    ax.tick_params(axis='both', which='minor', labelsize=fontsize-2)


    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # ax.grid()
    for index, list_values in enumerate(list_list_values_model):
        print([str(val) for val in list_values])
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        # Reduce the line width of solid
        linewidth = 0.7 if linestyle == "-" or linestyle == "-." else 1.0

        ax.plot(x, list_values, label=names_lines[2 * index], color=color, linewidth=linewidth,
                linestyle=linestyle, ) # marker=marker,)

        ax.plot(x, list_list_values_attack[index], label=names_lines[2 * index + 1], color=color, linestyle='None',
                linewidth=linewidth, fillstyle=fillstyle, marker=marker, markersize=7, )

def main():
    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    attacks = [SubqueriesUnchainedCNAME(), SubqueriesCCV(), SubqueriesCCV_Delay(), SubqueriesUnchainedDNAME(),
               SubqueriesDNAME_Chain_validation(), SubqueriesDNAMEChainVal_Delay()]

    name_folders = ["subquery+CNAME", "subquery+CNAME+scrubbing", "slowDNS+CNAME+scrubbing", "subquery+DNAME",
                    "subquery+DNAME+scrubbing", "slowDNS+DNAME+scrubbing", ]
    name_folders = [DATA_J_FOLDER + folder for folder in name_folders]

    # Create the 6 subplots
    # p = plt.figure(figsize=(12, 3))
    # plt.figure(figsize=(1,1))
    fig, axs = plt.subplots(2, 3)
    fig.set_figheight(3.1)
    fig.set_figwidth(7.5)
    # plt.rcParams["figure.figsize"] = (20,3)

    resolvers_folders = ["bind9_18_4", "bind9_18_4_cname", "bind9_18_4_no_chain_val", "powerDNS4_7_0_no_chain_val",
                         "powerDNS4_7_0", "unbound1_10_0", "unbound1_10_0_no_chain_val", "unbound1_16_0",
                         "unbound1_16_0_no_chain_val"]

    resolver_name_j = ["bind-9.18.4", "powerDNS-4.7.3", "unbound-1.10.0", "unbound-1.16.0"]

    names_lines = ["Model BIND 9.18.4", "BIND 9.18.4", "Model PowerDNS 4.7.0", "PowerDNS 4.7.3", "Model Unbound 1.10.0",
                   "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0", ]
    alphabet = string.ascii_lowercase
    for index, attack in enumerate(attacks):

        add_labels = index > 2

        list_list_values_model = get_values_attack_model(attack, resolvers_folders)
        print("LIST OF VALUES FOR ATTACK : " + attack.name_attack)
        print(list_list_values_model)

        list_list_values_attack = get_values_j(name_folders[index], resolver_name_j)

        subplot_attack(ax=axs.flat[index], title="({}) ".format(alphabet[index]) + attack.name_attack,
                       add_labels=add_labels, list_list_values_model=list_list_values_model,
                       list_list_values_attack=list_list_values_attack, list_linestyle=list_linestyle,
                       list_colors=list_colors, list_markers=list_markers, fillstyle=fillstyle, attack=attack,
                       names_lines=names_lines)

    filename = "Figure1_all_attacks"

    # Bbox_to_anchors to add spacing between legend and plots
    leg = fig.legend(names_lines, loc="upper center", ncol=len(names_lines) // 2, fontsize=6, borderaxespad=0,
                     bbox_to_anchor=(0.5, 1.07), frameon=False)  # , mode='expand')
    # Leaves some space between the rows
    fig.subplots_adjust(hspace=0.3)
    # plt.margins(y=2)
    fig.tight_layout()
    save_figure(plt, filename)

    plt.close()


def main_cname_qmin():
    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    attacks = [CCV_QMIN()]

    name_folders = ["CNAME+QMIN"]
    name_folders = [DATA_J_FOLDER + folder for folder in name_folders]

    # Create one subplot
    # p = plt.figure(figsize=(12, 3))
    plt.figure(figsize=(12 ,12))
    fig, axs = plt.subplots(1, 1)
    fig.set_figheight(4.0)
    fig.set_figwidth(6.0)
    plt.rcParams["figure.figsize"] = (20,3)

    resolvers_folders = ["bind9_18_4", "bind9_18_4_cname", "bind9_18_4_no_chain_val", "powerDNS4_7_0_no_chain_val",
                         "powerDNS4_7_0", "unbound1_10_0", "unbound1_10_0_cname_bypassed", "unbound1_16_0",
                         "unbound1_16_0_cname_bypassed"]

    resolver_name_j = ["bind-9.18.4", "powerdns-4.7", "unbound-1.10.0", "unbound-1.16.0"]
    resolver_name_j = ["resolver-" + res for res in resolver_name_j]
    names_lines = ["Model BIND 9.18.4", "BIND 9.18.4", "Model PowerDNS 4.7.0", "PowerDNS 4.7.3", "Model Unbound 1.10.0",
                   "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0", ]
    alphabet = string.ascii_lowercase
    for index, attack in enumerate(attacks):

        add_labels = True

        list_list_values_model = get_new_values_attack_model(attack, ["qmin_enabled/" + res for res in resolvers_folders])
        print("LIST OF VALUES FOR ATTACK : " + attack.name_attack)
        print(list_list_values_model)

        list_list_values_attack = get_new_values_j(name_folders[index], resolver_name_j, sorting_type="zone")
        print(list_list_values_attack)
        subplot_attack(ax=axs, title="CNAME + Scrubbing + QMIN",
                       add_labels=add_labels, list_list_values_model=list_list_values_model,
                       list_list_values_attack=list_list_values_attack, list_linestyle=list_linestyle,
                       list_colors=list_colors, list_markers=list_markers, fillstyle=fillstyle, attack=attack,
                       names_lines=names_lines)

    filename = attacks[0].folder + "/" + "CNAME_Scrubbing_QMIN"

    # Bbox_to_anchors to add spacing between legend and plots
    leg = fig.legend(names_lines, loc="upper center", ncol=len(names_lines) // 2, fontsize=6, borderaxespad=0,
                     bbox_to_anchor=(0.5, 1.07), frameon=False)  # , mode='expand')
    # Leaves some space between the rows
    fig.subplots_adjust(hspace=0.3)
    # plt.margins(y=2)
    fig.tight_layout()
    save_figure(plt, filename)

    plt.close()


def main_subqueries_three_qmin():

    list_markers = itertools.cycle(('o', 'v', 's', ))#'^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":",)) # "-."))
    list_colors = itertools.cycle(("tab:blue",  "tab:green", "tab:red")) # "tab:orange",
    fillstyle = 'none'

    attacks = [SubqueriesUnchainedCNAME(), SubqueriesCCV(), CCV_QMIN()]
    titles = ["Subqueries + Unchained", "Subqueries + CNAME Scrubbing", "CNAME Scrubbing + QMIN"]

    name_folders = ["subquery+CNAME", "subquery+CNAME+scrubbing+not_bypassed", "CNAME+QMIN"]
    name_folders = [DATA_J_FOLDER + folder for folder in name_folders]

    # p = plt.figure(figsize=(12, 3))
    # plt.figure(figsize=(12 ,12))
    fig, axs = plt.subplots(1, 3)
    fig.set_figheight(3.5)
    fig.set_figwidth(12.0)
    # plt.rcParams["figure.figsize"] = (20,3)

    resolvers_folders =  ["bind9_18_4", "bind9_18_4_cname", "bind9_18_4_no_chain_val", "powerDNS4_7_0_no_chain_val",
                         "powerDNS4_7_0",  "unbound1_16_0",
                         "unbound1_16_0_cname_bypassed", "unbound1_16_0_no_chain_val"]

    resolver_name_j = ["bind-9.18.4", "powerDNS-4.7.3", "unbound-1.16.0"]

    names_lines = ["Model BIND 9.18.4", "BIND 9.18.4", "Model PowerDNS 4.7.0", "PowerDNS 4.7.3", "Model Unbound 1.16.0", "Unbound 1.16.0", ]

    alphabet = string.ascii_lowercase
    for index, attack in enumerate(attacks):

        # get values
        add_labels = True
        if type(attack) is CCV_QMIN:
            list_list_values_model = get_values_attack_model_with_filename(attack, ["qmin_enabled" + "/" + res for res in resolvers_folders], "res_10labels_01nsdel")
        else :
            list_list_values_model = get_values_attack_model(attack, ["qmin_disabled" + "/" + res for res in resolvers_folders])

        # print("LIST OF VALUES FOR ATTACK : " + attack.name_attack)
        # print(list_list_values_model)

        if type(attack) is SubqueriesCCV:
            list_list_values_attack = get_values_j(name_folders[index], resolver_name_j)
        elif type(attack) is CCV_QMIN:
            list_list_values_attack = get_new_values_j(name_folders[index], ["resolver-" + res for res in resolver_name_j], sorting_type="zone")
        else:
            list_list_values_attack = get_values_j(name_folders[index], resolver_name_j)

        # Limit of the axes
        if type(attack) is SubqueriesUnchainedCNAME:
            ylim = 40
        elif type(attack) is SubqueriesCCV:
            ylim = 80
        else:
            ylim = 205
        xlim = len(list_list_values_attack[0])+1

        print(list_list_values_attack)
        subplot_attack_v2(ax=axs.flat[index], title="({}) ".format(alphabet[index]) + titles[index],#+ attack.name_attack,
                          add_labels_xaxis=add_labels, list_list_values_model=list_list_values_model,
                          list_list_values_attack=list_list_values_attack, list_linestyle=list_linestyle,
                          list_colors=list_colors, list_markers=list_markers, fillstyle=fillstyle, attack=attack,
                          names_lines=names_lines, xlim=xlim, ylim=ylim, fontsize=13)

    filename = "Figure1_chained_attacks"

    # Bbox_to_anchors to add spacing between legend and plots
    leg = fig.legend(names_lines, loc="upper center", ncol=len(names_lines) // 2, fontsize=10, borderaxespad=-1.4,
                     bbox_to_anchor=(0.5, 1.07), frameon=False)  # , mode='expand')
    # Leaves some space between the rows
    # fig.subplots_adjust(hspace=0.3)
    # plt.margins(y=2)
    fig.tight_layout()
    save_figure(plt, filename)

    plt.close()

def main_cname_qmin_delay():
    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    attacks = [CCV_QMIN_Delay()]

    name_folders = ["slowDNS+CNAME+scrubbing+QMIN"]
    name_folders = [DATA_J_FOLDER + folder for folder in name_folders]

    # Create one subplot
    # p = plt.figure(figsize=(12, 3))
    plt.figure(figsize=(8, 6))
    fig, axs = plt.subplots(1, 1)

    fig.set_figheight(4.0)
    fig.set_figwidth(6.0)
    # fig.set_figheight(3.1)
    # fig.set_figwidth(7.5)
    plt.rcParams["figure.figsize"] = (8, 8)

    resolvers_folders = ["bind9_18_4", "bind9_18_4_cname", "bind9_18_4_no_chain_val", "powerDNS4_7_0_no_chain_val",
                         "powerDNS4_7_0", "unbound1_10_0", "unbound1_10_0_cname_bypassed", "unbound1_16_0",
                         "unbound1_16_0_cname_bypassed"]

    resolver_name_j = ["bind-9.18.4", "powerdns-4.7", "unbound-1.10.0", "unbound-1.16.0"]
    resolver_name_j = ["resolver-" + res for res in resolver_name_j]

    names_lines = ["Model BIND 9.18.4", "BIND 9.18.4", "Model PowerDNS 4.7.0", "PowerDNS 4.7.3", "Model Unbound 1.10.0",
                   "Unbound 1.10.0", "Model Unbound 1.16.0", "Unbound 1.16.0", ]
    alphabet = string.ascii_lowercase
    for index, attack in enumerate(attacks):

        add_labels = True

        list_list_values_model = get_new_values_attack_model(attack, ["qmin_enabled/" + res for res in resolvers_folders])
        print("LIST OF VALUES FOR ATTACK : " + attack.name_attack)
        print(list_list_values_model)

        list_list_values_attack = get_new_values_j(name_folders[index], resolver_name_j, sorting_type="delay")
        # Convert to seconds
        list_list_values_attack = [[i/10**3 for i in list_values] for list_values in list_list_values_attack]
        print("List values attack ")
        print(list_list_values_attack)
        subplot_attack(ax=axs, title="SlowDNS + CNAME + Scrubbing + QMIN",
                       add_labels=add_labels, list_list_values_model=list_list_values_model,
                       list_list_values_attack=list_list_values_attack, list_linestyle=list_linestyle,
                       list_colors=list_colors, list_markers=list_markers, fillstyle=fillstyle, attack=attack,
                       names_lines=names_lines)

    filename = attacks[0].folder + "/" + "SLOWDNS_CNAME_Scrubbign_QMIN"

    # Bbox_to_anchors to add spacing between legend and plots
    leg = fig.legend(names_lines, loc="upper center", ncol=len(names_lines) // 2, fontsize=7, borderaxespad=0,
                     bbox_to_anchor=(0.5, 1.07), frameon=False)  # , mode='expand')
    # Leaves some space between the rows
    fig.subplots_adjust(hspace=0.3)
    # plt.margins(y=2)
    fig.tight_layout()
    save_figure(plt, filename)

    plt.close()

def main_delay():
    list_markers = itertools.cycle(('o', 'v', 's', ))#'^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", ))# "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:green", "tab:red"))# , "tab:orange",
    fillstyle = 'none'


    titles = ["CNAME Scrubbing + Delay", "CNAME Scrubbing + QMIN + Delay"]
    attacks = [CCV_Delay(), CCV_QMIN_Delay()]

    name_folders = ["slowDNS+CNAME+scrubbing", "slowDNS+CNAME+scrubbing+QMIN"]
    name_folders = [DATA_J_FOLDER + folder for folder in name_folders]

    # Create one subplot
    # p = plt.figure(figsize=(12, 3))
    plt.figure(figsize=(8, 6))
    fig, axs = plt.subplots(1, 2)

    fig.set_figheight(4)
    fig.set_figwidth(10.0)
    # fig.set_figheight(3.1)
    # fig.set_figwidth(7.5)
    # plt.rcParams["figure.figsize"] = (15, 8)

    resolvers_folders = ["bind9_18_4", "bind9_18_4_cname", "bind9_18_4_no_chain_val", "powerDNS4_7_0_no_chain_val",
                         "powerDNS4_7_0", "unbound1_16_0", "unbound1_16_0_cname_bypassed"]

    resolver_name_j = ["bind-9.18.4", "powerDNS-4.7.3", "unbound-1.16.0",]

    names_lines = ["Model BIND 9.18.4", "BIND 9.18.4", "Model PowerDNS 4.7.0", "PowerDNS 4.7.3", "Model Unbound 1.16.0", "Unbound 1.16.0", ]

    alphabet = string.ascii_lowercase
    for index, attack in enumerate(attacks):

        add_labels = index < 2

        if type(attack) is CCV_QMIN_Delay:
            list_list_values_model = get_values_attack_model_with_filename(attack, ["qmin_enabled/" + res for res in resolvers_folders], "res_10labels_01nsdel")
        else:
            # Do not use QMIN for this attack
            list_list_values_model = get_values_attack_model_with_filename(attack, ["qmin_disabled/" + res for res in resolvers_folders], "res_00labels_01nsdel")

        # print("LIST OF VALUES FOR ATTACK : " + attack.name_attack)
        # print(list_list_values_model)

        if type(attack) is CCV_QMIN_Delay:
            list_list_values_attack = get_new_values_j(name_folders[index], ["resolver-" + res for res in resolver_name_j], sorting_type="delay")
            # Convert to seconds
            list_list_values_attack = [[i/10**3 for i in list_values] for list_values in list_list_values_attack]
            ylim = 275
        else:
            list_list_values_attack = get_values_j(name_folders[index], resolver_name_j)
            ylim = 27

        # print("List values attack ")
        # print(list_list_values_attack)
        subplot_attack_v2(ax=axs.flat[index], title="({}) ".format(alphabet[index]) + titles[index],
                          add_labels_xaxis=add_labels, list_list_values_model=list_list_values_model,
                          list_list_values_attack=list_list_values_attack, list_linestyle=list_linestyle,
                          list_colors=list_colors, list_markers=list_markers, fillstyle=fillstyle, attack=attack,
                          names_lines=names_lines, xlim=1.5, ylim=ylim, fontsize=15)

    filename = "Figure2_delayed_attacks"

    # Bbox_to_anchors to add spacing between legend and plots
    leg = fig.legend(names_lines, loc="upper center", ncol=len(names_lines) // 2, fontsize=12, borderaxespad=0,
                     bbox_to_anchor=(0.5, 1.00), frameon=False)  # , mode='expand')

    # Leaves some space between the rows
    # fig.subplots_adjust(hspace=0.3)
    # plt.margins(y=2)
    # fig.tight_layout() # if activated -> 1.07 in bbox_to_anchor
    save_figure(plt, filename)

    plt.close()


if __name__ == "__main__":
    # main()
    # main_cname_qmin()
    # main_cname_qmin_delay()

    # For paper plots
    main_subqueries_three_qmin()
    main_delay()