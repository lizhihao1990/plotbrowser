# -*- coding: utf-8 -*-
"""
Plot browser in PySide/PyQt4
Created on Nov 23 2013

@author: Christopher Liman
Features:

Todo:

"""

from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#import sip
#import sys
#from copy import copy
#from re import split
#from functools import partial
from spyderlib.qt import QtGui
from spyderlib.qt import QtCore
from spyderlib.qt.QtCore import Slot
#from PySide import QtGui
#from PySide import QtCore
from IPython.lib import guisupport
import webcolors
import plotbrowser_ui

#assert sip.getapi('QString') == 2
#sys._excepthook = sys.excepthook
#def exception_hook(exctype, value, traceback):
#    sys._excepthook(exctype, value, traceback)
#    sys.exit(1)
#sys.excepthook = exception_hook


class PlotBrowser(QtGui.QMainWindow, plotbrowser_ui.Ui_PlotBrowser):
    """Graph explorer"""
    def __init__(self, parent=None):
        super(PlotBrowser, self).__init__(parent)  # boilerplate
        self.setupUi(self)  # boilerplate
        # allows editing of item names
        self.listwidgetitemflags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | \
            QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
        # figures
        self.lineEdit_figwidth.editingFinished.connect(self.lineEdit_figdims_editingFinished)
        self.lineEdit_figheight.editingFinished.connect(self.lineEdit_figdims_editingFinished)
        # axes
        self.lineEdit_xmin.editingFinished.connect(self.lineEdit_limits_editingFinished)
        self.lineEdit_xmax.editingFinished.connect(self.lineEdit_limits_editingFinished)
        self.lineEdit_ymin.editingFinished.connect(self.lineEdit_limits_editingFinished)
        self.lineEdit_ymax.editingFinished.connect(self.lineEdit_limits_editingFinished)
        # ticks
        # legend
        # lines
        self.linestyles = list(mpl.lines.Line2D.lineStyles.items())
        self.comboBox_linestyle.addItems([repr(item[0]) + " (" + item[1] + ")" for item in self.linestyles])
        self.markers = list(mpl.markers.MarkerStyle.markers.items())
        self.comboBox_markerstyle.addItems([repr(item[0]) + " (" + item[1] + ")" for item in self.markers])
        # fonts
        self.selectedfont = QtGui.QFont()
        self.fontdialog = QtGui.QFontDialog()
        self.on_pushButton_refreshlist_clicked()
        #self.actionCopy_path.triggered.connect(self.copy_path)
        #self.actionExit.triggered.connect(partial(self.closeEvent, QtGui.QCloseEvent()))  # use partial to pass argument to slot
        #self.actionExit.triggered.connect(self.close)
        #self.treeWidget.addAction(self.actionCopy_path)  # adds action to treeWidget's right click menu

    def rgb_frac_to_name(self, color):
        """
        >>> browser.rgb_frac_to_name([.5,.5,.5])
        'grey'
        >>> browser.rgb_frac_to_name('k')
        'black'
        """
        shortcolor_to_name = {'b': 'blue', 'g': 'green', 'r': 'red', 'c': 'cyan', 'm': 'magenta',
                              'y': 'yellow', 'k': 'black', 'w': 'white'}
        if color in shortcolor_to_name.keys():
            return shortcolor_to_name[color]
        elif isinstance(color, basestring):
            return color
        else:
            colorperc = [str(x * 100) + '%' for x in color]
            try:
                return webcolors.rgb_percent_to_name(colorperc)
            except ValueError:
                return None

    def setcurrenttext(self, widget, text):
        widget.setCurrentIndex(widget.findText(text))

    @Slot()
    def on_pushButton_refreshlist_clicked(self):
        """Refreshes figures list, selects last figure"""
        self.listWidget_figures.clear()
        current_row = -1
        for i in plt.get_fignums():
            self.listWidget_figures.addItem(plt.figure(i).canvas.get_window_title())
            current_row = self.listWidget_figures.count() - 1
            self.listWidget_figures.item(current_row).fig = plt.figure(i)
            self.listWidget_figures.item(current_row).setFlags(self.listwidgetitemflags)
        if current_row != -1:
            self.listWidget_figures.setCurrentRow(current_row)
            self.on_listWidget_figures_itemClicked()

    def refresh_listWidget_axes(self):
        self.listWidget_axes.clear()
        self.listWidget_lines.clear()
        current_row = -1
        for ax in self.fig.axes:
            self.listWidget_axes.addItem(ax.get_title())
            current_row = self.listWidget_axes.count() - 1
            self.listWidget_axes.item(current_row).setFlags(self.listwidgetitemflags)  # changing flags also triggers name changed but I guess that's ok
        if current_row != -1:
            self.listWidget_axes.setCurrentRow(current_row)
            self.on_listWidget_axes_itemClicked()

    def refresh_listWidget_lines(self):
        self.listWidget_lines.clear()
        current_row = -1
        for line in self.ax.lines:
            self.listWidget_lines.addItem(line.get_label())
            current_row = self.listWidget_lines.count() - 1
            self.listWidget_lines.item(current_row).setFlags(self.listwidgetitemflags)
        if current_row != -1:
            self.listWidget_lines.setCurrentRow(current_row)
            self.on_listWidget_lines_itemClicked()

    # figures
    @Slot()
    def on_listWidget_figures_itemClicked(self):
        """redraw figure and update GUI"""
        self.fig = self.listWidget_figures.selectedItems()[-1].fig
        self.fig.canvas.draw()
        # start update GUI
        figurefacecolor = self.rgb_frac_to_name(self.fig.get_facecolor()[0:3])
        self.setcurrenttext(self.comboBox_figurefacecolor, figurefacecolor)
        if self.fig.patch.get_alpha() is None:
            self.doubleSpinBox_figurefacealpha.setValue(1.0)
        else:
            self.doubleSpinBox_figurefacealpha.setValue(self.fig.patch.get_alpha())
        self.lineEdit_figwidth.setText(str(self.fig.get_size_inches()[0]))
        self.lineEdit_figheight.setText(str(self.fig.get_size_inches()[1]))
        # end update GUI
        self.refresh_listWidget_axes()

    @Slot()
    def on_listWidget_figures_itemChanged(self):
        """update figure window name"""
        itemlist = [self.listWidget_figures.item(i) for i in xrange(self.listWidget_figures.count())]
        for item in itemlist:
            item.fig.canvas.set_window_title(item.text())

    @Slot()
    def on_pushButton_makefigure_clicked(self):
        """create new figure"""
        plt.figure()
        self.on_pushButton_refreshlist_clicked()

    @Slot()
    def on_pushButton_bringtofront_clicked(self):
        """bring selected figure to front"""
        self.fig.show()  # brings back closed window
        self.fig.canvas.manager.window.raise_()

    @Slot()
    def on_pushButton_closefigure_clicked(self):
        """close figure and remove from listWidget"""
        self.fig.canvas.manager.window.close()  # frees up memory
        self.on_pushButton_refreshlist_clicked()

    @Slot(str)
    def on_comboBox_figurefacecolor_currentIndexChanged(self, value):
        if value != '':
            self.fig.set_facecolor(value)
            self.fig.canvas.draw()

    @Slot(float)
    def on_doubleSpinBox_figurefacealpha_valueChanged(self, value):
        self.fig.patch.set_alpha(value)
        self.fig.canvas.draw()

    def lineEdit_figdims_editingFinished(self):
        #self.fig.canvas.manager.window.geometry().getCoords()[0]
        self.fig.set_size_inches(float(self.lineEdit_figwidth.text()), float(self.lineEdit_figheight.text()), forward=True)

    @Slot()
    def on_pushButton_tightlayout_clicked(self):
        self.fig.tight_layout()
        self.fig.canvas.draw()

    # axes
    @Slot()
    def on_listWidget_axes_itemClicked(self):
        self.ax = self.fig.axes[self.listWidget_axes.selectedIndexes()[-1].row()]
        # start update GUI axes tab
        if self.ax.xaxis.get_label_position() == 'bottom':
            self.checkBox_labeltop.setChecked(False)
        else:
            self.checkBox_labeltop.setChecked(True)
        if self.ax.yaxis.get_label_position() == 'left':
            self.checkBox_labelright.setChecked(False)
        else:
            self.checkBox_labelright.setChecked(True)
        self.lineEdit_xlabel.setText(self.ax.get_xlabel())
        self.lineEdit_ylabel.setText(self.ax.get_ylabel())
        axisfacecolor = self.rgb_frac_to_name(self.ax.patch.get_facecolor()[0:3])
        self.setcurrenttext(self.comboBox_axisfacecolor, axisfacecolor)
        if self.ax.patch.get_alpha() is None:
            self.doubleSpinBox_axisfacealpha.setValue(1.0)
        else:
            self.doubleSpinBox_axisfacealpha.setValue(self.ax.patch.get_alpha())
        self.setcurrenttext(self.comboBox_xscale, self.ax.get_xscale())
        self.setcurrenttext(self.comboBox_yscale, self.ax.get_yscale())
        self.lineEdit_xmin.setText(str(self.ax.get_xlim()[0]))
        self.lineEdit_xmax.setText(str(self.ax.get_xlim()[1]))
        self.lineEdit_ymin.setText(str(self.ax.get_ylim()[0]))
        self.lineEdit_ymax.setText(str(self.ax.get_ylim()[1]))
        self.lineEdit_xmin.setCursorPosition(0)
        self.lineEdit_xmax.setCursorPosition(0)
        self.lineEdit_ymin.setCursorPosition(0)
        self.lineEdit_ymax.setCursorPosition(0)
        self.checkBox_xgrid.setChecked(self.ax.xaxis.majorTicks[0].gridOn)
        self.checkBox_ygrid.setChecked(self.ax.yaxis.majorTicks[0].gridOn)
        # start update GUI spines/ticks tab
        for (labelon, tickon, widget) in ((self.ax.xaxis.majorTicks[0].label1On, self.ax.xaxis.majorTicks[0].tick1On, self.comboBox_ticksdrawbottom),
                                          (self.ax.xaxis.majorTicks[0].label2On, self.ax.xaxis.majorTicks[0].tick2On, self.comboBox_ticksdrawtop),
                                          (self.ax.yaxis.majorTicks[0].label1On, self.ax.yaxis.majorTicks[0].tick1On, self.comboBox_ticksdrawleft),
                                          (self.ax.yaxis.majorTicks[0].label2On, self.ax.yaxis.majorTicks[0].tick2On, self.comboBox_ticksdrawright)):
            if labelon:
                if tickon:
                    self.setcurrenttext(widget, 'both')
                else:
                    self.setcurrenttext(widget, 'tick labels only')
            else:
                if tickon:
                    self.setcurrenttext(widget, 'ticks only')
                else:
                    self.setcurrenttext(widget, 'none')
        if hasattr(self.ax.xaxis.get_major_locator(), 'numticks'):  # LogLocator and others
            self.spinBox_numxmajorticks.setValue(self.ax.xaxis.get_major_locator().numticks)
        elif hasattr(self.ax.xaxis.get_major_locator(), '_nbins'):  # MaxNLocator, AutoLocator
            self.spinBox_numxmajorticks.setValue(self.ax.xaxis.get_major_locator()._nbins)
        if hasattr(self.ax.yaxis.get_major_locator(), 'numticks'):
            self.spinBox_numymajorticks.setValue(self.ax.yaxis.get_major_locator().numticks)
        elif hasattr(self.ax.yaxis.get_major_locator(), '_nbins'):
            self.spinBox_numymajorticks.setValue(self.ax.yaxis.get_major_locator()._nbins)
        if isinstance(self.ax.xaxis.get_minor_locator(), mpl.ticker.LogLocator) and self.ax.xaxis.get_minor_locator()._subs is not None:
            self.spinBox_numxminorticks.setValue(len(self.ax.xaxis.get_minor_locator()._subs))  # LogLocator
        elif hasattr(self.ax.xaxis.get_major_locator(), 'ndivs'):  # AutoMinorLocator
            self.spinBox_numxminorticks.setValue(self.ax.xaxis.get_minor_locator().ndivs - 1)
        elif isinstance(self.ax.xaxis.get_minor_locator(), mpl.ticker.NullLocator):  # NullLocator
            self.spinBox_numxminorticks.setValue(0)
        if isinstance(self.ax.yaxis.get_minor_locator(), mpl.ticker.LogLocator) and self.ax.yaxis.get_minor_locator()._subs is not None:
            self.spinBox_numyminorticks.setValue(len(self.ax.yaxis.get_minor_locator()._subs))
        elif hasattr(self.ax.yaxis.get_major_locator(), 'ndivs'):
            self.spinBox_numyminorticks.setValue(self.ax.yaxis.get_minor_locator().ndivs - 1)
        elif isinstance(self.ax.yaxis.get_minor_locator(), mpl.ticker.NullLocator):
            self.spinBox_numyminorticks.setValue(0)
        self.checkBox_xminorlabels.setChecked(not isinstance(self.ax.xaxis.get_minor_formatter(), mpl.ticker.NullFormatter))
        self.checkBox_yminorlabels.setChecked(not isinstance(self.ax.yaxis.get_minor_formatter(), mpl.ticker.NullFormatter))
        self.setcurrenttext(self.comboBox_ticksdirection, self.ax.xaxis.majorTicks[0]._tickdir)
        self.doubleSpinBox_ticksmajorlength.setValue(self.ax.xaxis.majorTicks[0].tick1line.get_markersize())
        self.doubleSpinBox_ticksmajorwidth.setValue(self.ax.xaxis.majorTicks[0].tick1line.get_markeredgewidth())
        self.doubleSpinBox_ticksminorlength.setValue(self.ax.xaxis.minorTicks[0].tick1line.get_markersize())
        self.doubleSpinBox_ticksminorwidth.setValue(self.ax.xaxis.minorTicks[0].tick1line.get_markeredgewidth())
        for (spineloc, spinewidget) in (('bottom', self.comboBox_bottomspine),
                                        ('top', self.comboBox_topspine),
                                        ('left', self.comboBox_leftspine),
                                        ('right', self.comboBox_rightspine)):
            if not self.ax.spines[spineloc].get_visible():
                spinetext = 'off'
            elif isinstance(self.ax.spines[spineloc].get_position(), str):
                spinetext = self.ax.spines[spineloc].get_position()
            else:
                spinetext = self.ax.spines[spineloc].get_position()[0]
            self.setcurrenttext(spinewidget, spinetext)
        self.doubleSpinBox_spinewidth.setValue(self.ax.spines['bottom'].get_linewidth())
        # end update GUI
        self.refresh_listWidget_lines()

    @Slot()
    def on_listWidget_axes_itemChanged(self):
        for i in xrange(self.listWidget_axes.count()):
            self.fig.axes[i].set_title(self.listWidget_axes.item(i).text(), {'fontsize': self.fig.axes[i].title.get_size()})
            #self.fig.axes[i].set_title(self.listWidget_axes.item(i).text())  # resets title fontsize to default
        self.fig.canvas.draw()

    @Slot()
    def on_pushButton_makesubplot_clicked(self):
        if self.checkBox_sharex.isChecked() and len(self.listWidget_axes.selectedIndexes()) > 0:
            sharex = self.ax
        else:
            sharex = None
        if self.checkBox_sharey.isChecked() and len(self.listWidget_axes.selectedIndexes()) > 0:
            sharey = self.ax
        else:
            sharey = None
        self.fig.add_subplot(self.spinBox_subplotrows.value(), self.spinBox_subplotcolumns.value(),
                             self.spinBox_subplotindex.value(), sharex=sharex, sharey=sharey)
        self.refresh_listWidget_axes()

    @Slot()
    def on_pushButton_makeaxes_clicked(self):
        if self.checkBox_sharex.isChecked() and len(self.listWidget_axes.selectedIndexes()) > 0:
            sharex = self.ax
        else:
            sharex = None
        if self.checkBox_sharey.isChecked() and len(self.listWidget_axes.selectedIndexes()) > 0:
            sharey = self.ax
        else:
            sharey = None
        self.fig.add_axes([self.doubleSpinBox_axesleft.value(), self.doubleSpinBox_axesbottom.value(),
                           self.doubleSpinBox_axeswidth.value(), self.doubleSpinBox_axesheight.value()],
                          sharex=sharex, sharey=sharey)
        self.refresh_listWidget_axes()

    @Slot()
    def on_pushButton_twinx_clicked(self):
        plt.twinx(self.ax)
        self.refresh_listWidget_axes()

    @Slot()
    def on_pushButton_twiny_clicked(self):
        plt.twiny(self.ax)
        self.refresh_listWidget_axes()

    @Slot()
    def on_pushButton_deleteaxes_clicked(self):
        if self.ax in self.fig.axes:
            self.fig.delaxes(self.ax)
            self.listWidget_axes.takeItem(self.listWidget_axes.selectedIndexes()[-1].row())
            self.fig.canvas.draw()
            if self.listWidget_axes.count() > 0:
                self.on_listWidget_axes_itemClicked()

    @Slot(bool)
    def on_checkBox_labeltop_clicked(self, value):
        if value:
            self.ax.xaxis.set_label_position('top')
        else:
            self.ax.xaxis.set_label_position('bottom')
        self.fig.canvas.draw()

    @Slot(bool)
    def on_checkBox_labelright_clicked(self, value):
        if value:
            self.ax.yaxis.set_label_position('right')
        else:
            self.ax.yaxis.set_label_position('left')
        self.fig.canvas.draw()

    @Slot()
    def on_lineEdit_xlabel_editingFinished(self):
        self.ax.set_xlabel(self.lineEdit_xlabel.text())
        self.fig.canvas.draw()

    @Slot()
    def on_lineEdit_ylabel_editingFinished(self):
        self.ax.set_ylabel(self.lineEdit_ylabel.text())
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_axisfacecolor_currentIndexChanged(self, value):
        if value != '':
            self.ax.patch.set_facecolor(value)
            self.fig.canvas.draw()

    @Slot(float)
    def on_doubleSpinBox_axisfacealpha_valueChanged(self, value):
        self.ax.patch.set_alpha(value)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_xscale_currentIndexChanged(self, value):
        self.ax.set_xscale(value)
        self.fig.canvas.draw()
        self.on_listWidget_axes_itemClicked()

    @Slot(str)
    def on_comboBox_yscale_currentIndexChanged(self, value):
        self.ax.set_yscale(value)
        self.fig.canvas.draw()
        self.on_listWidget_axes_itemClicked()

    def lineEdit_limits_editingFinished(self):
        self.ax.axis([float(self.lineEdit_xmin.text()), float(self.lineEdit_xmax.text()),
                      float(self.lineEdit_ymin.text()), float(self.lineEdit_ymax.text())])
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_autoscale_currentIndexChanged(self, value):
        self.ax.axis(value)  # get setting using axes.py line 1315, not implemented yet
        self.fig.canvas.draw()
        self.on_listWidget_axes_itemClicked()

    @Slot(bool)
    def on_checkBox_xgrid_clicked(self, value):
        self.ax.xaxis.grid(value)
        self.fig.canvas.draw()

    @Slot(bool)
    def on_checkBox_ygrid_clicked(self, value):
        self.ax.yaxis.grid(value)
        self.fig.canvas.draw()

    # ticks
    @Slot(str)
    def on_comboBox_ticksdrawbottom_currentIndexChanged(self, value):
        if value == 'ticks only':
            self.ax.tick_params(which='both', bottom=True, labelbottom=False)
        elif value == 'tick labels only':
            self.ax.tick_params(which='both', bottom=False, labelbottom=True)
        elif value == 'both':
            self.ax.tick_params(which='both', bottom=True, labelbottom=True)
        else:
            self.ax.tick_params(which='both', bottom=False, labelbottom=False)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_ticksdrawtop_currentIndexChanged(self, value):
        if value == 'ticks only':
            self.ax.tick_params(which='both', top=True, labeltop=False)
        elif value == 'tick labels only':
            self.ax.tick_params(which='both', top=False, labeltop=True)
        elif value == 'both':
            self.ax.tick_params(which='both', top=True, labeltop=True)
        else:
            self.ax.tick_params(which='both', top=False, labeltop=False)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_ticksdrawleft_currentIndexChanged(self, value):
        if value == 'ticks only':
            self.ax.tick_params(which='both', left=True, labelleft=False)
        elif value == 'tick labels only':
            self.ax.tick_params(which='both', left=False, labelleft=True)
        elif value == 'both':
            self.ax.tick_params(which='both', left=True, labelleft=True)
        else:
            self.ax.tick_params(which='both', left=False, labelleft=False)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_ticksdrawright_currentIndexChanged(self, value):
        if value == 'ticks only':
            self.ax.tick_params(which='both', right=True, labelright=False)
        elif value == 'tick labels only':
            self.ax.tick_params(which='both', right=False, labelright=True)
        elif value == 'both':
            self.ax.tick_params(which='both', right=True, labelright=True)
        else:
            self.ax.tick_params(which='both', right=False, labelright=False)
        self.fig.canvas.draw()

    @Slot(int)
    def on_spinBox_numxmajorticks_valueChanged(self, value):
        if hasattr(self.ax.xaxis.get_major_locator(), 'numticks'):
            self.ax.xaxis.get_major_locator().numticks = value
        elif hasattr(self.ax.xaxis.get_major_locator(), '_nbins'):
            self.ax.xaxis.get_major_locator()._nbins = value
        self.fig.canvas.draw()

    @Slot(int)
    def on_spinBox_numymajorticks_valueChanged(self, value):
        if hasattr(self.ax.yaxis.get_major_locator(), 'numticks'):
            self.ax.yaxis.get_major_locator().numticks = value
        elif hasattr(self.ax.yaxis.get_major_locator(), '_nbins'):
            self.ax.yaxis.get_major_locator()._nbins = value
        self.fig.canvas.draw()

    @Slot(int)
    def on_spinBox_numxminorticks_valueChanged(self, value):
        if isinstance(self.ax.xaxis.get_minor_locator(), mpl.ticker.LogLocator):
            if value >= 8:
                subs = range(2, 10)
            else:
                # evenly distributed minor ticks for LogLocator
                subs = np.floor(1 + np.arange(1, value + 1) * 9 / (value + 1))
            self.ax.xaxis.set_minor_locator(mpl.ticker.LogLocator(numticks=99, subs=subs))
        else:
            self.ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(value + 1))
        self.fig.canvas.draw()

    @Slot(int)
    def on_spinBox_numyminorticks_valueChanged(self, value):
        if isinstance(self.ax.yaxis.get_minor_locator(), mpl.ticker.LogLocator):
            if value >= 8:
                subs = range(2, 10)
            else:
                subs = np.floor(1 + np.arange(1, value + 1) * 9 / (value + 1))
            self.ax.yaxis.set_minor_locator(mpl.ticker.LogLocator(numticks=99, subs=subs))
        else:
            self.ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(value + 1))
        self.fig.canvas.draw()

    @Slot(bool)
    def on_checkBox_xminorlabels_clicked(self, value):
        if value:
            if self.ax.get_xscale() == 'linear':
                self.ax.xaxis.set_minor_formatter(mpl.ticker.ScalarFormatter())
            else:
                self.ax.xaxis.set_minor_formatter(mpl.ticker.FuncFormatter(myminortickformatter))
        else:
            self.ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())
        self.fig.canvas.draw()

    @Slot(bool)
    def on_checkBox_yminorlabels_clicked(self, value):
        if value:
            if self.ax.get_yscale() == 'linear':
                self.ax.yaxis.set_minor_formatter(mpl.ticker.ScalarFormatter())
            else:
                self.ax.yaxis.set_minor_formatter(mpl.ticker.FuncFormatter(myminortickformatter))
        else:
            self.ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_ticksdirection_currentIndexChanged(self, value):
        self.ax.tick_params(which='both', direction=value)
        self.fig.canvas.draw()

    @Slot(float)
    def on_doubleSpinBox_ticksmajorlength_valueChanged(self, value):
        self.ax.tick_params(which='major', length=value)
        if self.checkBox_applytorcparams.isChecked():
            plt.rcParams['xtick.major.size'] = value
            plt.rcParams['ytick.major.size'] = value
        self.fig.canvas.draw()

    @Slot(float)
    def on_doubleSpinBox_ticksmajorwidth_valueChanged(self, value):
        self.ax.tick_params(which='major', width=value)
        if self.checkBox_applytorcparams.isChecked():
            plt.rcParams['xtick.major.width'] = value
            plt.rcParams['ytick.major.width'] = value
        self.fig.canvas.draw()

    @Slot(float)
    def on_doubleSpinBox_ticksminorlength_valueChanged(self, value):
        self.ax.tick_params(which='minor', length=value)
        if self.checkBox_applytorcparams.isChecked():
            plt.rcParams['xtick.minor.size'] = value
            plt.rcParams['ytick.minor.size'] = value
        self.fig.canvas.draw()

    @Slot(float)
    def on_doubleSpinBox_ticksminorwidth_valueChanged(self, value):
        self.ax.tick_params(which='minor', width=value)
        if self.checkBox_applytorcparams.isChecked():
            plt.rcParams['xtick.minor.width'] = value
            plt.rcParams['ytick.minor.width'] = value
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_bottomspine_currentIndexChanged(self, value):
        self.ax.spines['bottom'].set_visible(True)
        if value == 'center' or value == 'zero':
            self.ax.spines['bottom'].set_position(value)
        elif value == 'outward':
            self.ax.spines['bottom'].set_position(('outward', 0))
        else:
            self.ax.spines['bottom'].set_visible(False)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_topspine_currentIndexChanged(self, value):
        self.ax.spines['top'].set_visible(True)
        if value == 'center' or value == 'zero':
            self.ax.spines['top'].set_position(value)
        elif value == 'outward':
            self.ax.spines['top'].set_position(('outward', 0))
        else:
            self.ax.spines['top'].set_visible(False)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_leftspine_currentIndexChanged(self, value):
        self.ax.spines['left'].set_visible(True)
        if value == 'center' or value == 'zero':
            self.ax.spines['left'].set_position(value)
        elif value == 'outward':
            self.ax.spines['left'].set_position(('outward', 0))
        else:
            self.ax.spines['left'].set_visible(False)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_rightspine_currentIndexChanged(self, value):
        self.ax.spines['right'].set_visible(True)
        if value == 'center' or value == 'zero':
            self.ax.spines['right'].set_position(value)
        elif value == 'outward':
            self.ax.spines['right'].set_position(('outward', 0))
        else:
            self.ax.spines['right'].set_visible(False)
        self.fig.canvas.draw()

    @Slot(float)
    def on_doubleSpinBox_spinewidth_valueChanged(self, value):
        for spine in self.ax.spines.values():
            spine.set_linewidth(value)
        self.fig.canvas.draw()

    # legend
    @Slot()
    def on_pushButton_legendapply_clicked(self):
        if self.checkBox_legendon.isChecked():
            self.ax.legend(frameon=self.checkBox_legendframe.isChecked(), fancybox=self.checkBox_legendfancybox.isChecked(),
                           shadow=self.checkBox_legendshadow.isChecked(), framealpha=self.doubleSpinBox_legendalpha.value(),
                           ncol=self.spinBox_legendcolumns.value(), title=self.lineEdit_legendtitle.text(),
                           loc='best')
            if self.ax.legend_ is not None:
                self.ax.legend_.draggable(True)
                self.ax.legend_.get_frame().set_facecolor(self.comboBox_legendfacecolor.currentText())
        elif self.ax.legend_ is not None:
            self.ax.legend_.set_visible(False)
        self.fig.canvas.draw()

    # lines
    @Slot()
    def on_listWidget_lines_itemClicked(self):
        self.line = self.ax.lines[self.listWidget_lines.selectedIndexes()[-1].row()]
        index = [item[0] for item in self.linestyles].index(self.line.get_linestyle())
        self.comboBox_linestyle.setCurrentIndex(index)
        self.doubleSpinBox_linewidth.setValue(self.line.get_linewidth())
        linecolor = self.rgb_frac_to_name(self.line.get_color())
        self.setcurrenttext(self.comboBox_linecolor, linecolor)
        index = [item[0] for item in self.markers].index(self.line.get_marker())
        self.comboBox_markerstyle.setCurrentIndex(index)
        self.spinBox_markersize.setValue(self.line.get_markersize())
        markercolor = self.rgb_frac_to_name(self.line.get_markerfacecolor())
        self.setcurrenttext(self.comboBox_markercolor, markercolor)
        self.on_pushButton_legendapply_clicked()

    @Slot()
    def on_listWidget_lines_itemChanged(self):
        for i in xrange(self.listWidget_lines.count()):
            self.ax.lines[i].set_label(self.listWidget_lines.item(i).text())
        self.fig.canvas.draw()

    @Slot()
    def on_pushButton_makeline_clicked(self):
        x = eval(self.lineEdit_x.text())
        self.ax.plot(eval(self.lineEdit_x.text()), eval(self.lineEdit_y.text()))
        self.fig.canvas.draw()
        self.on_listWidget_axes_itemClicked()

    @Slot()
    def on_pushButton_deleteline_clicked(self):
        if self.line in self.ax.lines:
            self.line.remove()
            self.refresh_listWidget_lines()

    @Slot(int)
    def on_comboBox_linestyle_currentIndexChanged(self, value):
        try:
            self.line.set_linestyle(self.linestyles[value][0])
            self.fig.canvas.draw()
        except AttributeError:
            pass

    @Slot(float)
    def on_doubleSpinBox_linewidth_valueChanged(self, value):
        self.line.set_linewidth(value)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_linecolor_currentIndexChanged(self, value):
        self.line.set_color(value)
        self.fig.canvas.draw()

    @Slot(int)
    def on_comboBox_markerstyle_currentIndexChanged(self, value):
        try:
            self.line.set_marker(self.markers[value][0])
            self.fig.canvas.draw()
        except AttributeError:
            pass

    @Slot(int)
    def on_spinBox_markersize_valueChanged(self, value):
        self.line.set_markersize(value)
        self.fig.canvas.draw()

    @Slot(str)
    def on_comboBox_markercolor_currentIndexChanged(self, value):
        self.line.set_markerfacecolor(value)
        self.line.set_markeredgecolor(value)
        self.fig.canvas.draw()

    @Slot()
    def on_pushButton_hline_clicked(self):
        self.ax.axhline()
        self.fig.canvas.draw()
        self.refresh_listWidget_lines()

    @Slot()
    def on_pushButton_vline_clicked(self):
        self.ax.axvline()
        self.fig.canvas.draw()
        self.refresh_listWidget_lines()

    # fonts
    @Slot()
    def on_pushButton_selectfont_clicked(self):
        self.selectedfont, ok = self.fontdialog.getFont(self.selectedfont)

    @Slot()
    def on_pushButton_fontapply_clicked(self):  # ignores strikeout and underline options
        items = []
        if self.checkBox_fontapplytotitle.isChecked():
            items.append(self.ax.title)
        if self.checkBox_fontapplytoxlabel.isChecked():
            items.append(self.ax.xaxis.label)
        if self.checkBox_fontapplytoylabel.isChecked():
            items.append(self.ax.yaxis.label)
        if self.checkBox_fontapplytoxmajorticklabels.isChecked():
            items += self.ax.get_xmajorticklabels()
        if self.checkBox_fontapplytoymajorticklabels.isChecked():
            items += self.ax.get_ymajorticklabels()
        if self.checkBox_fontapplytoxminorticklabels.isChecked():
            items += self.ax.get_xminorticklabels()
        if self.checkBox_fontapplytoyminorticklabels.isChecked():
            items += self.ax.get_yminorticklabels()
        if self.checkBox_fontapplytolegend.isChecked():
            items += self.ax.legend_.get_texts()
        for item in items:
            item.set_name(self.selectedfont.family())
            item.set_size(self.selectedfont.pointSize())
            item.set_color(self.comboBox_fontcolor.currentText())
            if self.selectedfont.bold():
                item.set_weight('bold')
            else:
                item.set_weight('normal')
            if self.selectedfont.italic():
                item.set_style('italic')
            else:
                item.set_style('normal')
        self.fig.canvas.draw()


def myminortickformatter(number, pos):
    numstr = str(format(number, 'e'))
    if numstr[0] == '-':
        return str(numstr)[1]
    else:
        return str(numstr)[0]


def rpx(string):
    string = string.replace('self', repl_string)
    print(string)
    exec(string)

if __name__ == '__main__':
    #app = QtGui.QApplication.instance()  # checks if QApplication already exists
    #if not app:  # create QApplication if it doesnt exist
    #    app = QtGui.QApplication(sys.argv)
    repl_string = 'browser'
    app = guisupport.get_app_qt4()
    browser = PlotBrowser()
    browser.show()
    guisupport.start_event_loop_qt4(app)  # doesn't block terminal when run in ipython
    #app.exec_()
