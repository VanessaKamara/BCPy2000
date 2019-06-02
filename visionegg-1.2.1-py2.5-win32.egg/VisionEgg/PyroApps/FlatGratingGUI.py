#!/usr/bin/env python
#
# The Vision Egg: FlatGratingGUI
#
# Copyright (C) 2001-2003 Andrew Straw.
# Author: Andrew Straw <astraw@users.sourceforge.net>
# URL: <http://www.visionegg.org/>
#
# Distributed under the terms of the GNU Lesser General Public License
# (LGPL). See LICENSE.TXT that came with this file.

"""Handle sinusoidal gratings (client-side)"""

import VisionEgg, string

import sys, os
import Tkinter
import VisionEgg.PyroApps.EPhysGUIUtils as client_utils

def get_control_list():
    return [("flat_grating_server",FlatGratingControlFrame,FlatGratingControlFrame.title)]

class FlatGratingMetaParameters:
    def __init__(self):
        self.contrast = 1.0
        self.orient = 0.0
        self.sf = 0.01 # cycles per pixel
        self.tf = 1.0
        self.size_x = 200.0
        self.size_y = 200.0
        self.center_x = 320.0
        self.center_y = 240.0
        self.pre_stim_sec = 1.0
        self.stim_sec = 2.0
        self.post_stim_sec = 1.0

class FlatGratingControlFrame(client_utils.StimulusControlFrame):
    title = "Grating (2D) Experiment"
    def __init__(self, master=None, suppress_go_buttons=0,**kw):
        client_utils.StimulusControlFrame.__init__(self,
                                                   master,
                                                   suppress_go_buttons,
                                                   FlatGratingControlFrame.title,
                                                   FlatGratingMetaParameters,
                                                   **kw)

        param_frame = self.param_frame # shorthand for self.param_frame created in base class

        # Allow columns to expand
        param_frame.columnconfigure(0,weight=1)
        param_frame.columnconfigure(1,weight=1)

        pf_row = 0
        Tkinter.Label(param_frame,text="Contrast:").grid(row=pf_row,column=0)
        self.contrast_tk_var = Tkinter.DoubleVar()
        self.contrast_tk_var.set(self.meta_params.contrast)
        self.make_callback_entry(textvariable=self.contrast_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Contrast"] = ("contrast",self.contrast_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Orientation (deg):").grid(row=pf_row,column=0)
        self.orient_tk_var = Tkinter.DoubleVar()
        self.orient_tk_var.set(self.meta_params.orient)
        self.make_callback_entry(textvariable=self.orient_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Orientation"] = ("orient",self.orient_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Spatial frequency (Cpp):").grid(row=pf_row,column=0)
        self.sf_tk_var = Tkinter.DoubleVar()
        self.sf_tk_var.set(self.meta_params.sf)
        self.make_callback_entry(textvariable=self.sf_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Spatial frequency"] = ("sf",self.sf_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Temporal frequency (Hz):").grid(row=pf_row,column=0)
        self.tf_tk_var = Tkinter.DoubleVar()
        self.tf_tk_var.set(self.meta_params.tf)
        self.make_callback_entry(textvariable=self.tf_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Temporal frequency"] = ("tf",self.tf_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Size X (pixels):").grid(row=pf_row,column=0)
        self.size_x_tk_var = Tkinter.DoubleVar()
        self.size_x_tk_var.set(self.meta_params.size_x)
        self.make_callback_entry(textvariable=self.size_x_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Size X"] = ("size_x",self.size_x_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Size Y (pixels):").grid(row=pf_row,column=0)
        self.size_y_tk_var = Tkinter.DoubleVar()
        self.size_y_tk_var.set(self.meta_params.size_y)
        self.make_callback_entry(textvariable=self.size_y_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Size Y"] = ("size_y",self.size_y_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Center X (pixels):").grid(row=pf_row,column=0)
        self.center_x_tk_var = Tkinter.DoubleVar()
        self.center_x_tk_var.set(self.meta_params.center_x)
        self.make_callback_entry(textvariable=self.center_x_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Center X"] = ("center_x",self.center_x_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Center Y (pixels):").grid(row=pf_row,column=0)
        self.center_y_tk_var = Tkinter.DoubleVar()
        self.center_y_tk_var.set(self.meta_params.center_y)
        self.make_callback_entry(textvariable=self.center_y_tk_var).grid(row=pf_row,column=1)
        self.loopable_variables["Center Y"] = ("center_y",self.center_y_tk_var)

        pf_row += 1
        Tkinter.Label(param_frame,text="Pre stimulus duration (sec):").grid(row=pf_row,column=0)
        self.prestim_dur_tk_var = Tkinter.DoubleVar()
        self.prestim_dur_tk_var.set(self.meta_params.pre_stim_sec)
        self.make_callback_entry(textvariable=self.prestim_dur_tk_var).grid(row=pf_row,column=1)

        pf_row += 1
        Tkinter.Label(param_frame,text="Stimulus duration (sec):").grid(row=pf_row,column=0)
        self.stim_dur_tk_var = Tkinter.DoubleVar()
        self.stim_dur_tk_var.set(self.meta_params.stim_sec)
        self.make_callback_entry(textvariable=self.stim_dur_tk_var).grid(row=pf_row,column=1)

        pf_row += 1
        Tkinter.Label(param_frame,text="Post stimulus duration (sec):").grid(row=pf_row,column=0)
        self.poststim_dur_tk_var = Tkinter.DoubleVar()
        self.poststim_dur_tk_var.set(self.meta_params.post_stim_sec)
        self.make_callback_entry(textvariable=self.poststim_dur_tk_var).grid(row=pf_row,column=1)

    def get_shortname(self):
        return "flat_grating"

    def update_tk_vars(self):
        self.contrast_tk_var.set( self.meta_params.contrast )
        self.orient_tk_var.set( self.meta_params.orient )
        self.sf_tk_var.set( self.meta_params.sf )
        self.tf_tk_var.set( self.meta_params.tf )
        self.size_x_tk_var.set( self.meta_params.size_x )
        self.size_y_tk_var.set( self.meta_params.size_y )
        self.center_x_tk_var.set( self.meta_params.center_x )
        self.center_y_tk_var.set( self.meta_params.center_y )
        self.prestim_dur_tk_var.set( self.meta_params.pre_stim_sec )
        self.stim_dur_tk_var.set( self.meta_params.stim_sec )
        self.poststim_dur_tk_var.set( self.meta_params.post_stim_sec )

    def send_values(self,dummy_arg=None):
        self.meta_params.contrast = self.contrast_tk_var.get()
        self.meta_params.orient = self.orient_tk_var.get()
        self.meta_params.sf = self.sf_tk_var.get()
        self.meta_params.tf = self.tf_tk_var.get()
        self.meta_params.size_x = self.size_x_tk_var.get()
        self.meta_params.size_y = self.size_y_tk_var.get()
        self.meta_params.center_x = self.center_x_tk_var.get()
        self.meta_params.center_y = self.center_y_tk_var.get()
        self.meta_params.pre_stim_sec = self.prestim_dur_tk_var.get()
        self.meta_params.stim_sec = self.stim_dur_tk_var.get()
        self.meta_params.post_stim_sec = self.poststim_dur_tk_var.get()
        if self.connected:
            self.meta_controller.set_parameters( self.meta_params )

    def get_duration_sec(self):
        self.meta_params.pre_stim_sec = self.prestim_dur_tk_var.get()
        self.meta_params.stim_sec = self.stim_dur_tk_var.get()
        self.meta_params.post_stim_sec = self.poststim_dur_tk_var.get()
        return self.meta_params.pre_stim_sec + self.meta_params.stim_sec + self.meta_params.post_stim_sec

if __name__=='__main__':
    frame = FlatGratingControlFrame()
    frame.pack(expand=1,fill=Tkinter.BOTH)
    frame.winfo_toplevel().title("%s"%(os.path.basename(os.path.splitext(sys.argv[0])[0]),))
    frame.mainloop()
