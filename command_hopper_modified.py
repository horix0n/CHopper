#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Hop on Demand
# Author: Bill Urrego
# Generated: Thu Mar 31 02:23:46 2016
# Modified: Sat April 2 22:20:00 2016
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import uhd
from gnuradio import wxgui
from gnuradio import zeromq
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import numpy
import time
import wx

### Added by Bill Urrego
from threading import Thread
import zmq
import struct

def sub(change_freq):
	context = zmq.Context()
	subscriber = context.socket(zmq.SUB)
	subscriber.connect("tcp://127.0.0.1:5558")
	subscriber.setsockopt(zmq.SUBSCRIBE,"")
	msg = zmq.Message
	while (True):
		msg = subscriber.recv()
		freqID = int(struct.unpack('<I',msg)[0])
		print "\n" , "[Control Subscriber] Received request to change to frequency ID:", freqID
		change_freq(freqID)
			
### End modifications ###

class command_hopper(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Hop on Demand")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.tx_samp_rate = tx_samp_rate = 50e3
        self.tx_freq = tx_freq = 100e6
        self.sps = sps = 4
        self.rx_samp_rate = rx_samp_rate = 2e6
        self.rx_freq = rx_freq = 100e6
        self.qpsk = qpsk = digital.constellation_rect(([0.707+0.707j, -0.707+0.707j, -0.707-0.707j, 0.707-0.707j]), ([0, 1, 2, 3]), 4, 2, 2, 1, 1).base()
        self.excess_bw = excess_bw = 0.35

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_source_0 = zeromq.sub_source(gr.sizeof_gr_complex, 1, "tcp://127.0.0.1:5557", 1000, False, -1)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.GetWin(),
        	baseband_freq=rx_freq,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=rx_samp_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=True,
        	avg_alpha=None,
        	title="FFT Plot",
        	peak_hold=True,
        )
        self.Add(self.wxgui_fftsink2_0.win)
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(rx_samp_rate)
        self.uhd_usrp_source_0.set_center_freq(rx_freq, 0)
        self.uhd_usrp_source_0.set_gain(15, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0.set_samp_rate(tx_samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(tx_freq, 0)
        self.uhd_usrp_sink_0.set_gain(30, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.low_pass_filter_0 = filter.fir_filter_ccf(1, firdes.low_pass(
        	1, rx_samp_rate, 1e6, 30e3, firdes.WIN_HAMMING, 6.76))
        self.digital_constellation_modulator_0 = digital.generic_mod(
          constellation=qpsk,
          differential=True,
          samples_per_symbol=sps,
          pre_diff_code=True,
          excess_bw=excess_bw,
          verbose=False,
          log=False,
          )
        self.blocks_probe_signal_x_0 = blocks.probe_signal_c()
        self.analog_random_source_x_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, 256, 1000)), True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0, 0), (self.digital_constellation_modulator_0, 0))    
        self.connect((self.digital_constellation_modulator_0, 0), (self.uhd_usrp_sink_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.wxgui_fftsink2_0, 0))    
        self.connect((self.uhd_usrp_source_0, 0), (self.low_pass_filter_0, 0))    
        self.connect((self.zeromq_sub_source_0, 0), (self.blocks_probe_signal_x_0, 0))

	### Added by Bill Urrego ###
    	t = Thread(target=sub, args=(self.change_freq,))
    	t.start()
   	### End modifications ###    

    def get_tx_samp_rate(self):
        return self.tx_samp_rate

    def set_tx_samp_rate(self, tx_samp_rate):
        self.tx_samp_rate = tx_samp_rate
        self.uhd_usrp_sink_0.set_samp_rate(self.tx_samp_rate)

    def get_tx_freq(self):
        return self.tx_freq

    def set_tx_freq(self, tx_freq):
        self.tx_freq = tx_freq
        self.uhd_usrp_sink_0.set_center_freq(self.tx_freq, 0)

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps

    def get_rx_samp_rate(self):
        return self.rx_samp_rate

    def set_rx_samp_rate(self, rx_samp_rate):
        self.rx_samp_rate = rx_samp_rate
        self.wxgui_fftsink2_0.set_sample_rate(self.rx_samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.rx_samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.rx_samp_rate, 200e3, 30e3, firdes.WIN_HAMMING, 6.76))

    def get_rx_freq(self):
        return self.rx_freq

    def set_rx_freq(self, rx_freq):
        self.rx_freq = rx_freq
        self.wxgui_fftsink2_0.set_baseband_freq(self.rx_freq)
        self.uhd_usrp_source_0.set_center_freq(self.rx_freq, 0)

    def get_qpsk(self):
        return self.qpsk

    def set_qpsk(self, qpsk):
        self.qpsk = qpsk

    def get_excess_bw(self):
        return self.excess_bw

    def set_excess_bw(self, excess_bw):
        self.excess_bw = excess_bw

    #### Added by Bill Urrego ###
    def change_freq(self, freqID):
	if freqID == 1:	
		self.tx_freq = 100.4e6
	elif freqID == 2:
		self.tx_freq = 99.4e6
	else:
		self.tx_freq = 100e6

	self.uhd_usrp_sink_0.set_center_freq(self.tx_freq, 0)

    ### End modifications ###

def main(top_block_cls=command_hopper, options=None):
    
    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()

if __name__ == '__main__':
    main()
