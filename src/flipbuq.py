#!/usr/bin/env python
# -*- Mode: Python; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- #!/usr/bin/python
#
# main.py
# Copyright (C) 2013 Noe Nieto <nnieto@noenieto.com>
#
# flipbuq is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# flipbuq is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
import os, sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, Gst, GObject
# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo

#Comment the first line and uncomment the second before installing
#or making the tarball (alternatively, use project variables)
UI_FILE = "src/flipbuq.ui"
#UI_FILE = "/usr/local/share/flipbuq/ui/flipbuq.ui"


class FlipBuqUI(object):
    _controls = ('BtnPlay', 'BtnStop', 'BtnRecord', 'BtnTime', 'ComboFPS', 'BtnSettings')

    def __init__(self):
        self._buildPipeline()
        self._buildUI()

    def _buildUI(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)
        self.mainWindow = self.builder.get_object('MainWindow')
        self._disableButtons(excepting=['BtnRecord', 'BtnTime', 'ComboFPS', 'BtnSettings'])
        self.videoWindow = self.builder.get_object('VideoWindow')
        self.videoWindow.set_double_buffered(False)
        self.mainWindow.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the onBusSync() handler because threading issues will cause
        # segfaults there.
        self.xid = self.videoWindow.get_property('window').get_xid()

    def _buildPipeline(self):
        #Create the pipeline
        self.pipeline = Gst.Pipeline(name='WebCamPipeline')
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message::eos", self.onShutdown)
        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.onBusSync)

        videoSource = Gst.ElementFactory.make('autovideosrc', name='source')
        self.pipeline.add(videoSource)
        tee = Gst.ElementFactory.make('tee', name='t')
        self.pipeline.add(tee)

        videoQueue = Gst.ElementFactory.make('queue', name='videoQueue')
        self.pipeline.add(videoQueue)
        self.videoSink = videoSink = Gst.ElementFactory.make('xvimagesink', name='videoSink')
        self.pipeline.add(videoSink)

        pngQueue = Gst.ElementFactory.make('queue', name='fipper')
        self.pipeline.add(pngQueue)
        colorSpaceFlt = Gst.ElementFactory.make('videoconvert', 'colorSpaceFlt')
        self.pipeline.add(colorSpaceFlt)
        pngEncoder = Gst.ElementFactory.make('pngenc', name='pngEncoder')
        self.pipeline.add(pngEncoder)
        multiFileSink = Gst.ElementFactory.make('multifilesink', name='multiFileSink')
        self.pipeline.add(multiFileSink)

        #Configure elements
        #
        videoSink.set_property('force-aspect-ratio', True)
        pngEncoder.set_property('snapshot', False)
        multiFileSink.set_property('location', 'frame%d.png')

        #Wire up pipeline
        #Png conversion part
        videoSource.link(tee)
        videoQueue.link(colorSpaceFlt)
        colorSpaceFlt.link(pngEncoder)
        pngEncoder.link(multiFileSink)
        #Video part
        pngQueue.link(videoSink)

        #connect pads
        teePad = tee.get_request_pad('src_%u')
        videoQPad = videoQueue.get_static_pad('sink')
        teePad.link(videoQPad)

        #connect pads
        teePad = tee.get_request_pad('src_%u')
        pngQPad = pngQueue.get_static_pad('sink')
        teePad.link(pngQPad)

    def onShutdown(self, window, args):
        Gtk.main_quit()
        self.pipeline.set_state(Gst.State.NULL)

    def onPlay(self, button, *args):
        self.pipeline.set_state(Gst.State.PLAYING)
        self._disableButtons(excepting=['BtnStop',])

    def onStop(self, button, *args):
        self.pipeline.set_state(Gst.State.NULL)
        self._disableButtons(excepting=['BtnRecord', 'BtnTime', 'ComboFPS'])

    def onRecord(self, button, *args):
        self._disableButtons(excepting = ['BtnStop'])
        self.pipeline.set_state(Gst.State.PLAYING)

    def onFpsSelect(self, button, *args):
        print self, button, args

    def _disableButtons(self, excepting):
        for cId in self._controls:
            c = self.builder.get_object(cId)
            c.set_sensitive(cId in excepting)

    def onBusSync(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            message.src.set_property('force-aspect-ratio', True)
            message.src.set_window_handle(self.xid)

    def onDraw(self, widget, evt):
        """
        Draw a gray background when pipeline is in NULL state.
        GStreamer takes care of this in the PAUSED and PLAYING states, otherwise, 
        we simply draw a black rectangle to avoid garbage showing up.
        """
        alloc = widget.get_allocation()
        cr = Gdk.cairo_create(widget.get_window())
        cr.set_source_rgb (0.5, 0.5, 0.5);
        cr.rectangle (0, 0, alloc.width, alloc.height);
        cr.fill();

def main():
    GObject.threads_init()
    Gst.init_check(sys.argv)
    app = FlipBuqUI()
    Gtk.main()

if __name__ == "__main__":
    sys.exit(main())
