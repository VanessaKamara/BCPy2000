# -*- coding: utf-8 -*-
# 
#   $Id: Electrodes.py 3328 2011-06-18 02:17:13Z jhill $
#   
#   This file is part of the BCPy2000 framework, a Python framework for
#   implementing modules that run on top of the BCI2000 <http://bci2000.org/>
#   platform, for the purpose of realtime biosignal processing.
# 
#   Copyright (C) 2007-11  Jeremy Hill, Thomas Schreiner,
#                          Christian Puzicha, Jason Farquhar
#   
#   bcpy2000@bci2000.org
#   
#   The BCPy2000 framework is free software: you can redistribute it
#   and/or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
__all__ = [
	'ChannelSet',
	'channel',
	'trodeplot',
]
import copy, numpy
import ElectrodePositions

class channel:
	
	def __init__(self, pos, neg, gnd, label=None):

		def cleanup(s):
			if isinstance(s, (tuple,list)): s = reduce(list.__add__, [list(cleanup(x)) for x in s])
			if isinstance(s, basestring):
				s = s.replace(',',' ').lstrip('\r\n ([{').rstrip('}]) \n\r')
				s = s.replace('+',' ').replace('&',' ')
				s = s.split()
			s = tuple(s)
			if s == ('0',) or s == (0,): s = ()
			return s

		pos = cleanup(pos)
		if isinstance(pos, (tuple,list)): pos = [(k,1.0/len(pos)) for k in pos]
		self.pos = dict(pos)
		
		neg = cleanup(neg)
		if isinstance(neg, (tuple,list)): neg = [(k,1.0/len(neg)) for k in neg]
		self.neg = dict(neg)
		
		if isinstance(gnd, dict): gnd = gnd.keys()
		gnd = cleanup(gnd)
		self.gnd = tuple(gnd)
		
		self.label = label
		self._update()
		
	def _update(self, add=(), subtract=()):
		t = {}; case = {}
		if subtract == None: subtract = {}
		for d in list(subtract) + [self.neg]:
			for k in d:
				u = k.upper(); case[u] = k
				t[u] = t.get(u, 0.0) - float(d[k])
		if add == None: add = {}
		for d in list(add) + [self.pos]:
			for k in d:
				u = k.upper(); case[u] = k
				t[u] = t.get(u, 0.0) + float(d[k])
		tol = 1e-6
		self.pos = dict([(case[k],+v) for k,v in t.items() if v > +tol])
		self.neg = dict([(case[k],-v) for k,v in t.items() if v < -tol])
		
		if len(self.pos) and len(self.neg):
			car = 1.0/(len(self.pos) + len(self.neg))
			carred = 1.0 - car
			if max([abs(v - carred) for v in self.pos.values()] + [abs(v - car) for v in self.neg.values()]) < tol:
				for k in self.pos:
					self.pos[k] = 1.0
					self.neg[k] = car
			elif max([abs(v - carred) for v in self.neg.values()] + [abs(v - car) for v in self.pos.values()]) < tol:
				for k in self.pos:
					self.neg[k] = 1.0
					self.pos[k] = car
		return self
	
	def __repr__(self):
		return '<%s object at 0x%08X>: %s' % (self.__class__.__name__, id(self), self.__str__())
	
	def __str__(self):
		s = self._dict2str(self.pos)+' - '+self._dict2str(self.neg)
		if self.label != None: s = self.label + ' = ' + s
		return s
	
	def _dict2str(self, d):
		if len(d) == 0: return '0'
		s = ''
		tol = 1e-6
		k,w = d.keys(),d.values()
		avg = len(d) > 1 and max([abs(x - 1.0/len(d)) for x in w]) < tol
		if len(d) > 4:
			if avg: s = '(average of %d electrodes)' % len(d)
			else: s = '(weighted combination of %d electrodes)' % len(d)
		elif avg:
			s = '(' + ' + '.join(k) + ')/%d' % len(d)
		else:
			for i in range(len(w)):
				if abs(w[i] - 1.0) < tol: pass
				elif abs(1.0/w[i] - round(1.0/w[i])) < tol: k[i] = '%s/%d' % (k[i],round(1.0/w[i]))
				else: k[i] = '%g*%s' % (w[i],k[i])
			s = ' + '.join(k)
			if len(d) > 1: s = '(' + s + ')'
		return s
		
	def __iadd__(self, other):
		return self._update(add=[other.pos], subtract=[other.neg])
	def __isub__(self, other):
		return self._update(add=[other.neg], subtract=[other.pos])
	def __imul__(self, x):
		for k in self.pos: self.pos[k] *= float(x)
		for k in self.neg: self.neg[k] *= float(x)
		return self._update()
	def __idiv__(self, x):
		for k in self.pos: self.pos[k] /= float(x)
		for k in self.neg: self.neg[k] /= float(x)
		return self._update()
	
	def __add__(self, x): return self.copy().__iadd__(x)
	def __sub__(self, x): return self.copy().__isub__(x)
	def __mul__(self, x): return self.copy().__imul__(x)
	def __rmul__(self, x): return self.copy().__imul__(x)
	def __div__(self, x): return self.copy().__idiv__(x)
	def __neg__(self):
		x = self.copy()
		x.pos,x.neg = x.neg,x.pos
		return x

	def get_label(self, lower=False):
		x = self.label
		if x == None: x = sorted(self.pos.keys())[0]
		if lower: x = x.lower()
		return x
		
	def get_position(self, type='schematic2D'):
		return get_position(self.get_label(), type=type)
		
	def copy(self):
		return copy.deepcopy(self)

class ChannelSet(numpy.matrix):
	
	def __new__(cls, s=None):
		if s == None: self = []
		self = cls.cparse(s)
		self = numpy.matrix(self, dtype=numpy.object).view(cls)
		if self.size == 0: self.shape = (0,1)
		return self
		
	def plot(self, *pargs, **kwargs):
		trodeplot(self, *pargs, **kwargs)
		
	def stplot(self, img, fs=None, drawnow=True, **kwargs):
		#kwargs['colorbar'] = kwargs.get('colorbar', True)
		if img.shape[0] != self.size: raise ValueError("number of rows in image should match number of channels (=%d)" % self.size)
		import SigTools
		pylab = SigTools.Plotting.load_pylab()
		t = numpy.arange(img.shape[1], dtype=numpy.float64)
		if fs == None: x = None; xlabel = 'time-sample index'
		else: x = t = SigTools.samples2msec(t, fs); xlabel = 'time (msec)'
		x = None
		pylab.subplot(121)
		h = SigTools.Plotting.imagesc(img, x=x, aspect='auto', drawnow=False, picker=5, **kwargs)
		ax = pylab.gca()
		if x == None and fs != None:
			xl = ax.get_xlim()
			xt = numpy.array([x for x in ax.get_xticks() if min(xl)<=x<=max(xl)])
			xtl = ['%g' % x for x in SigTools.samples2msec(xt, fs)]
			ax.set(xticks=xt, xticklabels=xtl)
		ax.set(xlabel=xlabel, yticks=range(img.shape[0]), yticklabels=['%d: %s' % x for x in enumerate(self.get_labels())])
		ax.grid(True)
		h.channels = self
		h.img = numpy.asarray(img)
		h.timebase = t
		h.spaceax = pylab.subplot(222)
		h.timeax = pylab.subplot(224)
		def onpick(evt):
			col = int(round(evt.mouseevent.xdata))
			row = int(round(evt.mouseevent.ydata))
			h = evt.artist
			pylab.axes(h.spaceax)
			h.channels.plot(h.img[:,col], clim=h.get_clim(), drawnow=False)
			pylab.axes(h.timeax)
			SigTools.plot(h.timebase, h.img[row], drawnow=False)
			pylab.gca().set(ylim=h.get_clim(), xlim=(h.timebase[0],h.timebase[-1]))
			pylab.draw()
		pylab.gcf().canvas.mpl_connect('pick_event', onpick)
		if drawnow: pylab.draw()
		return h
	
	def get_labels(self, lower=False, flatten=True):
		out = []
		for row in self.A:
			row = [element.get_label(lower=lower) for element in row]
			if flatten: out += row
			else: out.append(row)
		return out
		
	def get_positions(self, type='schematic2D'):
		x = numpy.zeros(self.shape, dtype=numpy.float64)
		y = numpy.zeros(self.shape, dtype=numpy.float64)
		lab = self.get_labels(lower=True, flatten=True)
		for i,ch in enumerate(lab):
			x.flat[i],y.flat[i] = get_position(ch, type=type)
		return x,y
		
	def sqdist(self, type='schematic2D'):
		x,y = self.flatten().get_positions()
		p = x + 1j * y
		q = numpy.abs(p - p.T)
		return q
	
	@staticmethod
	def cparse(s):
		"""
		Parse a file, sequence of strings or multiline string.
		On each line, the first (space- or comma-delimited) field is
		the electrode position, the second is the reference electrode(s)
		and the third is the ground electrode, for a given channel.
		
		Optionally, each line may begin with a number, or number followed
		by a colon, indicating the electrode "index". This index is not
		obeyed strictly, but the outputs are sorted by increasing value of
		these indices. 
		"""###

		if s == None: s = []
		if isinstance(s, file): s = s.readlines()
		if isinstance(s, basestring): s = [x for x in s.replace('\r\n', '\n').replace('\r','\n').split('\n') if len(x)]
		if isinstance(s, numpy.ndarray): s = list(numpy.asarray(s).flat)

		out,ind = [],0
		for si in s:
			if isinstance(si, (tuple,list)):
				row = list(si)
			else:
				if not isinstance(si, basestring): raise ValueError("inputs are expected to be strings")
				if len(si.strip()) == 0: continue
				
				import re
				b = [
					re.compile(r'^\s*\{(.*)\}\s*'),
					re.compile(r'^\s*\[(.*)\]\s*'),
					re.compile(r'^\s*\((.*)\)\s*'),
					re.compile(r'^\s*([^\{\[\(\)\]\}\s]+)\s*'),
				]
				r = re.compile(r'[\s,:;]+')
				(x,n) = r.subn(' ', si.strip())
				row = []
				while len(x):
					for r in b:
						m = r.match(x)
						if m != None:
							row.append(m.groups()[0].split())
							x = r.sub('', x)
							break
					else:
						raise RuntimeError('could not parse channel definition string "%s"' % x)
			if len(row) == 4:
				ind = ' '.join(row.pop(0))
				try: ind = int(ind)
				except: raise RuntimeError('failed to interpret string "%s" as an index' % ind)		

			if len(row) == 1: row.append('REF?')
			if row[1] == None: row[1] = 'REF?'
			if len(row) == 2: row.append('GND?')
			if row[2] == None: row[2] = 'GND?'
			if len(row) != 3: raise RuntimeError('channel definition string "%s" should have 3 or 4 fields' % si)
			
			ch = channel(pos=row[0], neg=row[1], gnd=row[2])
			out.append((ind,ch))
			ind += 1
		
		out = [[ch] for ind,ch in sorted(out)]
		nch = len(out)
		return out
		

def trodeplot(channels=(), act='connected',
		ref=None, gnd=None, troderadius='auto',
		surf=70, contour='auto', scheme='auto',
		head=True, eegbg='auto', ears='auto', nose='auto',
		color='k', facecolor='auto', cmap='jet', clim='auto', balance=0.0,
		labels='auto', indices='auto', one_based=False, fontsize='auto',
		ax=None, layout=None, title=None, hold=False, drawnow=True, use_pcolor=False,
	):
	"""
	channels      Channels to plot. May be a sequence of strings, a single
	              space-delimited string of electrode names, or a sequence
	              of channel objects.
	act           An optional sequence of activation values. May also be
	              the string 'connected' which has the same effect as
	              it does in <facecolor>.
	ref           An optional string (or sequence of strings) specifying
	              the names of the reference electrode(s).
	gnd           An optional string (or sequence of strings) specifying
	              the names of the ground electrode(s).
	troderadius   Radius of the circles representing the electrodes, in
	              the ballpark of, say, 0.05, or alternatively 'auto'.
	surf          Whether to draw an interpolated scalp map (assuming <act>
	              has been supplied).  May be True, False or an integer
	              indicating the resolution of the interpolation.
	contour       Whether to draw contours (assuming <act> has been supplied).
	              May be True, False or 'auto'.
	scheme        Whether to draw other electrodes, besides those mentioned,
	              from the same "schemes". May be True, False, 'auto', or a
	              space-delimited string (or tuple of strings or list of
	              strings) specifying explicitly which schemes to draw. The
	              'auto' or True setting makes an intelligent guess at which
	              schemes to use, although if no <channels> at all are
	              supplied, the default is to draw three schemes:
	              scheme='extended1020 eyes_monopolar ears'. The strings
	              must be keys of the dict ElectrodePositions.schemes
	head          Whether to draw a circle for the head: True or False
	eegbg         Whether to draw 10-20-system grid lines: True, False or
	              'auto'.
	ears          Whether to draw ears: True, False or 'auto'.
	nose          Whether to draw a nose: True, False or 'auto'.
	color         A colour specification for the lines, circles and text.
	facecolor     May be True, False or 'auto' (all of which determine
	              whether the <act> values are used to colour the electrode
	              circles). Alternatively it may be 'connected', which causes
	              four different types of electrodes (explicitly supplied 
	              <channels>, <ref>, <gnd> and others from the same <scheme>)
	              to be distinguishable by colour.  Finally, facecolor may
	              also be a single colour specification applied to all.
	cmap          A colormap for the interpolated scalp map.
	clim          Colour limits: may be 'auto' or a sequence (min,max).
	balance       Balance point for colour limits: if not None, the middle
	              of the colormap will be mapped to this value.
	labels        Whether to draw text labels indicating the electrode names.
	              May be True, False, 'auto', or a tuple indicating where to
	              draw them, the 'auto' default being equivalent to (0,0)
	              which is the centre of the electrode
	indices       Whether to draw text labels indicating the numeric indices
	              of the electrodes that were explicitly given in <channels>.
	              May be True, False or 'auto', or a tuple indicating where
	              to draw them, the 'auto' default being equivalent to (1,1)
	              in electrode-radius coordinates (above and to the right
	              of the electrode).
	one_based     Whether channel-index labels are one-based or zero-based
	              (by default, this is False, meaning the first channel will
	              be labelled 0 in Python style, rather than 1 in Matlab
	              style).
	fontsize      The size of labels and indices. May be 'auto', or a size
	              in points.
	ax            Axes on which to draw. Default is pylab.gca()
	layout        (rows,cols) of subplots if plotting multiple <act> columns
	title         Axes title (or sequence of titles)
	hold          If True, do not clear the axes before starting.
	drawnow       Whether to call pylab.draw() immediately at the end.
	
	"""###
	
	# TODO: meg mode, ecog mode
	import SigTools.Plotting
	from SigTools.LearningTools import sqdist
	import numpy, matplotlib
	
	if channels == None: channels = ()
	if isinstance(channels, basestring): channels = channels.split()
	if not hasattr(channels, '__len__'): channels = [channels]
	if isinstance(channels, numpy.ndarray): channels = list(numpy.asarray(channels).flat)
	if len(channels) and isinstance(channels[0], channel):
		if ref == None: ref = reduce(list.__add__, [ch.neg.keys() for ch in channels if len(ch.neg) < 3])
		if gnd == None: gnd = reduce(list.__add__, [list(ch.gnd) for ch in channels if len(ch.gnd) < 2])
		channels = [ch.get_label() for ch in channels]
	channels = list(channels)
	chk = [ch.lower() for ch in channels]
	
	number_of_explicitly_given_channels = len(channels)
	
	if ref == None: ref = []
	elif isinstance(ref, basestring): ref = ref.split()
	else: ref = list(ref)
	if gnd == None: gnd = []
	elif isinstance(gnd, basestring): gnd = gnd.split()
	else: gnd = list(gnd)

	highlight_connected = (act == 'connected' or facecolor == 'connected')
	if act == None or act == 'connected': contour = surf = False; act = []
	if highlight_connected: facecolor = 'connected'
	
	pylab = SigTools.Plotting.load_pylab()

	act = numpy.asarray(act, dtype=numpy.float64)
	if act.shape[0] not in (0,len(channels)): raise ValueError('wrong number of activation values')
	if len(act.shape) > 1 and act.shape[1] > 1:
		import inspect
		args,argnames = {},inspect.getargspec(trodeplot)[0]
		locals = inspect.currentframe().f_locals
		for a in argnames:
			if a in locals: args[a] = locals[a]
		act = numpy.asarray(act.view())
		nplots = int(numpy.prod(act.shape[1:]))
		act.shape = (act.shape[0], nplots)
		if layout == None: layout = nplots
		if ax == None:
			if not hold: pylab.clf()
			ax = SigTools.Plotting.subplots(layout, visible=False,xlim=(-1,1),ylim=(-1,1))
		h = []
		for i,ai in enumerate(act.T):
			args['act'] = list(ai)
			args['ax'] = ax.flat[i]
			if isinstance(title, (tuple,list)): args['title'] = title[i]
			h += trodeplot(**args)
		if i+1 < ax.size:
			ax.flat[i+1].cla()
			ax.flat[i+1].add_artist(pylab.Text(0,0, text='Fin', fontname='fantasy',clip_on=False, size=20,visible=True))
			ax.flat[i+1].set(visible=True, frame_on=False,xticks=[],yticks=[])
			pylab.draw()
		return h
			
	act = list(act.flat) # from now on, we're only dealing with one sequence
	if len(act):
		if clim == 'auto': clim = numpy.r_[min(act),max(act)]
		if balance != None: clim = balance + numpy.r_[-1,+1] * max(abs(numpy.asarray(clim) - balance))

	if ax == None: ax = pylab.gca()
	else: pylab.axes(ax)
	fig = ax.get_figure()
	if not hold: ax.cla()
	
	h = {'figure':fig, 'axes':ax, 'head':None, 'surf':None, 'dots':None}

	def green(x, x2=None):
		g = numpy.asarray(sqdist(x=x, x2=x2))
		mask = g.flat !=0.0
		gfm = g.flat[mask]
		g.flat[mask] = gfm * (0.5 * numpy.log(gfm) - 1.0)
		return g
		
	def interp(x, y, z, xi, yi):
		if hasattr(x, 'flat'): x = x.flat
		if hasattr(y, 'flat'): y = y.flat
		if hasattr(z, 'flat'): z = z.flat
		if hasattr(xi, 'flat'): xi = xi.flat
		if hasattr(yi, 'flat'): yi = yi.flat
		xy = numpy.array(zip(x,y)) # TODO: handle duplicate positions in xy
		xi,yi = numpy.meshgrid(xi,yi)
		zi = numpy.zeros(xi.shape, dtype=numpy.float64)
		xiyi = numpy.array(zip(xi.flat,yi.flat))
		del xi,yi
		w = numpy.linalg.solve(green(xy), z)
		zi.flat = numpy.dot(green(xiyi, xy), w).flat
		return zi
	
	res = 70
	if isinstance(surf, (int, float)) and surf > 1: res = surf
	if isinstance(cmap, basestring): cmap = pylab.cm.get_cmap(cmap)
	if cmap == None: cmap = pylab.cm.jet
	
	if contour == 'auto': contour = surf
	if surf or contour:
		expand = 1.1
		if not isinstance(expand, (tuple,list,numpy.ndarray)): expand = [expand]
		positions = [get_position(ch, default=None) for ch in chk]
		chx,chy,chz = zip(*[p+(act[i],) for i,p in enumerate(positions) if p != None])	
		xl = numpy.array([min(chx), max(chx)]); xl = xl.mean() + expand[0] * (xl - xl.mean())
		yl = numpy.array([min(chy), max(chy)]); yl = yl.mean() + expand[-1] * (yl - yl.mean())
		xl = yl = [-1.0, 1.0]
		chxi = numpy.linspace(xl[0], xl[1], res, endpoint=True)
		chyi = numpy.linspace(yl[0], yl[1], res, endpoint=True)
		chzi = interp(chx, chy, chz, chxi, chyi)
		h['contour'] = h['surf'] = None		
		if surf:
			if use_pcolor:
				h['surf'] = pylab.pcolor(chxi, chyi, chzi, zorder=1)
				h['surf'].set(cmap=cmap,clim=clim,clip_path=None)
			else:
				h['surf'] = matplotlib.image.NonUniformImage(ax, extent=(xl[0],xl[1],yl[0],yl[1]), interpolation='bilinear', zorder=1)
				h['surf'].set(cmap=cmap,clim=clim,clip_path=None)
				h['surf'].set_data(chxi, chyi, chzi)
				ax.images.append(h['surf'])
			clim = h['surf'].get_clim()
		if contour:
			h['contour'] = pylab.contour(chxi,chyi,chzi, zorder=1.5, hold='on', colors=[color], linestyles=['--'])
	
	if highlight_connected:
		for i,r in enumerate(ref):
			if r.lower() not in chk: channels.append(r); chk.append(r.lower())
			ref[i] = r.lower()
		for i,g in enumerate(gnd):
			if g.lower() not in chk: channels.append(g); chk.append(g.lower())
			gnd[i] = g.lower()
	if scheme == 'auto':
		if len(channels) == 0: 	scheme = 'extended1020 eyes_monopolar ears'
		else: scheme = not surf	
	if scheme:
		if not isinstance(scheme, (tuple,list,basestring,numpy.ndarray)): scheme = None
		channels,ans = match_schemes(channels, force_schemes=scheme)
	
	chk = [ch.lower() for ch in channels]
	act += [numpy.nan] * (len(channels)-len(act))
	chx,chy,chz = zip(*[get_position(ch)+(act[i],) for i,ch in enumerate(chk)])	
	chx,chy,chz = list(chx), list(chy), list(chz)
	
	if troderadius == 'auto':
		if surf: troderadius = 0.02
		elif len(channels) > 136: troderadius = 0.04
		else: troderadius = 0.06

	y = 1.0
	for i,x in enumerate(chx):
		if numpy.isnan(x): chx[i] = 1 + troderadius*2.2; chy[i] = y; y -= troderadius * 2.2
	
	eeg = True; meg = False
	if nose == 'auto': nose = (eeg or meg) and head
	h['nose'] = None
	if nose:
		nxy = numpy.array([[0.20, -0.01], [0.13, 0.10], [0.07, 0.14], [0.0, 0.16]])
		nxy = numpy.r_[nxy[:-1], nxy[::-1]*[[-1,1]]] + [[0,1]]
		h['nose'] = pylab.Polygon(nxy, closed=False, edgecolor=color, facecolor='None', clip_on=False, zorder=0); ax.add_patch(h['nose'])
		#h['nose'] = SigTools.Plotting.curve(nxy, edgecolor=color, facecolor='None', clip_on=False, zorder=0, hold=True)
	if ears == 'auto': ears = (eeg or meg) and head
	h['ears'] = []
	if ears:
		w = 0.1 # width factor
		q = 0.04 # length factor
		x = numpy.array([.492, .510, .518, .5299, .5419, .54, .547, .532, .510, .484]) * 2
		y = numpy.array([q+.0555, q+.0775, q+.0783, q+.0746, q+.0555, -.0055, -.0932, -.1313, -.1384, -.1199]) * 2
		x = x - 1; x = w * x/max(x) + 1
		y[[0, -1]] = numpy.sign(y[[0,-1]]) * (1 - x[[0,-1]] ** 2) ** 0.5;
		exy = numpy.c_[x,y]
		right = pylab.Polygon(exy,            closed=False, edgecolor=color, facecolor='None', clip_on=False, zorder=0); ax.add_patch(right)
		left  = pylab.Polygon(exy * [[-1,1]], closed=False, edgecolor=color, facecolor='None', clip_on=False, zorder=0); ax.add_patch(left)
		#right = SigTools.Plotting.curve(exy,            edgecolor=color, facecolor='None', clip_on=False, zorder=0, hold=True)
		#left  = SigTools.Plotting.curve(exy * [[-1,1]], edgecolor=color, facecolor='None', clip_on=False, zorder=0, hold=True)
		h['ears'] = [left,right]

	if head or h.get('surf') or h.get('contour'): #or h.get('nose') or h.get('ears'):
		h['head'] = pylab.Circle((0.0,0.0), radius=1.0, edgecolor='none', facecolor='none', clip_on=False, zorder=2); ax.add_patch(h['head'])
		if head: h['head'].set_edgecolor(color)
		if h.get('surf'): h['surf'].set_clip_path(h['head'])
		for hh in getattr(h.get('contour'), 'collections', []): hh.set_clip_path(h['head'])
		#if h.get('nose'): h['nose'].set_clip_path(h['head'])  # TODO: how to invert the path?
		#if h.get('ears'): h['ears'].set_clip_path(h['head'])  # TODO: how to invert the path?

	if eeg and eegbg:
		gridlines = [
			'f9 f7 f5 f3 f1 fz f2 f4 f6 f8 f10',
			'ft9 ft7 fc5 fc3 fc1 fcz fc2 fc4 fc6 ft8 ft10',
			'tp9 tp7 cp5 cp3 cp1 cpz cp2 cp4 cp6 tp8 tp10',
			'p9 p7 p5 p3 p1 pz p2 p4 p6 p8 p10',
			'f5 fc5 c5 cp5 p5',
			'af3 f3 fc3 c3 cp3 p3 po3',
			'f1 fc1 c1 cp1 p1',
			'f2 fc2 c2 cp2 p2',
			'af4 f4 fc4 c4 cp4 p4 po4',
			'f6 fc6 c6 cp6 p6',
		]
		if eegbg == 'auto':
			drawing = zip(chx,chy)
			gpos = [get_position(ch) for ch in ' '.join(gridlines).split()]
			eegbg = head and not surf and False not in [gp in drawing for gp in gpos]
		if eegbg:
			circ = pylab.Circle((0.0,0.0), radius=0.82, edgecolor=color, facecolor='none', zorder=3); ax.add_patch(circ)
			h['gridlines'] = [circ]
			for gl in gridlines:
				x,y = zip(*[get_position(ch) for ch in gl.split()])
				h['gridlines'] += pylab.plot(x, y, linestyle='-', marker='None', color=color, zorder=3)
			h['gridlines'] += pylab.plot([0,0], [-1,+1], linestyle='-', marker='None', color=color, zorder=3)
			h['gridlines'] += pylab.plot([-1,+1], [0,0], linestyle='-', marker='None', color=color, zorder=3)
	h['dots'] = []
	h['labels'] = []
	h['indices'] = []
	#dfc = fig.get_facecolor()
	dfc = None
	if dfc in ('none','None',None): dfc = 'w'
	if facecolor not in  ('auto','connected') and isinstance(facecolor, (basestring,tuple,list,float)): dfc = facecolor
	for i, (x,y) in enumerate(zip(chx,chy)):
		if fontsize == 'auto':
			fontsize = numpy.diff(ax.get_position(),axis=0).flat[-1] * fig.get_size_inches()[1] * 1.2
			fontsize = int(round(fontsize))
		circ = pylab.Circle((x,y), radius=troderadius, edgecolor=color, facecolor=dfc, clip_on=False, zorder=4); ax.add_patch(circ); h['dots'].append(circ)
		z = act[i]
		if facecolor == 'auto': actface = (not surf or eeg and (x**2+y**2)**0.5 > 1.005)
		else: actface = isinstance(facecolor, (int,bool)) and facecolor
		if facecolor == 'connected':
			actface = False
			if i < number_of_explicitly_given_channels: circ.set_facecolor([1.0,0.5,0.5])
			elif chk[i] in ref: circ.set_facecolor([0.5,0.5,1.0])
			elif chk[i] in gnd: circ.set_facecolor([0.5,1.0,0.5])
		if actface and not numpy.isnan(z):
			z = (z - clim[0]) / (clim[-1] - clim[0])
			circ.set_facecolor(cmap(z))
		props = {'fontsize':fontsize,'color':color,'fontname':'monospaced','verticalalignment':'center','horizontalalignment':'center', 'clip_on':False, 'zorder':5}
		if labels == 'auto': labels = {True:(0,0), False:False}[troderadius>=0.04]
		if labels:
			xy = numpy.array([x,y])
			if isinstance(labels, (tuple,list,numpy.ndarray)): xy = xy + numpy.asarray(labels) * troderadius
			txt = pylab.Text(xy[0],xy[1], text=channels[i], **props); ax.add_artist(txt); h['labels'].append(txt)
		if indices == 'auto': indices = {True:(1,1), False:False}[troderadius>=0.04]
		if indices:
			xy = numpy.array([x,y])
			if indices == True: indices = (1,1)
			if isinstance(indices, (tuple,list,numpy.ndarray)): xy = xy + numpy.asarray(indices) * troderadius
			if i < number_of_explicitly_given_channels: text = str(i + int(bool(one_based)))
			elif chk[i] in ref: text = 'ref'
			elif chk[i] in gnd: text = 'gnd'
			else: text = ''
			txt = pylab.Text(xy[0],xy[1], text=text, **props); ax.add_artist(txt); h['indices'].append(txt)
	
	ax.set(aspect='equal', xticks=[],yticks=[],frame_on=False,xlim=(-1,1),ylim=(-1,1), visible=True)
	if title != None:
		t = ax.set_title(title)
		t.set(position=(1,0),verticalalignment='bottom',rotation=45)
	if drawnow: pylab.draw()
	return [h]

def match_schemes(channels, force_schemes=None):
	
	if not isinstance(channels, basestring):
		for ch,i in enumerate(channels):
			if hasattr(ch, 'get_label'): ch = ch.get_label()
		channels = ' '.join(channels)
	lchannels = channels.lower().split()
	channels = channels.split()

	if force_schemes == None:
		count = {}
		matched = {}
		lengths = {}
		for k,v in ElectrodePositions.schemes.items():
			v = v.lower().split()
			lengths[k] = len(v)
			for ch in channels:
				if ch.lower() in v:
					count[k] = count.get(k, 0) + 1
					matched[ch] = matched.get(ch, [])
					matched[ch].append(k)
		matchingschemes = {}
		for ch, cand in matched.items():
			cand = [(-count[scheme],lengths[scheme],scheme) for scheme in cand]
			best = sorted(cand)[0][2]
			matchingschemes[best] = tuple(ElectrodePositions.schemes[best].split())
	else:
		if isinstance(force_schemes, basestring): force_schemes = force_schemes.split()
		matchingschemes	= dict([(sch,ElectrodePositions.schemes[sch.lower()].split()) for sch in force_schemes])
	
	universe = {}
	for v in matchingschemes.values():
		for vi in v:
			if vi.lower() not in lchannels: universe[vi.lower()] = vi
	universe = channels + sorted(universe.values())
	return universe,matchingschemes	

def get_position(label, type='schematic2D', default=(numpy.nan,numpy.nan)):
	return getattr(ElectrodePositions, type).get(label.lower(), default)
