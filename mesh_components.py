import numpy as np
import pandas as pd
from collections import OrderedDict
import datetime, time

import matplotlib.pyplot as plt

from databroker import get_events, get_table, DataBroker as DB

import ipywidgets as widgets
from ipywidgets import interact, fixed

import matplotlib as mpl
from cycler import cycler
new_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
              '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
              '#bcbd22', '#17becf']

mpl.rcParams['axes.prop_cycle'] = cycler(color=new_colors)


# Functions
def stopped(header):
    try:
        status = header.stop.exit_status
    except AttributeError:
        status = 'Python crash before exit'
    
    if status == 'success' and header.start.plan_name == 'mesh':
        return True
    else:
        return False
    
    
def get_scan_id_dict(headers):
    return OrderedDict([(get_scan_desc(header), header) for header in headers[::-1] if stopped(header)])

def get_columns(header):
    try:
        columns = get_table(header).columns
        col_list = sorted(list(columns))
        return col_list
    except:
        return []

def get_scanned_motor(header):
    try:
        return ' '.join(header.start.motors)
    except:
        return ''

def get_scan_desc(header):
    return '{} {} {}'.format(header.start.scan_id, header.start['plan_name'], get_scanned_motor(header))


# Widgets

today_string = str(datetime.datetime.now().date())
DB_search_widget = widgets.Text(description='Database search',
                                value='start_time=\'{}\''.format(today_string))
refresh_headers_widget = widgets.Button(description='Refresh')

select_scan_id_widget = widgets.Select(description='Select scan id')

select_I_widget = widgets.Dropdown(description='I')

plot_button = widgets.Button(description='Plot')
clear_button = widgets.Button(description='Clear')


# bindings

def wrap_refresh(change):
    try:
        query = eval("dict({})".format(DB_search_widget.value))
        headers = DB(**query)
    except NameError:
        headers = []
        DB_search_widget.value += " -- is an invalid search"
    
    scan_id_dict = get_scan_id_dict(headers)
    select_scan_id_widget.options = scan_id_dict

    
refresh_headers_widget.on_click(wrap_refresh)
    
def wrap_select_scan_id(change):
    columns = get_columns(select_scan_id_widget.value)
    select_I_widget.options = columns
    default_I = 'gc_diag_grid'
    try:
        select_I_widget.value = default_y
    except:
        pass

select_scan_id_widget.observe(wrap_select_scan_id)


def wrap_plotit(change):
    header = select_scan_id_widget.value
    table = get_table(header)
    
    det_name = select_I_widget.value
    
    def plot_mesh(header, table, det_name, vmin=np.nanpercentile(table[det_name],5),
                                       vmax=np.nanpercentile(table[det_name], 95)):
        plt.figure()
        motor_name_0, motor_name_1 = header.start.motors
        shape = header.start.shape
        I = table[det_name].values.reshape(shape)
        motor_0 = table[motor_name_0].values.reshape(shape)
        motor_1 = table[motor_name_1].values.reshape(shape)

        plt.pcolormesh(motor_0, motor_1, I, vmin=vmin, vmax=vmax)
        plt.title("Scan_id {}".format(header.start.scan_id))
        plt.xlabel(motor_name_0)
        plt.ylabel(motor_name_1)
        plt.colorbar(label=det_name)


    interact(plot_mesh, header=fixed(header), table=fixed(table), det_name=fixed(det_name),
                vmin=(table[det_name].min(), table[det_name].max()),
                vmax=(table[det_name].min(), table[det_name].max()))

plot_button.on_click(wrap_plotit)

def wrap_clearit(change):
    plt.cla()
    
clear_button.on_click(wrap_clearit)

