#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt


def save_to_svg(plt, filename):
    new_filename = filename + '.svg'
    if os.path.exists(new_filename):
        os.remove(new_filename)
    plt.savefig(new_filename, format='svg', dpi=1200)
    save_to_pdf(plt, filename)


def save_to_eps(plt, filename):
    new_filename = filename + '.eps'
    if os.path.exists(new_filename):
        os.remove(new_filename)
    plt.savefig(new_filename, format='eps')


def save_to_pdf(plt, filename):
    new_filename = filename + '.pdf'
    if os.path.exists(new_filename):
        os.remove(new_filename)
    plt.savefig(new_filename, format='pdf')


def save_high_quality(plt, filename):
    save_to_pdf(plt, filename)
    save_to_eps(plt, filename)


def extract_values_from_files(files):
    list_list_values = []
    for f in files:
        file = open(f, "r")
        for row in file:
            list_values = row.split(",")[:-1]
        file.close()
        print("Values of file {} : ".format(f))
        print(list_values)
        list_list_values.append(list_values)
    return list_list_values


def text_plot_qmin(QMIN_DEACTIVATED):
    if QMIN_DEACTIVATED:
        return "with QMIN disabled"
    return "with QMIN enabled"
