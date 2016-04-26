#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: DVB-T Signal Detector using RTL-SDR
# Author: Andri Rahmadhani
# Description: Detect DVB-T signal for cognitive radio application
# Generated: Mon Apr 25 21:42:16 2016
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import numbersink2
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import osmosdr
import threading
import time
import wx

class signal_detector(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="DVB-T Signal Detector using RTL-SDR")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = -70
        self.samp_rate = samp_rate = 2048000
        self.probe_level = probe_level = 0
        self.probe_detection = probe_detection = 0
        self.freq = freq = 525200000
        self.fft_size = fft_size = 1024

        ##################################################
        # Blocks
        ##################################################
        _threshold_sizer = wx.BoxSizer(wx.VERTICAL)
        self._threshold_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_threshold_sizer,
        	value=self.threshold,
        	callback=self.set_threshold,
        	label="Threshold",
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._threshold_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_threshold_sizer,
        	value=self.threshold,
        	callback=self.set_threshold,
        	minimum=-100,
        	maximum=0,
        	num_steps=100,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_threshold_sizer)
        self.probe_signal_level = blocks.probe_signal_f()
        self.probe_signal_detection = blocks.probe_signal_f()
        self.notebook = self.notebook = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
        self.notebook.AddPage(grc_wxgui.Panel(self.notebook), "Waterfall")
        self.notebook.AddPage(grc_wxgui.Panel(self.notebook), "Spectrum")
        self.notebook.AddPage(grc_wxgui.Panel(self.notebook), "Output")
        self.Add(self.notebook)
        _freq_sizer = wx.BoxSizer(wx.VERTICAL)
        self._freq_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_freq_sizer,
        	value=self.freq,
        	callback=self.set_freq,
        	label="freq",
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._freq_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_freq_sizer,
        	value=self.freq,
        	callback=self.set_freq,
        	minimum=478000000,
        	maximum=862000000,
        	num_steps=1000,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_freq_sizer)
        self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
        	self.notebook.GetPage(0).GetWin(),
        	baseband_freq=freq,
        	dynamic_range=100,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=samp_rate,
        	fft_size=fft_size,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="Waterfall Plot",
        	win=window.rectangular,
        )
        self.notebook.GetPage(0).Add(self.wxgui_waterfallsink2_0.win)
        self.wxgui_numbersink2_1 = numbersink2.number_sink_f(
        	self.notebook.GetPage(2).GetWin(),
        	unit="dB",
        	minval=-120,
        	maxval=0,
        	factor=1,
        	decimal_places=0,
        	ref_level=0,
        	sample_rate=samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=0.03,
        	label="Level",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.notebook.GetPage(2).Add(self.wxgui_numbersink2_1.win)
        self.wxgui_numbersink2_0 = numbersink2.number_sink_f(
        	self.notebook.GetPage(2).GetWin(),
        	unit="signal present",
        	minval=0,
        	maxval=1,
        	factor=1.0,
        	decimal_places=0,
        	ref_level=0,
        	sample_rate=samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=None,
        	label="Signal Detector",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.notebook.GetPage(2).Add(self.wxgui_numbersink2_0.win)
        self.wxgui_fftsink2_1 = fftsink2.fft_sink_c(
        	self.notebook.GetPage(1).GetWin(),
        	baseband_freq=freq,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=samp_rate,
        	fft_size=fft_size,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="Spectrum",
        	peak_hold=False,
        	win=window.rectangular,
        )
        self.notebook.GetPage(1).Add(self.wxgui_fftsink2_1.win)
        self.rtlsdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(freq, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(20, 0)
        self.rtlsdr_source_0.set_if_gain(10, 0)
        self.rtlsdr_source_0.set_bb_gain(5, 0)
        self.rtlsdr_source_0.set_antenna("", 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
          
        def _probe_level_probe():
        	while True:
        		val = self.probe_signal_level.level()
        		try: self.set_probe_level(val)
        		except AttributeError, e: pass
        		time.sleep(1.0/(10))
        _probe_level_thread = threading.Thread(target=_probe_level_probe)
        _probe_level_thread.daemon = True
        _probe_level_thread.start()
        def _probe_detection_probe():
        	while True:
        		val = self.probe_signal_detection.level()
        		try: self.set_probe_detection(val)
        		except AttributeError, e: pass
        		time.sleep(1.0/(10))
        _probe_detection_thread = threading.Thread(target=_probe_detection_probe)
        _probe_detection_thread.daemon = True
        _probe_detection_thread.start()
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, (window.rectangular(fft_size)), True, 1)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, fft_size)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(threshold, threshold, threshold)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(fft_size, 1.0/fft_size, 4000)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_size)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, fft_size*fft_size)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.wxgui_numbersink2_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.wxgui_fftsink2_1, 0))
        self.connect((self.blocks_throttle_0, 0), (self.wxgui_waterfallsink2_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.wxgui_numbersink2_1, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.probe_signal_level, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.probe_signal_detection, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_vector_to_stream_0, 0))


# QT sink close method reimplementation

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.blocks_threshold_ff_0.set_hi(self.threshold)
        self.blocks_threshold_ff_0.set_lo(self.threshold)
        self._threshold_slider.set_value(self.threshold)
        self._threshold_text_box.set_value(self.threshold)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)
        self.wxgui_waterfallsink2_0.set_sample_rate(self.samp_rate)
        self.wxgui_fftsink2_1.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_probe_level(self):
        return self.probe_level

    def set_probe_level(self, probe_level):
        self.probe_level = probe_level

    def get_probe_detection(self):
        return self.probe_detection

    def set_probe_detection(self, probe_detection):
        self.probe_detection = probe_detection

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.rtlsdr_source_0.set_center_freq(self.freq, 0)
        self.wxgui_waterfallsink2_0.set_baseband_freq(self.freq)
        self.wxgui_fftsink2_1.set_baseband_freq(self.freq)
        self._freq_slider.set_value(self.freq)
        self._freq_text_box.set_value(self.freq)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.analog_const_source_x_0.set_offset(self.fft_size*self.fft_size)
        self.blocks_moving_average_xx_0.set_length_and_scale(self.fft_size, 1.0/self.fft_size)

if __name__ == '__main__':
    import ctypes
    import os
    if os.name == 'posix':
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = signal_detector()
    tb.Start(True)
    tb.Wait()

