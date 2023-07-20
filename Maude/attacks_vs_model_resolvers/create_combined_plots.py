#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import time
import numpy as np
import re
from create_sub_ccv_qmin_files import *
from utils import *
import plot_utils
import model_attack_file

import itertools

from plot_utils import save_high_quality, text_plot_qmin

INCORRECT_ABORTING = "Number of missing attributes is not correct.\n Aborting ... "

'''This file is used to create a plot with the resolvers MODELS combined'''


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


def create_combine_models_only(list_list_values, filename, resolver_names, folder_figures, xtitle, ytitle, x_range,
                               y_range, new_figure_name):

    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = \
        search_missing_attributes_cname(filename, missing_attributes,
                                        ns_del,
                                        cname_chain_length,
                                        nb_labels)

    try:
        assert len(missing_attributes) == 1
    except:
        print(INCORRECT_ABORTING)
        return

    x_labels = {"ns_del": "Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    if xtitle is None:
        xtitle = x_labels[missing_attributes[0]]
    ax.set_xlabel(xtitle, fontsize=12)
    # # of subqueries
    ax.set_ylabel(ytitle, fontsize=12)

    if x_range is None:
        x_range = (0, len(list_list_values[0]))
    ax.set_xlim(*x_range)
    ax.set_ylim(*y_range)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)

    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers \n with Scrubbing + CNAME \n Fixed values : {vars} and {qmin}'.format(
     vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    ax.grid()
    for list_values in list_list_values:
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        ax.plot(x, list_values, color=color, linestyle=linestyle, marker=marker, fillstyle=fillstyle)  # marker='o')

    plot_path = folder_figures + new_figure_name
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_simple(list_list_values, filename, resolver_names, folder_path):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    x_labels = "TOBEDEFINED"

    ax.set_xlabel(x_labels, fontsize=12)
    ax.set_ylabel('Amplification factor', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 1700)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys()]
    vars = ", ".join(fixed)
    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title('Amplification factor c/nameserver with Sub+CCV+QMIN \n Fixed values : {vars}'.format(vars=vars),
                 fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_path + "fig_" + filename.split(".")[0] + ".jpg"

    # remove the previous path
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

    for i in range(0, len(resolver_names)):
        list_values = list_list_values[i]
        max_point_annot(x, list_values, resolver_names[i], i / len(list_list_values))

    plt.legend(resolver_names)

    plt.savefig(plot_path)
    plt.close()


def create_combined_plots_dname(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    dname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, dname_chain_length, nb_labels = search_missing_attributes_dname(filename,
                                                                                                missing_attributes,
                                                                                                ns_del,
                                                                                                dname_chain_length,
                                                                                                nb_labels)

    try:
        assert len(missing_attributes) == 1
    except:
        print(INCORRECT_ABORTING)
        return

    x_labels = {"ns_del": "Number of delegations", "dname_chain_length": "Length of the DNAME chain",
                "nb_labels": "Number of labels"}
    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 100)

    # fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)), "dname_chain_length": "DNAME_length={}".format(str(dname_chain_length)), "nb_labels": "#Labels={}".format(str(nb_labels))}
    # fixed =  [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = "DNAME_length={}".format(str(dname_chain_length))  # ", ".join(fixed)

    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# Queries sent to victim nameserver w.r.t. MODEL resolvers \n with Sub+Unchained with DNAME\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_" + filename.split(".")[0]
    plot_path = folder_figures + "fig_sub_unchained_dname_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)
    plt.close()

    del fig


def create_combined_plots_cname(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = search_missing_attributes_cname(filename,
                                                                                                missing_attributes,
                                                                                                ns_del,
                                                                                                cname_chain_length,
                                                                                                nb_labels)

    try:
        assert len(missing_attributes) == 1
    except:
        print(INCORRECT_ABORTING)

    x_labels = {"ns_del": "Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 110)
    

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)

    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers \n with Sub+Unchained with CNAME\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_sub_unchained_cname_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_unchained_cname(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = search_missing_attributes_cname(filename,
                                                                                                missing_attributes,
                                                                                                ns_del,
                                                                                                cname_chain_length,
                                                                                                nb_labels)

    try:
        assert len(missing_attributes) == 1
    except:
        print(INCORRECT_ABORTING)
        return

    x_labels = {"ns_del": "Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)

    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, len(list_list_values[0]))
    ax.set_ylim(0, 110)
    

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)

    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers \n with Unchained + CNAME')

    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    ax.grid()
    for list_values in list_list_values:
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        ax.plot(x, list_values, color=color, linestyle=linestyle, marker=marker, fillstyle=fillstyle)  # marker='o')

    plot_path = folder_figures + "fig_unchained_cname_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_cname_scrub(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = \
        search_missing_attributes_cname(filename, missing_attributes,
                                        ns_del,
                                        cname_chain_length,
                                        nb_labels)

    try:
        assert len(missing_attributes) == 1
    except:
        print("Number of missing attributes is not correct.\n Aborting ... ")
        return

    x_labels = {"ns_del": "Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, len(list_list_values[0]))
    ax.set_ylim(0, 210)
    

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)

    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers \n with Scrubbing + CNAME')

    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    ax.grid()
    for list_values in list_list_values:
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        ax.plot(x, list_values, color=color, linestyle=linestyle, marker=marker, fillstyle=fillstyle)  # marker='o')

    plot_path = folder_figures + "fig_cname_scrubbing_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_cname_scrub_qmin(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = search_missing_attributes_cname(filename,
                                                                                                missing_attributes,
                                                                                                ns_del,
                                                                                                cname_chain_length,
                                                                                                nb_labels)

    try:
        assert len(missing_attributes) == 1
    except:
        print("Number of missing attributes is not correct.\n Aborting ... ")
        return

    x_labels = {"ns_del": "Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)
    #
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, len(list_list_values[0]))
    ax.set_ylim(0, 210)
    

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)

    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers \n with Scrubbing + CNAME + QMIN with  #Labels={}'.format(
            str(nb_labels)))  # \n Fixed values : {vars} and {qmin}'.format(
    # vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    ax.grid()
    for list_values in list_list_values:
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        ax.plot(x, list_values, color=color, linestyle=linestyle, marker=marker, fillstyle=fillstyle)  # marker='o')

    plot_path = folder_figures + "fig_cname_scrubbing_qmin_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_unchained_cname_qmin(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = search_missing_attributes_cname(filename,
                                                                                                missing_attributes,
                                                                                                ns_del,
                                                                                                cname_chain_length,
                                                                                                nb_labels)

    try:
        assert len(missing_attributes) == 1
    except:
        print("Number of missing attributes is not correct.\n Aborting ... ")
        return

    x_labels = {"ns_del": "Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)
    #
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, len(list_list_values[0]))
    ax.set_ylim(0, 110)
    

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)

    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers \n with Unchained + CNAME + QMIN with #Labels = {}'.format(
            str(nb_labels)), )

    ax.grid()
    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    for list_values in list_list_values:
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        ax.plot(x, list_values, color=color, linestyle=linestyle, marker=marker, fillstyle=fillstyle)  # marker='o')

    plot_path = folder_figures + "fig_unchained_cname_qmin_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_sub_cname_scrub_delay(list_list_values, filename, resolver_names, folder_figures):
    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    ns_del = 1
    cname_chain_length = re.search(r"(\d+)cnamelength", filename).group(1)
    nb_labels = 0

    # match = re.search(r"(\d+)ns_delay", filename)
    # ns_delay = match.group(1)

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    ax.set_xlabel("Artificial Delay (ms or time unit)")  # x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('Duration of client query (s)', fontsize=12)

    ax.set_xlim(0, 1500)
    ax.set_ylim(0, 50)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys()]
    vars = ", ".join(fixed)

    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        'Duration of client query w.r.t. MODEL resolvers\n with Sub+CNAME scrubbing +Delay (slow CNAME)\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    print(len(list_list_values[0]))
    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_sub_cname_scrubbing_delay_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_sub_cname_scrub_qmin_delay(list_list_values, filename, resolver_names, folder_figures):
    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    ns_del = 1
    cname_chain_length = re.search(r"(\d+)cnamelength", filename).group(1)
    nb_labels = 0

    # match = re.search(r"(\d+)ns_delay", filename)
    # ns_delay = match.group(1)

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    ax.set_xlabel("Artificial Delay (ms or time unit)")  # x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('Duration of client query (s)', fontsize=12)

    ax.set_xlim(0, 1500)
    ax.set_ylim(0, 300)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys()]
    vars = ", ".join(fixed)

    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        'Duration of client query w.r.t. MODEL resolvers\n with Sub+CNAME scrubbing + QMIN + Delay (slow CNAME)\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    print(len(list_list_values[0]))
    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_sub_cname_scrubbing_qmin_delay_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig



def create_combined_plots_cname_scrub_delay(list_list_values, filename, resolver_names, folder_figures):
    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    ns_del = 1
    cname_chain_length = 17  # re.search(r"(\d+)cnamelength", filename).group(1)
    nb_labels = 0

    # match = re.search(r"(\d+)ns_delay", filename)
    # ns_delay = match.group(1)

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    ax.set_xlabel("Artificial Delay (ms or time unit)")  # x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('Duration of client query (s)', fontsize=12)

    ax.set_xlim(0, 1700)
    ax.set_ylim(0, 250)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys()]
    vars = ", ".join(fixed)

    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        'Duration of client query w.r.t. MODEL resolvers\n with Scrubbing + CNAME + Delay (slow CNAME)')  # Fixed values : {vars} and {qmin}'.format(
    # vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    print(len(list_list_values[0]))

    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    ax.grid()
    for list_values in list_list_values:
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        ax.plot(x, list_values, color=color, linestyle=linestyle, marker=marker, fillstyle=fillstyle)  #

    plot_path = folder_figures + "fig_cname_scrubbing_delay_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_cname_scrub_qmin_delay(list_list_values, filename, resolver_names, folder_figures):
    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    ns_del = 1

    cname_chain_length = 17  # re.search(r"(\d+)cnamelength", filename).group(1)
    nb_labels = 0

    # match = re.search(r"(\d+)ns_delay", filename)
    # ns_delay = match.group(1)

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    ax.set_xlabel("Artificial Delay (ms or time unit)")  # x_labels[missing_attributes[0]], fontsize=12)
    ax.set_ylabel('Duration of client query (s)', fontsize=12)

    ax.set_xlim(0, 1700)
    ax.set_ylim(0, 310)

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys()]
    vars = ", ".join(fixed)

    ax.set_title(
        'Duration of client query w.r.t. MODEL resolvers\n with Scrubbing + CNAME + QMIN + Delay (slow CNAME)')  # Fixed values : {vars} and {qmin}'.format(
    # vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    print(len(list_list_values[0]))

    list_markers = itertools.cycle(('o', 'v', 's', '^'))  # "x", "d",))  # "p","*","s", "o", "."))
    list_linestyle = itertools.cycle(("-", "--", ":", "-."))
    list_colors = itertools.cycle(("tab:blue", "tab:orange", "tab:green", "tab:red"))
    fillstyle = 'none'

    ax.grid()
    for list_values in list_list_values:
        color = next(list_colors)
        marker = next(list_markers)
        linestyle = next(list_linestyle)
        ax.plot(x, list_values, color=color, linestyle=linestyle, marker=marker, fillstyle=fillstyle)  #
    # ax.grid()

    plot_path = folder_figures + "fig_cname_scrubbing_qmin_delay_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_sub_cname_scrub_qmin(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, 10 + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    ns_del = 1
    cname_chain_length = re.search(r"(\d+)cnamelength", filename).group(1)
    nb_labels = 0

    # match = re.search(r"(\d+)ns_delay", filename)
    # ns_delay = match.group(1)

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    ax.set_xlabel("Number of delegations")  # x_labels[missing_attributes[0]], fontsize=12)
    #
    ax.set_ylabel('Number of queries received', fontsize=12)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1700)
    

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys()]
    vars = ", ".join(fixed)

    ax.set_title(
        'Number of queries received by victim w.r.t. MODEL resolvers\n with Sub+CNAME scrubbing +QMIN\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    print(len(list_list_values[0]))
    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_sub_cname_scrubbing_qmin_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_dname_scrub_qmin(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, 10 + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    ns_del = 1
    dname_chain_length = re.search(r"(\d+)dnamelength", filename).group(1)
    nb_labels = 0

    # match = re.search(r"(\d+)ns_delay", filename)
    # ns_delay = match.group(1)

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    ax.set_xlabel("Number of delegations")  # x_labels[missing_attributes[0]], fontsize=12)
    #
    ax.set_ylabel('Number of queries received', fontsize=12)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1700)

    vars = "DNAME_length={}".format(str(dname_chain_length))

    ax.set_title(
        'Number of queries received by victim w.r.t. MODEL resolvers\n with Sub+DNAME+Scrubbing+QMIN\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    print(len(list_list_values[0]))
    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_sub_dname_scrubbing_qmin_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def create_combined_plots_dname_scrub_delay(list_list_values, filename, resolver_names, folder_figures):
    x = range(0, 1700, 200)
    fig = plt.figure()
    ax = fig.add_subplot()

    ns_del = 1
    dname_chain_length = re.search(r"(\d+)dnamelength", filename).group(1)
    nb_labels = 0

    # match = re.search(r"(\d+)ns_delay", filename)
    # ns_delay = match.group(1)

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    ax.set_xlabel("Artificial Delay (ms or time unit)")  # x_labels[missing_attributes[0]], fontsize=12)
    #
    ax.set_ylabel('Duration of client query (ms or time unit)', fontsize=12)

    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 50)
    


    vars = "DNAME_length={}".format(str(dname_chain_length))  # ", ".join(fixed)

    ax.set_title(
        'Duration of client query w.r.t. MODEL resolvers\n with Sub+DNAME scrubbbing+Delay (slow DNAME)\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    print(len(list_list_values[0]))
    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_sub_dname_scrubbing_delay_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()
    plt.close()

    del fig


def create_combined_plots(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = search_missing_attributes_cname(filename,
                                                                                                missing_attributes,
                                                                                                ns_del,
                                                                                                cname_chain_length,
                                                                                                nb_labels)

    try:
        assert (len(missing_attributes) == 1)
    except:
        print("Number of missing attributes is not correct.\n Aborting ... ")
        return

    x_labels = {"ns_del": "Number of delegations", "cname_chain_length": "Length of the CNAME chain",
                "nb_labels": "Number of labels"}
    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel(x_labels[missing_attributes[0]], fontsize=12)
    #
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 1700)
    

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "cname_chain_length": "CNAME_length={}".format(str(cname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)

    # RElated to the previous : find from the filename what are the fixed attributes
    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers with Sub+CCV+QMIN \n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_" + filename.split(".")[0] + ".jpg"
    if os.path.exists(plot_path):
        os.remove(plot_path)
        # print("removed plot")

    plt.legend(resolver_names)

    plt.savefig(plot_path)
    plt.close()

    del fig


def create_combined_plots_sub_cname_val(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    cname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, cname_chain_length, nb_labels = search_missing_attributes_cname(filename,
                                                                                                missing_attributes,
                                                                                                ns_del,
                                                                                                cname_chain_length,
                                                                                                nb_labels)

    try:
        assert (len(missing_attributes) == 1)
    except:
        print("Number of missing attributes is not correct.\n Aborting ... ")
        return

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel("Number of delegations", fontsize=12)
    #
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 200)

    vars = "CNAME_length={}".format(str(cname_chain_length))  # ", ".join(fixed)

    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers\n with Sub+CNAME scrubbing\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)

    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_sub_cname_scrubbing_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)
    plt.close()

    del fig


def create_combined_plots_dname_val(list_list_values, filename, resolver_names, folder_figures):
    x = range(1, len(list_list_values[0]) + 1)
    fig = plt.figure()
    ax = fig.add_subplot()

    missing_attributes = []
    ns_del = 0
    dname_chain_length = 0
    nb_labels = 0

    missing_attributes, ns_del, dname_chain_length, nb_labels = search_missing_attributes_dname(filename,
                                                                                                missing_attributes,
                                                                                                ns_del,
                                                                                                dname_chain_length,
                                                                                                nb_labels)

    try:
        assert (len(missing_attributes) == 1)
    except:
        print("Number of missing attributes is not correct.\n Aborting ... ")
        return

    # Determine the x_axis label regarding the missing_attributes attribute in the filename
    missing_att = missing_attributes[0]
    ax.set_xlabel("Number of delegations", fontsize=12)
    ax.set_ylabel('# queries sent to victim nameserver', fontsize=12)

    ax.set_xlim(0, 10 + 1)
    ax.set_ylim(0, 200)
    

    fixed_vars = {"ns_del": "#Del={}".format(str(ns_del)),
                  "dname_chain_length": "DNAME_length={}".format(str(dname_chain_length)),
                  "nb_labels": "#Labels={}".format(str(nb_labels))}
    fixed = [fixed_vars[i] for i in fixed_vars.keys() if i != missing_att]
    vars = ", ".join(fixed)

    ax.set_title(
        '# queries sent to victim nameserver w.r.t. MODEL resolvers\n with Sub+DNAME scrubbing\n Fixed values : {vars} and {qmin}'.format(
            vars=vars, qmin=text_plot_qmin(QMIN_DEACTIVATED)), fontsize=11)


    ax.grid()
    for list_values in list_list_values:
        ax.plot(x, list_values, marker='o')

    plot_path = folder_figures + "fig_sub_dname_scrubbing_model"
    plot_path_jpg = plot_path + ".jpg"
    if os.path.exists(plot_path_jpg):
        os.remove(plot_path_jpg)

    plt.legend(resolver_names)

    plt.savefig(plot_path_jpg)
    save_high_quality(plt, plot_path)

    plt.close()

    del fig


def main():
    scrubbing = True
    resolver_models = [Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0_CNAME_BYPASSED(),
                       which_powerdns(scrubbing, QMIN_DEACTIVATED), Unbound1_10_0(),
                       Unbound1_16_0()]  # PowerDNS4_7_0()]
    attack_folder = "sub-ccv-qmin-a/"
    # attacks_vs_model_resolvers
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

        create_combined_plots(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_dname():
    scrubbing = False
    resolver_models = [Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(),
                       which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4_NO_CHAIN_VALIDATION()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = model_attack_file.SubqueriesUnchainedDNAME().folder + "/" + qmin_folder + "/"
    # attacks_vs_model_resolvers
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

        create_combined_plots_dname(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_cname():
    scrubbing = False

    resolver_models = [Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(),
                       which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4_NO_CHAIN_VALIDATION()]  # ,Unbound1_10_0(), Unbound1_16_0(), PowerDNS4_7_0()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = SubqueriesUnchainedCNAME().folder + "/" + qmin_folder + "/"
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = ["Model " + res.name for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(res.folder) for res in resolver_models]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

        create_combined_plots_cname(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_unchained_cname():
    scrubbing = False

    resolver_models = [Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(),
                       which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    # attack_folder = "sub-unchained-cname/"
    attack_folder = UnchainedCNAME().folder + "/" + qmin_folder + "/"
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = ["Model " + res.name for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(res.folder) for res in resolver_models]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]
        resolver_names = ["Model Unbound 1.10.0", "Model Unbound 1.16.0", "Model PowerDNS 4.7.0", "Model BIND 9.18.4", ]
        create_combined_plots_unchained_cname(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_cname_scrub():
    scrubbing = True

    resolver_models = [Unbound1_10_0(), Unbound1_16_0(), utils.which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    # attack_folder = "sub-unchained-cname/"
    attack_folder = CCV().folder + "/" + qmin_folder + "/"
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = ["Model " + res.name for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(res.folder) for res in resolver_models]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]
        resolver_names = ["Model Unbound 1.10.0", "Model Unbound 1.16.0", "Model PowerDNS 4.7.0", "Model BIND 9.18.4", ]
        # create_combined_plots_cname_scrub(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)
        create_combine_models_only(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS,
                                   xtitle="Length of the CNAME chain",
                                   ytitle="# queries sent to victim nameserver",
                                   x_range=(0, len(list_list_values[0])),
                                   y_range=(0, 210),
                                   new_figure_name="fig_cname_scrubbing_model")

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_cname_scrub_qmin():
    scrubbing = True

    resolver_models = [Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0_CNAME_BYPASSED(),
                       utils.which_powerdns(scrubbing, QMIN_DEACTIVATED), Bind9_18_4()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    # attack_folder = "sub-unchained-cname/"
    attack_folder = CCV_QMIN().folder + "/" + qmin_folder + "/"
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = ["Model " + res.name for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(res.folder) for res in resolver_models]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]
        resolver_names = ["Model Unbound 1.10.0", "Model Unbound 1.16.0", "Model PowerDNS 4.7.0", "Model BIND 9.18.4", ]
        create_combined_plots_cname_scrub_qmin(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_dname_validation():
    scrubbing = True
    # Special case for BIND
    resolver_models = [Unbound1_10_0(), Unbound1_16_0(), which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4_NO_CHAIN_VALIDATION()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = model_attack_file.SubqueriesDNAME_Chain_validation().folder + "/" + qmin_folder + "/"

    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = ["Model " + res.name for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(res.folder) for res in resolver_models]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

        create_combined_plots_dname_val(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_sub_cname_scrub_delay():
    scrubbing = True

    resolver_models = [Unbound1_10_0(), Unbound1_16_0(), which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4()]

    # attack_folder = "sub-ccv-delay/"
    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = SubqueriesCCV_Delay().folder + "/" + qmin_folder + "/"
    # attacks_vs_model_resolvers
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

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

        lists_to_float = [[float(i) / 10 ** 3 for i in list_values] for list_values in list_list_values]

        create_combined_plots_sub_cname_scrub_delay(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))

def main_sub_cname_scrub_qmin_delay():
    scrubbing = True

    resolver_models = [Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0_CNAME_BYPASSED(), which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4_CNAME()]

    # attack_folder = "sub-ccv-delay/"
    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = SubqueriesCCVQMINA_Delay().folder + "/" + qmin_folder + "/"
    # attacks_vs_model_resolvers
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

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

        lists_to_float = [[float(i) / 10 ** 3 for i in list_values] for list_values in list_list_values]

        create_combined_plots_sub_cname_scrub_qmin_delay(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_cname_scrub_delay():
    scrubbing = True

    resolver_models = [Unbound1_10_0(), Unbound1_16_0(), which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4()]  # [Unbound1_16_0(), PowerDNS4_7_0(), Bind9_18_4()]  # Unbound1_10_0(),Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(), PowerDNS4_7_0_NO_CHAIN_VALIDATION()],

    # attack_folder = "sub-ccv-delay/"
    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = CCV_Delay().folder + "/" + qmin_folder + "/"
    # attacks_vs_model_resolvers
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

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

        lists_to_float = [[float(i) / 10 ** 3 for i in list_values] for list_values in list_list_values]

        resolver_names = ["Model Unbound 1.10.0", "Model Unbound 1.16.0", "Model PowerDNS 4.7.0", "Model BIND 9.18.4", ]
        create_combined_plots_cname_scrub_delay(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_cname_scrub_qmin_delay():
    scrubbing = True

    resolver_models = [Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0_CNAME_BYPASSED(),
                       which_powerdns(scrubbing, QMIN_DEACTIVATED), Bind9_18_4()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = CCV_QMIN_Delay().folder + "/" + qmin_folder + "/"
    # attacks_vs_model_resolvers
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

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

        lists_to_float = [[float(i) / 10 ** 3 for i in list_values] for list_values in list_list_values]
        print(lists_to_float)
        resolver_names = ["Model Unbound 1.10.0", "Model Unbound 1.16.0", "Model PowerDNS 4.7.0", "Model BIND 9.18.4", ]

        create_combined_plots_cname_scrub_qmin_delay(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_sub_cname_scrub_qmin():
    scrubbing = True
    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = model_attack_file.SubqueriesCCVQMINA().folder + "/" + qmin_folder + "/"

    resolver_models = [Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0_CNAME_BYPASSED(),
                       which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4_CNAME()]  # [Unbound1_16_0(), PowerDNS4_7_0(), Bind9_18_4()]  # Unbound1_10_0(),Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(), PowerDNS4_7_0_NO_CHAIN_VALIDATION()],

    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

        create_combined_plots_sub_cname_scrub_qmin(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_unchained_cname_qmin():
    scrubbing = False
    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = model_attack_file.UnchainedCNAMEQMIN().folder + "/" + qmin_folder + "/"

    resolver_models = [Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(),
                       utils.which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4()]  # [Unbound1_16_0(), PowerDNS4_7_0(), Bind9_18_4()]  # Unbound1_10_0(),Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(), PowerDNS4_7_0_NO_CHAIN_VALIDATION()],

    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

        resolver_names = ["Model Unbound 1.10.0", "Model Unbound 1.16.0", "Model PowerDNS 4.7.0", "Model BIND 9.18.4", ]
        create_combined_plots_unchained_cname_qmin(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_sub_dname_scrub_qmin():
    scrubbing = True
    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = model_attack_file.SubqueriesDCVQMINA().folder + "/" + qmin_folder + "/"

    resolver_models = [Unbound1_10_0_CNAME_BYPASSED(), Unbound1_16_0_CNAME_BYPASSED(),
                       which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4()]  # [Unbound1_16_0(), PowerDNS4_7_0(), Bind9_18_4()]  # Unbound1_10_0(),Unbound1_10_0_NO_CHAIN_VALIDATION(), Unbound1_16_0_NO_CHAIN_VALIDATION(), PowerDNS4_7_0_NO_CHAIN_VALIDATION()],

    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

        create_combined_plots_dname_scrub_qmin(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_sub_cname_validation():
    scrubbing = True

    resolver_models = [Unbound1_10_0(), Unbound1_16_0(), which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4_CNAME()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = model_attack_file.SubqueriesCCV().folder + "/" + qmin_folder + "/"
    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = ["Model " + res.name for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(res.folder) for res in resolver_models]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) for i in list_values] for list_values in list_list_values]

        create_combined_plots_sub_cname_val(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


def main_dname_scrub_delay():
    scrubbing = True

    resolver_models = [Unbound1_10_0(), Unbound1_16_0(), which_powerdns(scrubbing, QMIN_DEACTIVATED),
                       Bind9_18_4()]

    qmin_folder = "qmin_disabled" if QMIN_DEACTIVATED else "qmin_enabled"
    attack_folder = model_attack_file.SubqueriesDNAMEChainVal_Delay().folder + "/" + qmin_folder + "/"

    FOLDER_COMBINED_RESULTS = attack_folder + "combined/"
    check_folder_exists(FOLDER_COMBINED_RESULTS)

    print("#" * 20 + "\n")
    print("Start of the creation of the combined plots for the attack {} ....\n".format(attack_folder[:-1]))
    time1 = time.perf_counter()

    resolver_names = [res.folder for res in resolver_models]

    FOLDERS_RESULTS = [attack_folder + "{}/results/".format(name) for name in resolver_names]
    FOLDERS_RESULTS_MEASUREMENTS = [f + "measurements/" for f in FOLDERS_RESULTS]
    for i in range(0, len(resolver_models)):
        check_folder_exists(FOLDERS_RESULTS[i])
        check_folder_exists(FOLDERS_RESULTS_MEASUREMENTS[i])

    # Look for all the measurements files in the first resolver folder
    for filename in os.listdir(FOLDERS_RESULTS_MEASUREMENTS[0]):
        files = [os.path.join(folder, filename) for folder in FOLDERS_RESULTS_MEASUREMENTS]

        # Check that the same files exist in the other resolvers' folders
        if not all(os.path.isfile(f) for f in files):
            print("{} doesn't exist in all the folders. Please compute it. PASS...".format(filename))
            continue

        list_list_values = plot_utils.extract_values_from_files(files)

        # Check that all the lists have the same size
        check_lists_size(list_list_values)

        lists_to_float = [[float(i) / 10 ** 3 for i in list_values] for list_values in list_list_values]

        create_combined_plots_dname_scrub_delay(lists_to_float, filename, resolver_names, FOLDER_COMBINED_RESULTS)

    time2 = time.perf_counter()

    print("DONE ! All the plots have been created in {:.3f} seconds !".format(time2 - time1))


if __name__ == "__main__":

    global QMIN_DEACTIVATED
    QMIN_DEACTIVATED = False

    # main_dname()
    # main_dname_validation()
    # main_dname_scrub_delay()
    #
    # main_cname()
    # main_sub_cname_validation()()
    main_sub_cname_scrub_delay()

    # main_dname()
    # main_dname_validation()
    # main_dname_scrub_delay()
    # main_sub_dname_scrub_qmin()
    #
    # main_cname()
    # main_sub_cname_validation()()
    # main_sub_cname_scrub_delay()
    # main_sub_cname_scrub_qmin()
    # main_sub_cname_scrub_qmin_delay()

    # main_unchained_cname()
    # main_unchained_cname_qmin()

    # main_cname_scrub()
    # main_cname_scrub_delay()
    # main_cname_scrub_qmin()
    # main_cname_scrub_qmin_delay()

    QMIN_DEACTIVATED = True
    #
    # main_dname()
    # main_dname_validation()
    # main_dname_scrub_delay()
    # main_sub_dname_scrub_qmin()
    #
    # main_cname()
    # main_sub_cname_validation()
    main_sub_cname_scrub_delay()
    # main_sub_cname_scrub_qmin()
    # main_sub_cname_scrub_qmin_delay()
