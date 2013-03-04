#!/usr/bin/python
# -*- coding: latin-1 -*-
import wx                  # This module uses the new wx namespace
import tools3D
try:
  version = tools3D.GetVersion()
  if version != "v1.0d":
	raise ValueError
except:
	class ErrApp( wx.App ):
		def OnInit( self ):
			dlg = wx.MessageDialog(None, "It seems that there is a conflicting dll\nPlease make sure to uninstall previous version\nAnd reinstall this one",
									 'Error',
								 wx.OK | wx.ICON_ERROR
								 )
			dlg.ShowModal()
			dlg.Destroy()
			return False

	app = ErrApp( False )
	app.MainLoop()
				
	exit()


import zipUtils
import dircache
import sys
import os
import os.path
import webbrowser
import struct
import zlib
import QuestionDialog
import about


import Image
import ImageDraw
import numpy as Numeric

import wx.lib.masked as masked

import rgnReader

MAPPER_VERSION = "2013.5c"
SCROLL_RATE = 1
class CreateRgnFromFile( wx.Dialog ):
	"""Dialog for entering region setting ( file , size , name, config.bmp )"""
	def __init__( self, parent, title, wildCard, bAllowScale = False ):
		self.wildCard = wildCard
		pre = wx.PreDialog()        
		pre.Create(parent, -1, "Create region from "+title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE)
		self.PostCreate(pre)
		labelFileName = wx.StaticText(self, -1, "Filename")  
		self.fileName = wx.TextCtrl( self, -1, "",style=wx.TE_READONLY )
		browseFile= wx.Button( self, -1, "...",size=(20,-1) )
		if bAllowScale:
			label = wx.StaticText(self, -1, "Scale factor:")
			self.imageFactor = wx.ComboBox( self, -1, "Default factor", style = wx.CB_DROPDOWN )
			scaleTable = [ "100m","250m","500m","Default factor", "1000m", "1500m", "2000m", "import.dat","2500m","3000m","3500m","4000m","4500m","5000m" ]
			for s in scaleTable:
				self.imageFactor.Append( s )
		self.fromConfig = wx.RadioButton( self, -1, "Config.bmp", style = wx.RB_GROUP )
		self.configFileName = wx.TextCtrl( self, -1, "",style=wx.TE_READONLY )
		browseConfig = wx.Button( self, -1, "...",size=(20,-1) )
		self.fromSize = wx.RadioButton( self, -1, "Specify size" )
		self.sizeX = masked.NumCtrl( self, value=8, integerWidth=3, allowNegative=False, min = 2 )
		self.sizeY = masked.NumCtrl( self, value=8, integerWidth=3, allowNegative=False, min = 2 )
		sizer = wx.BoxSizer(wx.VERTICAL)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add( labelFileName, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		box.Add( self.fileName, 0, wx.ALIGN_CENTRE|wx.EXPAND|wx.ALL, 5)
		box.Add( browseFile, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		sizer.Add(box, 0, wx.GROW|wx.ALL, 5)
		if bAllowScale:
		  box = wx.BoxSizer(wx.HORIZONTAL)
		  box.Add( label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		  box.Add( self.imageFactor, 0, wx.ALIGN_CENTRE|wx.EXPAND|wx.ALL, 5)
		  sizer.Add(box, 0, wx.GROW|wx.ALL, 5)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add( self.fromConfig, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		box.Add( self.configFileName, 0, wx.ALIGN_CENTRE|wx.EXPAND|wx.ALL, 5)
		box.Add( browseConfig, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		sizer.Add(box, 0, wx.GROW|wx.ALL, 5)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add( self.fromSize, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		box.Add( self.sizeX, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		box.Add( self.sizeY, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
		sizer.Add(box, 0, wx.GROW|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALL, 5)
		btnsizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK)
		self.btnOk.SetDefault()
		btnsizer.AddButton(self.btnOk)
		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()
		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
		self.SetSizer(sizer)
		sizer.Fit(self)
		self.Bind(wx.EVT_BUTTON, self.OnBrowseFile, browseFile)
		self.Bind(wx.EVT_BUTTON, self.OnBrowseConfig, browseConfig)
		self.Bind(wx.EVT_RADIOBUTTON, self.OnSelectSize, self.fromSize )
		self.Bind(wx.EVT_RADIOBUTTON, self.OnSelectConfig, self.fromConfig )
		self.sizeX.Enable( True )        
		self.sizeY.Enable( True )        
		self.configFileName.Enable( False )        
		self.fromConfig.SetValue( False )
		self.fromSize.SetValue( True )
		self.btnOk.Enable( False )
		
	def GetImageFactor( self ):
		"""return the factor for standard terran mod or a real value"""
		s = self.imageFactor.GetValue()
		scales = { "100m" : 1.3725 ,"250m":1.9608 ,"500m":2.9412 ,"Default factor":3., "1000m":4.9020, "1500m":6.8627, "2000m":8.8235, "import.dat":9.7832,"2500m":10.7843,"3000m":12.7451,"3500m":14.7059,"4000m":16.6667,"4500m":18.6275,"5000m":20.5882 }
		if s in scales.keys():
			return scales[s]
		try:
			return float( s )
		except:
			return 3.
		
	def OnSelectConfig( self, event ):
		self.sizeX.Enable( False )        
		self.sizeY.Enable( False )        
		self.configFileName.Enable( True )        

	def OnSelectSize( self, event ):
		self.sizeX.Enable( True )        
		self.sizeY.Enable( True )        
		self.configFileName.Enable( False )        
		
	def OnBrowseFile( self, event ):
		dlg = wx.FileDialog( self
							, message = "Choose a file"
							, defaultDir = os.getcwd()
							, defaultFile = ""
							, wildcard = self.wildCard
							, style=wx.OPEN )
		if dlg.ShowModal() == wx.ID_OK:
			paths = dlg.GetPaths()
			dlg.Destroy()
			try:
				im = Image.open( paths[0] )
			except:
				dlg1 = wx.MessageDialog( self, "This is not a valid file","Error",wx.OK | wx.ICON_ERROR )
				dlg1.ShowModal()
				dlg1.Destroy()
				return
			x = (im.size[0]-1)/64
			y = (im.size[1]-1)/64
			self.fileName.SetValue( paths[0] )
			self.sizeX.SetValue( x )
			self.sizeY.SetValue( y )
			del im
			self.btnOk.Enable( True )
		dlg.Destroy()
		
	def OnBrowseConfig( self, event ):
		dlg = wx.FileDialog( self
						   , message = "Choose a config.bmp"
						   , defaultDir = os.getcwd()
						   , defaultFile = ""
						   , wildcard = "config (*.bmp)|*config.bmp"
						   , style = wx.OPEN )
		if dlg.ShowModal() == wx.ID_OK:
			paths = dlg.GetPaths()
			dlg.Destroy()
			self.configFileName.SetValue( paths[0] )
			try:
				im = Image.open( paths[0] )
			except:
				dlg1 = wx.MessageDialog( self, "This is not a valid config","Error", wx.OK | wx.ICON_ERROR )
				dlg1.ShowModal()
				dlg1.Destroy()
				return
			x = im.size[0]
			y = im.size[1]
			self.sizeX.SetValue( x )
			self.sizeY.SetValue( y )
			del im
			self.fromConfig.SetValue( True )
			self.fromSize.SetValue( False )
			self.sizeX.Enable( False )        
			self.sizeY.Enable( False )        
			self.configFileName.Enable( True )        
		dlg.Destroy()

class OverViewCanvas( wx.ScrolledWindow):
	def __init__(self, parent, id = -1, size = wx.DefaultSize):
		wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER|wx.FULL_REPAINT_ON_RESIZE)
		self.parent = parent
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_SCROLLWIN, self.OnScroll )
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_CHAR, self.OnKeyDown )
		self.bmp = None
		self.drag = False
		self.buffer = None
		self.wait = False
		self.crop = None
		self.offX = 0
		self.offY = 0
		self.OnSize( None )

	def OnKeyDown( self, event ):
		if self.parent.btnEditMode.GetValue() and self.parent.editMode == EDITMODE_NONE:		
			if self.wait == True:
				return
			if event.GetModifiers() != wx.MOD_CONTROL:
				return
			if event.GetKeyCode() == wx.WXK_LEFT:
				for _ in xrange( self.parent.zoomLevel ):
					offX = self.offX-1
					deletes = [] 
					for city in self.parent.region.allCities:
						if city.xPos+offX < 0:
							deletes.append( (city.cityXPos, city.cityYPos) )
					if len( deletes ) == 0:
						self.offX = offX
				self.UpdateDrawing()
				self.wait = True
				self.Refresh( False )
			if event.GetKeyCode() == wx.WXK_RIGHT:
				for _ in xrange( self.parent.zoomLevel ):
					offX = self.offX+1
					deletes = [] 
					for city in self.parent.region.allCities:
						if city.xPos+city.xSize+offX > self.parent.region.imgSize[0]:
							deletes.append( (city.cityXPos, city.cityYPos) )
					if len( deletes ) == 0:
						self.offX = offX
				self.UpdateDrawing()
				self.wait = True
				self.Refresh( False )
			if event.GetKeyCode() == wx.WXK_UP:
				for _ in xrange( self.parent.zoomLevel ):
					offY = self.offY-1
					deletes = [] 
					for city in self.parent.region.allCities:
						if city.yPos+offY < 0:
							deletes.append( (city.cityXPos, city.cityYPos) )
					if len( deletes ) == 0:
						self.offY = offY
				self.UpdateDrawing()
				self.wait = True
				self.Refresh( False )
			if event.GetKeyCode() == wx.WXK_DOWN:
				for _ in xrange( self.parent.zoomLevel ):
					offY = self.offY+1
					deletes = [] 
					for city in self.parent.region.allCities:
						if city.yPos+city.ySize+offY > self.parent.region.imgSize[1]:
							deletes.append( (city.cityXPos, city.cityYPos) )
					if len( deletes ) == 0:
						self.offY = offY
				self.UpdateDrawing()
				self.wait = True
				self.Refresh( False )
			
	def OnEraseBackground( self, event ):
		pass

	def OnSize(self,event):
		size  = self.ClientSize
		if event:
			size = event.GetSize()
		if self.parent.region:
			if self.buffer == None or ( self.buffer.GetWidth() != size[0] or self.buffer.GetHeight() != size[1] ):
				self.buffer = wx.EmptyBitmap(*size)
			self.UpdateDrawing( newSize = size )	
		else:
			self.buffer = None
		if event:
			event.Skip()
			
	def OnScroll( self, event ):
		size  = self.ClientSize
		x,y = self.GetViewStart()
		if self.parent.region:
			if self.buffer == None or ( self.buffer.GetWidth() != size[0] or self.buffer.GetHeight() != size[1] ):
				self.buffer = wx.EmptyBitmap(*size)
				
			eventType = event.GetEventType()
			if event.GetOrientation() == wx.HORIZONTAL:
				pos = ( event.GetPosition(), y )
			else:
				pos = ( x, event.GetPosition() )
			wx.CallAfter( self.UpdateDrawing )
			
		else:
			self.buffer = None
		event.Skip()
			
	def UpdateDrawing( self, pos = None, newSize = None, finish = True):
		lightDir = rgnReader.Normalize( (1, -5, -1) )
		size  = self.ClientSize
		if newSize:
			size = newSize
		
		if self.parent.zoomLevel == 1:
			sizeDest = ( min( size[0], self.parent.region.height.shape[1] ), min( size[1], self.parent.region.height.shape[0] ) )
			sizeSource = sizeDest
		else:			
			sizeDest = ( min( size[0], self.parent.region.height.shape[1]/self.parent.zoomLevel ), min( size[1], self.parent.region.height.shape[0]/self.parent.zoomLevel ) )
			sizeSource = ( sizeDest[0]*self.parent.zoomLevel,sizeDest[1]*self.parent.zoomLevel )
		print sizeDest,sizeSource
		if pos:
			x,y = pos
		else:
			x,y = self.GetViewStart()
		x *= SCROLL_RATE
		y *= SCROLL_RATE
		x *= self.parent.zoomLevel
		y *= self.parent.zoomLevel
		print 'Drawing from',x,y
		heightMap = Numeric.zeros( (sizeDest[1], sizeDest[0]), Numeric.uint16 )
		try:
			heightMap[::,::] = self.parent.region.height[ y:y+sizeSource[1]:self.parent.zoomLevel, x:x+sizeSource[0]:self.parent.zoomLevel ]
		except ValueError:
			wx.CallAfter( self.UpdateDrawing, None )
			return
		heightMap = heightMap.astype( Numeric.float32 )
		heightMap /= Numeric.array( 10 ).astype( Numeric.float32 )
		rawRGB = tools3D.onePassColors( False, heightMap.shape, self.parent.region.waterLevel, heightMap, rgnReader.GradientReader.paletteWater, rgnReader.GradientReader.paletteLand, lightDir )
		img = wx.EmptyImage( heightMap.shape[1], heightMap.shape[0] )        
		img.SetData( rawRGB )

		dc = wx.BufferedDC(None, self.buffer)
		dc.BeginDrawing()
		dc.SetBackground(wx.Brush("Light Gray"))			
		dc.Clear()			
		dc.DrawBitmap( wx.BitmapFromImage( img ), 0, 0,  False )
		
		dc.SetPen( wx.TRANSPARENT_PEN )
		dc.SetBrush( wx.Brush("Light Gray") )		
		dc.SetLogicalFunction( wx.OR )
		dc.DrawRectangle( 0-x/self.parent.zoomLevel, 0-y/self.parent.zoomLevel, self.offX/self.parent.zoomLevel, self.parent.region.imgSize[1]/self.parent.zoomLevel )
		dc.DrawRectangle( 0-x/self.parent.zoomLevel, 0-y/self.parent.zoomLevel, self.parent.region.imgSize[0]/self.parent.zoomLevel, self.offY/self.parent.zoomLevel )
		dc.DrawRectangle( (self.parent.region.imgSize[0]+self.offX)/self.parent.zoomLevel-x/self.parent.zoomLevel, 0-y/self.parent.zoomLevel, -self.offX/self.parent.zoomLevel, self.parent.region.imgSize[1]/self.parent.zoomLevel )
		dc.DrawRectangle( 0-x/self.parent.zoomLevel, (self.parent.region.imgSize[1]+self.offY)/self.parent.zoomLevel-y/self.parent.zoomLevel, self.parent.region.imgSize[0]/self.parent.zoomLevel, -self.offY/self.parent.zoomLevel )
		dc.SetLogicalFunction( wx.COPY )
		
		if self.parent.overlayCbx.GetValue():
			self.AddMasked( dc, self.parent.zoomLevel, self.parent.region,x/self.parent.zoomLevel,y/self.parent.zoomLevel )
			self.AddGrid( dc, self.parent.zoomLevel, self.parent.region,x/self.parent.zoomLevel,y/self.parent.zoomLevel )
			self.AddOverlay( dc, self.parent.zoomLevel, self.parent.region,x/self.parent.zoomLevel,y/self.parent.zoomLevel )
		if self.crop != None:
			dc.SetPen( wx.TRANSPARENT_PEN )
			dc.SetBrush( wx.Brush("Light Gray") )		
			dc.SetLogicalFunction( wx.XOR )
			crop = [ min( self.crop[0],self.crop[2] ), min( self.crop[1],self.crop[3] ), max( self.crop[0],self.crop[2] ), max( self.crop[1],self.crop[3] ) ]
			self.DrawRectangle( dc,(crop[0]*64-x)/self.parent.zoomLevel, (crop[1]*64-y)/self.parent.zoomLevel, ((crop[2]-crop[0])*64+65)/self.parent.zoomLevel,((crop[3]-crop[1])*64+65)/self.parent.zoomLevel )
			dc.SetLogicalFunction( wx.COPY )
		if finish:
			dc.EndDrawing()
		self.wait = True
		wx.CallAfter( self.Refresh, False )
		if finish == False:
			return dc
		
	def AddGrid( self, dc, zoomLevel, region,xO,yO ):
		lines=[]
		s = (region.height.shape[1],region.height.shape[0])
		for y in xrange( s[1]/int(64) ):
			lines.append( [ 0-xO,y*int(64/zoomLevel)-yO,region.originalConfig.size[0]*int(64/zoomLevel)-xO,y*int(64/zoomLevel)-yO ] )
		for x in xrange( s[0]/int(64) ):
			lines.append( [ x*int(64/zoomLevel)-xO,0-yO,x*int(64/zoomLevel)-xO,region.originalConfig.size[1]*int(64/zoomLevel)-yO ] )
		#dc.SetPen(wx.Pen( wx.Colour( 100,100,100 ) ) )
		dc.SetPen( wx.Pen( "Light Gray" ) )
		dc.DrawLineList( [ (x1+self.offX/zoomLevel,y1+self.offY/zoomLevel,x2+self.offX/zoomLevel,y2+self.offY/zoomLevel) for x1,y1,x2,y2 in lines ] )
		
	def AddOverlay( self, dc, zoomLevel, region,xO,yO ):
		dc.SetPen(wx.Pen("WHITE"))
		dc.SetBrush(wx.Brush( "WHITE",wx.TRANSPARENT ) )
		colours = [ 0, wx.Colour( 255,0,0 ), wx.Colour( 0,255,0 ), 0, wx.Colour( 0,0,255 ) ]
		sizes = [ 0,64,128,0,256 ]
		for city in region.allCities:
			x = int( city.xPos/zoomLevel )
			y = int( city.yPos/zoomLevel )
			width = sizes[city.cityXSize]/zoomLevel
			height = sizes[city.cityYSize]/zoomLevel
			dc.SetPen(wx.Pen("WHITE"))				
			dc.SetBrush(wx.Brush( "WHITE",wx.TRANSPARENT ) )
			dc.SetPen( wx.Pen(colours[city.cityXSize]) )
			dc.SetBrush(wx.Brush( colours[city.cityXSize],wx.TRANSPARENT ) )
			self.DrawRectangle( dc, x-xO,y-yO,width,height )
			self.DrawRectangle( dc, x-xO+1,y-yO+1,width-2,height-2 )
			
	def AddMasked( self, dc, zoomLevel, region,xO,yO ):
		dc.SetPen(wx.Pen("LIGHT GRAY"))
		dc.SetBrush(wx.Brush("LIGHT GRAY", wx.CROSSDIAG_HATCH ) )
		width = 64/zoomLevel
		height = 64/zoomLevel
		for x,y in region.missingCities:
			x = int( x*64/zoomLevel )
			y = int( y*64/zoomLevel )
			self.DrawRectangle( dc, x-xO,y-yO,width,height )
	
	def HighlightCity( self, zoomLevel, region, pos ):
		dc = self.UpdateDrawing( finish = False )
		xO,yO = self.GetViewStart()
		colours = [ 0, wx.Colour( 255,0,0 ), wx.Colour( 0,255,0 ), 0, wx.Colour( 0,0,255 ) ]
		for city in region.allCities:
			if pos[0] >= city.cityXPos and pos[0] < city.cityXPos+city.cityXSize and pos[1] >= city.cityYPos and pos[1] < city.cityYPos+city.cityYSize :
				x = int( city.xPos/zoomLevel )
				y = int( city.yPos/zoomLevel )
				width = int( city.xSize/zoomLevel )
				height = int( city.ySize/zoomLevel )
				dc.SetPen(wx.Pen(colours[city.cityXSize]))
				dc.SetBrush(wx.Brush( colours[city.cityXSize],wx.CROSSDIAG_HATCH ) )		
				self.DrawRectangle( dc, x+1-xO,y+1-yO,width-2,height-2 )
				self.DrawRectangle( dc, x-xO,y-yO,width,height )
				self.DrawRectangle( dc, x-xO-1,y-1-yO,width+2,height+2 )
				break
		dc.EndDrawing()

	def HighlightNewCity( self, zoomLevel, region, pos, size ):
		dc = self.UpdateDrawing( finish = False )
		xO,yO = self.GetViewStart()
		colours = [ 0, wx.Colour( 255,0,0 ), wx.Colour( 0,255,0 ), 0, wx.Colour( 0,0,255 ) ]
		x = int( pos[0]*64/zoomLevel )
		y = int( pos[1]*64/zoomLevel )
		width = size*64/zoomLevel
		height = size*64/zoomLevel
		dc.SetPen(wx.Pen(colours[size]))
		dc.SetBrush(wx.Brush( colours[size],wx.TRANSPARENT ) )
		self.DrawRectangle( dc, x+1-xO,y+1-yO,width-2,height-2 )
		self.DrawRectangle( dc, x-xO,y-yO,width,height )
		self.DrawRectangle( dc, x-1-xO,y-1-yO,width+2,height+2	)
		dc.EndDrawing()
		
	def DrawRectangle( self, dc, x, y, width, height ):
		dc.DrawRectangle( x+self.offX/self.parent.zoomLevel, y+self.offY/self.parent.zoomLevel, width, height )	

	def OnPaint(self, event):
		if self.buffer is None:
			self.clear = False
			self.wait = False
			dc = wx.PaintDC(self)
			self.DoPrepareDC(dc)
			dc.SetBackground(wx.Brush(self.GetBackgroundColour()))			
			dc.Clear()			
		if self.buffer is not None:
			self.wait = False
			dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_CLIENT_AREA )
	

	  
EDITMODE_NONE = 0
EDITMODE_SMALL = 1
EDITMODE_MEDIUM = 2
EDITMODE_BIG = 3
EDITMODE_VOID = 4

class OverView( wx.Frame ):
	def __init__( self, parent, title, virtualSize, pos=wx.DefaultPosition, size=wx.DefaultSize,
				  style=wx.DEFAULT_FRAME_STYLE |wx.MINIMIZE_BOX |wx.MAXIMIZE_BOX ):
		wx.Frame.__init__(self, parent, -1, title, pos, size, style)
		self.region = None
		self.SetSizeHintsSz( wx.Size( 700,400 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		self.editMode = EDITMODE_NONE
		self.btnSmall = wx.ToggleButton(self, -1, "Small\nCity")
		self.Bind( wx.EVT_TOGGLEBUTTON, self.SetEditModeSmall, self.btnSmall )    
		self.btnMedium = wx.ToggleButton(self, -1, "Medium\nCity")
		self.Bind( wx.EVT_TOGGLEBUTTON, self.SetEditModeMedium, self.btnMedium )    
		self.btnBig = wx.ToggleButton(self, -1, "Big\nCity")
		self.Bind( wx.EVT_TOGGLEBUTTON, self.SetEditModeBig, self.btnBig )    
		self.btnVoid = wx.ToggleButton(self, -1, "Erase\nCity")
		self.Bind( wx.EVT_TOGGLEBUTTON, self.SetEditModeVoid, self.btnVoid )
		self.btnRevert = wx.Button(self, -1, "Revert\nConfig")		
		self.Bind( wx.EVT_BUTTON, self.RevertConfig, self.btnRevert )
		
		self.btnSave = wx.Button(self, -1, "Save\nImage")
		self.Bind( wx.EVT_BUTTON, self.SaveBmp, self.btnSave  )    
		self.btnLoadRgn = wx.Button(self, -1, "Load\nRegion")
		self.Bind( wx.EVT_BUTTON, self.OpenRgn  , self.btnLoadRgn )    
		self.btnCreateRgn = wx.Button(self, -1, "Create\nRegion")
		self.Bind( wx.EVT_BUTTON, self.CreateRgn, self.btnCreateRgn )    
		self.btnSaveRgn = wx.Button(self, -1, "Save\nRegion")
		self.Bind( wx.EVT_BUTTON, self.SaveRgn, self.btnSaveRgn )    
		self.btnExportRgn = wx.Button(self, -1, "Export\nRegion")
		self.Bind( wx.EVT_BUTTON, self.ExportRgn, self.btnExportRgn )    
		self.btnQuit = wx.Button(self, -1, "Quit")
		self.Bind( wx.EVT_BUTTON, self.OnCloseWindow, self.btnQuit )    

		self.btnZoomIn = wx.Button(self, -1, "+", wx.DefaultPosition, wx.Size( 24,-1 ) )
		self.Bind( wx.EVT_BUTTON, self.OnZoomIn, self.btnZoomIn )    
		self.btnZoomOut = wx.Button(self, -1, "-", wx.DefaultPosition, wx.Size( 24,-1 ))
		self.Bind( wx.EVT_BUTTON, self.OnZoomOut, self.btnZoomOut )    

		self.overlayCbx = wx.CheckBox( self, wx.ID_ANY, u"Cities\noverlay" )
		self.overlayCbx.Bind( wx.EVT_CHECKBOX, self.OnOverlay )
		self.overlayCbx.SetValue( True )
		
		self.btnEditMode = wx.ToggleButton( self, wx.ID_ANY, "Edit\nConfig.bmp" );
		self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleEditMode, self.btnEditMode)
		
		self.back = OverViewCanvas(self, -1,size=size)
		self.back.SetBackgroundColour("WHITE")
		self.back.SetVirtualSize(virtualSize)
		self.back.SetScrollRate(SCROLL_RATE,SCROLL_RATE)
		self.back.Bind( wx.EVT_MOTION, self.OnMouseMove )
		self.back.Bind( wx.EVT_LEFT_UP, self.OnLeftUp )
		self.back.Bind( wx.EVT_LEFT_DOWN, self.OnLeftDown )
		
		self.box = wx.BoxSizer(wx.VERTICAL)
		boxh = wx.BoxSizer(wx.HORIZONTAL)
		
		boxh.Add(self.btnSmall, 0 )        
		self.btnSmall.Hide()
		boxh.Add(self.btnMedium, 0 )        
		self.btnMedium.Hide()
		boxh.Add(self.btnBig, 0 )        
		self.btnBig.Hide()
		boxh.Add(self.btnVoid, 0 )        
		self.btnVoid.Hide()
		boxh.Add(self.btnRevert, 0 )
		self.btnRevert.Hide()
		
		boxh.Add(self.btnLoadRgn, 0 )        
		boxh.Add(self.btnCreateRgn, 0 )        
		boxh.Add(self.btnSaveRgn, 0 )
		boxh.Add(self.btnExportRgn, 0 )        
		boxh.Add(self.btnSave, 0 )
		boxh.Add( wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL ), 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		boxh.Add(self.btnEditMode, 0 )
		boxh.Add(self.btnZoomIn, 0, wx.ALIGN_CENTER_VERTICAL)        
		boxh.Add(self.btnZoomOut, 0,wx.ALIGN_CENTER_VERTICAL)        
		boxh.Add(self.overlayCbx, 0, wx.ALIGN_CENTER_VERTICAL)
		boxh.Add( wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL ), 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		boxh.AddStretchSpacer()

		boxh.Add(self.btnQuit, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL )        
		self.box.Add(boxh, 0, wx.EXPAND)
		self.box.Add(wx.StaticLine(self), 0, wx.EXPAND)
		self.box.Add(self.back, 1, wx.EXPAND)
		self.box.Fit(self)
		self.SetSizer(self.box)

		self.SetClientSize( (800,600) )

		self.mydocs = wx.StandardPaths.Get().GetDocumentsDir()
		self.mydocs = os.path.join( self.mydocs, u'SimCity 4/Regions/' )
		
		self.originalColors = None
		self.zoomLevel = 1
		self.zoomLevelPow = 0
		self.region = None
		self.rebuilder = None
	
		self.btnZoomIn.Enable( False )
		self.btnZoomOut.Enable( False )
		self.btnSaveRgn.Enable( False )
		self.btnSave.Enable( False )
		self.overlayCbx.Enable( False )
		self.btnEditMode.Enable( False )
		self.btnExportRgn.Enable( False )
		self.Center()
		
	def OnCloseWindow(self, event):
		dlg = wx.MessageDialog( self, "Are you sure you want to quit ?","SC4Mapper",wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION )
		res = dlg.ShowModal()
		dlg.Destroy()
		if res == wx.ID_NO :
			return
		self.Destroy()
		sys.exit(0)
		
	def RevertConfig( self, event ):
		self.region.allCities = rgnReader.WorkTheconfig( self.region.originalConfig, 250.0 )
		self.region.config =self.region.BuildConfig()
		self.editMode = EDITMODE_NONE
		self.btnSmall.SetValue( False )
		self.btnMedium.SetValue( False )
		self.btnBig.SetValue( False )
		self.btnVoid.SetValue( False )
		self.back.offX = 0
		self.back.offY = 0
		self.back.UpdateDrawing()
		self.back.Refresh( False )
		self.back.SetFocus()
		
	def SetEditModeSmall( self, event ):
		if self.btnSmall.GetValue():
			self.editMode = EDITMODE_SMALL
			self.btnMedium.SetValue( False )
			self.btnBig.SetValue( False )
			self.btnVoid.SetValue( False )
		else:
			self.editMode = EDITMODE_NONE
			self.back.UpdateDrawing()
		self.back.SetFocus()
		
	def SetEditModeMedium( self, event ):
		if self.btnMedium.GetValue():
			self.editMode = EDITMODE_MEDIUM
			self.btnSmall.SetValue( False )
			self.btnBig.SetValue( False )
			self.btnVoid.SetValue( False )
		else:
			self.editMode = EDITMODE_NONE
			self.back.UpdateDrawing()
		self.back.SetFocus()
		
	def SetEditModeBig( self, event ):
		if self.btnBig.GetValue():
			self.editMode = EDITMODE_BIG
			self.btnMedium.SetValue( False )
			self.btnSmall.SetValue( False )
			self.btnVoid.SetValue( False )
		else:
			self.editMode = EDITMODE_NONE
			self.back.UpdateDrawing()
		self.back.SetFocus()
		
	def SetEditModeVoid( self, event ):
		if self.btnVoid.GetValue():
			self.editMode = EDITMODE_VOID
			self.btnMedium.SetValue( False )
			self.btnBig.SetValue( False )
			self.btnSmall.SetValue( False )
		else:
			self.editMode = EDITMODE_NONE
			self.back.UpdateDrawing()
		self.back.SetFocus()	
		
	def OnToggleEditMode( self, event ):
		self.Freeze()
		if self.btnEditMode.GetValue():
			self.btnSmall.SetValue( False )		
			self.btnMedium.SetValue( False )
			self.btnBig.SetValue( False )
			self.btnVoid.SetValue( False )
			
			self.btnSmall.Show()
			self.btnLoadRgn.Hide()
			self.btnMedium.Show()
			self.btnCreateRgn.Hide()
			self.btnBig.Show()
			self.btnSaveRgn.Hide()
			self.btnVoid.Show()
			self.btnExportRgn.Hide()
			self.btnRevert.Show()
			#self.btnCrop.Show()
			self.btnSave.Hide()
			self.overlayCbx.SetValue( True )
			self.overlayCbx.Enable( False )
			self.editMode = EDITMODE_NONE
			self.back.SetFocus()	
		else:
			self.btnSmall.Hide()
			self.btnLoadRgn.Show()
			self.btnMedium.Hide()
			self.btnCreateRgn.Show()
			self.btnBig.Hide()
			self.btnSaveRgn.Show()
			self.btnVoid.Hide()
			self.btnExportRgn.Show()
			self.btnRevert.Hide()
			#self.btnCrop.Hide()
			self.btnSave.Show()
			self.overlayCbx.Enable( True )
		self.back.OnSize( None )
		self.Layout()
		self.Refresh()
		self.Thaw()

	def OnOverlay( self, event ):		
		self.Freeze()
		self.back.UpdateDrawing()	
		self.back.Refresh()
		self.Thaw()

	def OnZoomIn( self, event ):
		if self.zoomLevelPow > 0:
			self.zoomLevelPow -= 1
			self.zoomLevel = 2**self.zoomLevelPow
			self.back.SetVirtualSize( (self.region.imgSize[0]/self.zoomLevel,self.region.imgSize[1]/self.zoomLevel) )		
		if self.zoomLevelPow > 0:
			self.btnZoomIn.Enable( True )
		else:
			self.btnZoomIn.Enable( False )
		if self.zoomLevelPow < 4:
			self.btnZoomOut.Enable( True )
		else:
			self.btnZoomOut.Enable( False )
		self.back.OnSize(None)
		self.back.SetFocus()	
		
	def OnZoomOut( self, event ):
		if self.zoomLevelPow < 4 :
			self.zoomLevelPow += 1
			self.zoomLevel = 2**self.zoomLevelPow
			self.back.SetVirtualSize( (self.region.imgSize[0]/self.zoomLevel,self.region.imgSize[1]/self.zoomLevel) )		
		if self.zoomLevelPow > 0:
			self.btnZoomIn.Enable( True )
		else:
			self.btnZoomIn.Enable( False )
		if self.zoomLevelPow < 4:
			self.btnZoomOut.Enable( True )
		else:
			self.btnZoomOut.Enable( False )
		self.back.OnSize(None)
		self.back.SetFocus()	
	
	def OnMouseMove( self, event ):
		if self.btnEditMode.GetValue():
			if self.back.wait == True:
				pass
			elif self.editMode == EDITMODE_NONE:
				if event.Dragging() and self.back.crop != None:
					newpos = self.back.CalcUnscrolledPosition(event.GetX(), event.GetY())			
					newpos =  [ newpos[0]*self.zoomLevel,newpos[1]*self.zoomLevel ]
					newpos =  [ newpos[0]-self.back.offX,newpos[1]-self.back.offY ]
					newpos =  [ newpos[0]/64,newpos[1]/64 ]
					origin = [ newpos[0]*64+self.back.offX,newpos[1]*64+self.back.offY ]
					size = 64 + 1
					if origin[0] >= 0 and origin[1] >= 0 and origin[0]+size <= self.region.imgSize[0] and origin[1]+size <= self.region.imgSize[1] :				
						self.back.crop = [ self.back.crop[0], self.back.crop[1], newpos[0], newpos[1] ]
						print 'Crop', self.back.crop
						self.back.UpdateDrawing()
						self.back.wait = True
						self.back.Refresh( False )
				
			elif self.editMode == EDITMODE_VOID:
				newpos = self.back.CalcUnscrolledPosition(event.GetX(), event.GetY())			
				newpos =  [ newpos[0]*self.zoomLevel,newpos[1]*self.zoomLevel ]
				newpos =  [ newpos[0]-self.back.offX,newpos[1]-self.back.offY ]
				newpos =  [ newpos[0]/64,newpos[1]/64 ]
				self.back.HighlightCity( self.zoomLevel, self.region, newpos ) 
				self.back.wait = True
				self.back.Refresh( False )
			else:
				sizes = [0,1,2,4]
				newpos = self.back.CalcUnscrolledPosition(event.GetX(), event.GetY())
				newpos =  [ newpos[0]*self.zoomLevel,newpos[1]*self.zoomLevel ]
				newpos =  [ newpos[0]-self.back.offX,newpos[1]-self.back.offY ]
				newpos =  [ newpos[0]/64,newpos[1]/64 ]
				
				origin = [ newpos[0]*64+self.back.offX,newpos[1]*64+self.back.offY ]
				size = sizes[ self.editMode ]*64 + 1
				if origin[0] + size > self.region.imgSize[0]:
					origin[0] = self.region.imgSize[0]-size
					newpos[0] = (origin[0]-self.back.offX)/64
				if origin[1] + size > self.region.imgSize[1]:
					origin[1] = self.region.imgSize[1]-size
					newpos[1] = (origin[1]-self.back.offY)/64
					
				if origin[0] >= 0 and origin[1] >= 0 and origin[0]+size <= self.region.imgSize[0] and origin[1]+size <= self.region.imgSize[1] :				
					self.back.HighlightNewCity( self.zoomLevel, self.region, newpos, sizes[self.editMode] )
					
				self.back.wait = True
				self.back.Refresh( False )

	def OnLeftDown( self, event ):
		if self.btnEditMode.GetValue() and self.editMode == EDITMODE_NONE and event.controlDown:		
			newSize = (int(self.region.imgSize[0]/self.zoomLevel),int(self.region.imgSize[1]/self.zoomLevel) )
			newpos = self.back.CalcUnscrolledPosition(event.GetX(), event.GetY())
			newpos =  [ newpos[0]*self.zoomLevel,newpos[1]*self.zoomLevel ]
			newpos =  [ newpos[0]-self.back.offX,newpos[1]-self.back.offY ]
			newpos =  [ newpos[0]/64,newpos[1]/64 ]
			origin = [ newpos[0]*64+self.back.offX,newpos[1]*64+self.back.offY ]
			size = 64 + 1
			if origin[0] >= 0 and origin[1] >= 0 and origin[0]+size <= self.region.imgSize[0] and origin[1]+size <= self.region.imgSize[1] :								
				self.back.crop = [ newpos[0], newpos[1], newpos[0], newpos[1] ]
			
	def OnLeftUp( self, event ):
		if self.btnEditMode.GetValue():
			newSize = (int(self.region.imgSize[0]/self.zoomLevel),int(self.region.imgSize[1]/self.zoomLevel) )
			newpos = self.back.CalcUnscrolledPosition(event.GetX(), event.GetY())
			newpos =  [ newpos[0]*self.zoomLevel,newpos[1]*self.zoomLevel ]
			newpos =  [ newpos[0]-self.back.offX,newpos[1]-self.back.offY ]
			newpos =  [ newpos[0]/64,newpos[1]/64 ]

			if self.editMode == EDITMODE_NONE:		
				if self.back.crop != None:				
					crop = [ min( self.back.crop[0],self.back.crop[2] ), min( self.back.crop[1],self.back.crop[3] ), max( self.back.crop[0],self.back.crop[2] ), max( self.back.crop[1],self.back.crop[3] ) ]
					configSize = ( crop[2]-crop[0]+1, crop[3]-crop[1]+1 )
					config = rgnReader.BuildBestConfig( configSize )
					self.region.config.paste( '#000000', ( 0,0, self.region.config.size[0], self.region.config.size[1] ))
					self.region.config.paste( config, (crop[0],crop[1] ) )
					self.region.allCities = rgnReader.WorkTheconfig( self.region.config, self.region.waterLevel )
					self.region.config =self.region.BuildConfig()
				self.back.crop = None
			elif self.editMode == EDITMODE_VOID:
				self.region.DeleteCityAt( newpos )
			else: 
				sizes = [0,1,2,4]
				origin = [ newpos[0]*64+self.back.offX,newpos[1]*64+self.back.offY ]
				size = sizes[ self.editMode ]*64 + 1
				if origin[0] + size > self.region.imgSize[0]:
					origin[0] = self.region.imgSize[0]-size
					newpos[0] = (origin[0]-self.back.offX)/64
				if origin[1] + size > self.region.imgSize[1]:
					origin[1] = self.region.imgSize[1]-size
					newpos[1] = (origin[1]-self.back.offY)/64
					
				if origin[0] >= 0 and origin[1] >= 0 and origin[0]+size <= self.region.imgSize[0] and origin[1]+size <= self.region.imgSize[1] :				
					currentSize = sizes[ self.editMode ]
					done = False
					print 'start split'
					while not done:				
						done = True
						cities = self.region.GetCitiesUnder( newpos, currentSize )
						for city in cities:
							if city.cityXSize == 1:
								self.region.allCities.remove( city )
							else:
								done = False
								newCities = city.Split()
								self.region.allCities.remove( city )
								for c in newCities:
									self.region.allCities.append( c )
					print 'end split'
					self.region.allCities.append( rgnReader.CityProxy( 250.0, newpos[0],newpos[1], currentSize,currentSize) )
			print 'start build'
			self.region.config = self.region.BuildConfig()
			print 'end build'
			self.back.UpdateDrawing()
			self.back.wait = True
			self.back.Refresh( False )
				
	  
	def SaveBmp( self,event ):
		dlg = wx.FileDialog(
			self, message="Save file as ...", defaultDir=os.getcwd(), 
			defaultFile="", wildcard="PNG file (*.png)|*.png|""Jpeg file (*.jpg)|*.jpg|""Bitmap file (*.bmp)|*.bmp", style=wx.FD_SAVE
			)
		if dlg.ShowModal() == wx.ID_OK:
			wx.BeginBusyCursor()
			path = dlg.GetPath()

			lightDir = rgnReader.Normalize( (1, -5, -1) )
			s = (self.region.height.shape[1],self.region.height.shape[0])
			xO = yO = 0
			colours = [ 0, "#FF0000", "#00FF00", 0, "#0000FF" ]
			sizes = [ 0,64,128,0,256 ]

			dlgProg = wx.ProgressDialog("Saving overview",
							   "Please wait while saving overview",
							   maximum = len( self.region.allCities ) + len( self.region.missingCities ) + 10,
							   parent=self,
							   style = 0 )
				
			im = Image.new( "RGB", (self.region.imgSize[0],self.region.imgSize[1]) )
			for i,city in enumerate( self.region.allCities ):
				dlgProg.Update( i, "Please wait while saving overview" )
				x = int( city.xPos )
				y = int( city.yPos )
				width = sizes[city.cityXSize]+1
				height = sizes[city.cityYSize]+1
				x1 = x-xO+self.back.offX
				y1 = y-yO+self.back.offY
				x2 = x1+width
				y2 = y1+height
				
				h = Numeric.zeros( (height, width), Numeric.uint16 )
				h[:,:] = Numeric.reshape( self.region.height[ y1:y2, x1:x2 ], (height,width ) )
				h = h.astype( Numeric.float32 )
				h /= Numeric.array( 10 ).astype( Numeric.float32 )
				rawRGB = tools3D.onePassColors( False, (height,width ), self.region.waterLevel, h, rgnReader.GradientReader.paletteWater, rgnReader.GradientReader.paletteLand, lightDir )
				del h
				imCity = Image.fromstring( "RGB", (width,height ), rawRGB )
				del rawRGB
				im.paste( imCity, (x1,y1 ) )
				#imCity.save( "%d-%d.png"%(x,y) )
				del imCity
				
			if self.overlayCbx.GetValue():
				draw = ImageDraw.Draw(im)
				def DrawHided( x, y, width, height ):
					x1 = x
					y1 = y
					x2 = x1+width
					y2 = y1+height
					h = Numeric.zeros( (height, width), Numeric.uint16)
					h[:,:] = Numeric.reshape( self.region.height[ y1:y2, x1:x2 ], (height,width ) )
					h = h.astype( Numeric.float32 )
					h /= Numeric.array( 10 ).astype( Numeric.float32 )
					rawRGB = tools3D.onePassColors( False, (height,width ), self.region.waterLevel, h, rgnReader.GradientReader.paletteWater, rgnReader.GradientReader.paletteLand, lightDir )
					del h
					imCity = Image.fromstring( "RGB", (width,height ), rawRGB ).convert("L").convert("RGB" )
					del rawRGB
					im.paste( imCity, (x1,y1 ) )
					del imCity
				if self.back.offX > 0:
					i+=1
					dlgProg.Update( i, "Please wait while saving overview" )
					width = self.back.offX
					height = self.region.imgSize[1]
					x = 0
					y = 0
					DrawHided( x, y, width, height)
					x1 = x
					y1 = y
					x2 = x1+width
					y2 = y1+height
					h = Numeric.zeros( (height, width), Numeric.uint16)
					h[:,:] = Numeric.reshape( self.region.height[ y1:y2, x1:x2 ], (height,width ) )
					h = h.astype( Numeric.float32 )
					h /= Numeric.array( 10 ).astype( Numeric.float32 )
					rawRGB = tools3D.onePassColors( False, (height,width ), self.region.waterLevel, h, rgnReader.GradientReader.paletteWater, rgnReader.GradientReader.paletteLand, lightDir )
					del h
					imCity = Image.fromstring( "RGB", (width,height ), rawRGB ).convert("L").convert("RGB" )
					del rawRGB
					im.paste( imCity, (x1,y1 ) )
					del imCity
				if self.back.offY > 0:
					i+=1
					dlgProg.Update( i, "Please wait while saving overview" )
					width = self.back.imgSize[0]
					height = self.back.offY
					x = 0
					y = 0
					DrawHided( x, y, width, height)
				if self.back.offX < 0:
					i+=1
					dlgProg.Update( i, "Please wait while saving overview" )
					width = -self.back.offX
					height = self.region.imgSize[1]
					x = self.region.imgSize[0]+self.back.offX
					y = 0
					DrawHided( x, y, width, height)
				if self.back.offY < 0:
					i+=1
					dlgProg.Update( i, "Please wait while saving overview" )
					width = self.region.imgSize[0]
					height = -self.back.offY
					x = 0
					y = self.region.imgSize[1]+self.back.offY
					DrawHided( x, y, width, height)
				lines=[]
				
				for y in xrange( s[1]/int(64) ):
					lines.append( [ 0-xO,y*int(64)-yO,self.region.originalConfig.size[0]*int(64)-xO,y*int(64)-yO ] )
				for x in xrange( s[0]/int(64) ):
					lines.append( [ x*int(64)-xO,0-yO,x*int(64)-xO,self.region.originalConfig.size[1]*int(64)-yO ] )
				for x1,y1,x2,y2 in lines:
					draw.line( [ x1+self.back.offX,y1+self.back.offY,x2+self.back.offX,y2+self.back.offY ], fill = "#222222" )

				for city in self.region.allCities:
					x = int( city.xPos )
					y = int( city.yPos )
					width = sizes[city.cityXSize]
					height = sizes[city.cityYSize]
					#draw.rectangle( [x-xO+self.back.offX,y-yO+self.back.offY,x-xO+width+self.back.offX,y-yO+height+self.back.offY], outline = colours[city.cityXSize] )
					draw.rectangle( [x-xO+1+self.back.offX,y-yO+1+self.back.offY,x-xO+width-1+self.back.offX,y-yO+height-1+self.back.offY], outline = colours[city.cityXSize] )
				for x,y in self.region.missingCities:
					i+=1
					dlgProg.Update( i, "Please wait while saving overview" )
				
					width = 65
					height = 65
					x = int( x*64 )
					y = int( y*64 )
					x1 = x-xO+self.back.offX
					y1 = y-yO+self.back.offY
					x2 = x-xO+width+self.back.offX
					y2 =y-yO+height+self.back.offY
					if x1<0:
						x1=0
					if y1<0:
						y1=0
					if x2<0:
						x2=0
					if y2<0:
						y2=0
					if x1>self.region.imgSize[0]:
						x1=self.region.imgSize[0]
					if y1>self.region.imgSize[1]:
						y1=self.region.imgSize[1]
					if x2>self.region.imgSize[0]:
						x2=self.region.imgSize[0]
					if y2>self.region.imgSize[1]:
						y2=self.region.imgSize[1]
					width = x2-x1
					height = y2-y1
					if width <= 0 or height <= 0:
						continue
					h = Numeric.zeros( (height, width), Numeric.uint16 )
					h[:,:] = Numeric.reshape( self.region.height[ y1:y2, x1:x2 ], (height, width) )
					h = h.astype( Numeric.float32 )
					h /= Numeric.array( 10 ).astype( Numeric.float32 )
					rawRGB = tools3D.onePassColors( False, (height,width ), self.region.waterLevel, h, rgnReader.GradientReader.paletteWater, rgnReader.GradientReader.paletteLand, lightDir )
					imCity = Image.fromstring( "RGB", (width,height ), rawRGB ).convert("L").convert("RGB" )
					del rawRGB
					im.paste( imCity, (x1,y1 ) )
					del imCity

			
			im.save( path )
			#del im
			dlgProg.Close()
			dlgProg.Destroy()
			wx.EndBusyCursor()
	  
		
	def CreateRgn( self, event ):
		result = QuestionDialog.questionDialog( 'Do you want to create a region from ?', buttons =["SC4M","Grayscale image","16 bit png","RGB image",wx.ID_CANCEL ] ) 
		if result == wx.ID_CANCEL or result == None:
			return
		self.btnEditMode.Enable( False )
		if result == 'SC4M':
			self.CreateRgnFromSC4M()             
		if result == 'Grayscale image':
			self.CreateRgnFromGrey()             
		if result == '16 bit png':
			self.CreateRgnFromPNG()             
		if result == 'RGB image':
			self.CreateRgnFromRGB()             
			
	def CreateRgnInit( self ):
		self.btnSave.Enable( False )
		self.btnExportRgn.Enable( False )
		self.btnSaveRgn.Enable( False )
		self.region = None
		
		self.back.SetVirtualSize((100,100))
		self.zoomLevel = 1
		self.zoomLevelPow = 0
		
		self.SetTitle( "NHP SC4Mapper %s Version "%MAPPER_VERSION )

		
	def CreateRgnOk( self ):
		self.btnSave.Enable( True )
		self.btnSaveRgn.Enable( True )
		self.btnExportRgn.Enable( True )
		self.SetTitle( "NHP SC4Mapper %s Version - "%MAPPER_VERSION+self.regionName )
		self.btnZoomIn.Enable( False )
		self.btnZoomOut.Enable( True )
		self.overlayCbx.Enable( True )
		self.back.offX = 0
		self.back.offY = 0
		self.back.OnSize(None)		

	def CreateRgnFromSC4M( self ):
		self.CreateRgnInit()
		dlg = wx.FileDialog(
			self, message="Choose a SC4M file", defaultDir=os.getcwd(), 
			defaultFile="", wildcard= "SC4Terraform exported (*.SC4M)|*.SC4M"
			, style=wx.OPEN  
			)
		if dlg.ShowModal() == wx.ID_OK:
		  paths = dlg.GetPaths()[0]
		  dlg.Destroy()
		else:
		  dlg.Destroy()
		  return
		sc4mFile = paths
		name = os.path.split( sc4mFile )[1]
		name = os.path.splitext( name )[0]
		
		wx.BeginBusyCursor()			
				
		try:
			raw = open( sc4mFile,"rb" )            			
			zipped = zipUtils.ZipInputStream( raw )
			s = zipped.read( 4 )
			if s != "SC4M":
			  raise IOError,"SC4M"
			version = struct.unpack( "L", zipped.read(4) )[0]
			if version != 0x0200:
			  raise IOError,"Version"
			ySize = struct.unpack( "L", zipped.read(4) )[0]
			xSize = struct.unpack( "L", zipped.read(4) )[0]
			mini = struct.unpack( "f", zipped.read(4) )[0]
			temp = zipped.read(4)
			print temp
			if temp == "SC4N":			  
				lenHtml = struct.unpack( "L", zipped.read(4) )[0]
				if lenHtml:
					htmlText = zipped.read(lenHtml)
					os.chdir( os.path.split( sc4mFile )[0] )
					try:
						authorNotes = about.AuthorBox(self,htmlText)
						wx.EndBusyCursor()
						authorNotes.ShowModal()
						wx.BeginBusyCursor()
						authorNotes.Destroy()
					except:
						pass
					os.chdir( sys.path[0] )
				temp = zipped.read(4)
				print temp
			if temp == 'SC4C':			  
			  configSize = struct.unpack( "LL", zipped.read(8) )
			  lenstring = struct.unpack( "L", zipped.read(4) )[0]
			  imString = zipped.read( lenstring )
			  config = Image.fromstring( "RGB", configSize, imString )
			  temp = zipped.read(4)
			  print 'config',temp
			if temp != "SC4D":
			  raise IOError,"SC4D"
			r = Numeric.fromstring( zipped.read( xSize*ySize ), Numeric.uint8 )
			rH = Numeric.fromstring( zipped.read( xSize*ySize ), Numeric.uint8 )
			raw.close()
			zipped = None
			r = r.astype( Numeric.uint16 )
			rH = rH.astype( Numeric.uint16 )
			rH *= Numeric.array( 256 ).astype( Numeric.uint16 )
			r += rH
			del rH

			class dlgstub:
				def __init__( self ):
					pass
				def Update( self, x, y ):
					pass
			NewRegion = rgnReader.SC4Region( None,250, dlgstub(), config )
			NewRegion.show( dlgstub() )
		except IOError,msg:
			wx.EndBusyCursor()			
			print msg
			dlg1 = wx.MessageDialog(self, sc4mFile + ' seems not to be a valid image file',
			 'Region creation error',
			 wx.OK | wx.ICON_ERROR
			 )
			dlg1.ShowModal()
			dlg1.Destroy()
			return
		
		self.regionName = name    
		self.region = NewRegion;
		self.region.height = Numeric.reshape( r, self.region.shape )
		del r
		self.zoomLevel = 1
		self.zoomLevelPow = 0
		self.back.SetVirtualSize((self.region.height.shape[1],self.region.height.shape[0]))
		self.SetFocus()
		self.CreateRgnOk()
		self.btnEditMode.Enable( True )
		wx.EndBusyCursor()			
				  
		
	def CreateRgnFromGrey( self ):
		self.CreateRgnInit()
		dlg = CreateRgnFromFile( self, "8-bit Greyscale", "All graphics file |*.jpeg;*.jpg;*.png;*.bmp|" "Jpeg file (*.jpeg;*.jpg)|*.jpeg;*.jpg|""Bitmap file (*.bmp)|*.bmp", True )
		ret = dlg.ShowModal()
		
		if ret == wx.ID_OK:
			paths = dlg.fileName.GetValue()
			configName = dlg.configFileName.GetValue()
			configSize = ( dlg.sizeX.GetValue(),dlg.sizeY.GetValue() )
			fromConfig = dlg.fromConfig.GetValue()
			scale = dlg.GetImageFactor()
			dlg.Destroy()
		else:
			
			dlg.Destroy()
			return
		
		wx.BeginBusyCursor()	
		name = os.path.split( paths )[1]
		name = os.path.splitext( name )[0]
		
		im = Image.open(  paths )
		if not( im.size[0] == configSize[0]*64+1 and im.size[1] == configSize[1]*64+1) : 
		  dlg1 = wx.MessageDialog(self, paths + ' has not correct dimensions\n'+'It should be (%d by %d) but it is (%d by %d)\nDo you want to resize the image to fit region dimensions?'%(configSize[0]*64+1,configSize[1]*64+1,im.size[0],im.size[1]),
		   'Import warning',
		   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
		   )
		  res = dlg1.ShowModal()
		  dlg1.Destroy()
		  if res == wx.ID_YES:            
			im = im.resize( (configSize[0]*64+1, configSize[1]*64+1),Image.BICUBIC )
		  else:
			return          
		if im.mode != "L":
		  im = im.convert( "L" )

		r = Numeric.fromstring( im.tostring(), Numeric.uint8 )
		r = Numeric.asarray( r, Numeric.float32 )
		r *= Numeric.array(10*scale).astype(Numeric.float32)
		r = Numeric.asarray( r, Numeric.uint16 )
		
		if fromConfig:
		  config = Image.open( configName )
		else:
		  config = rgnReader.BuildBestConfig( configSize ) #Image.new( "RGB", configSize, "#FF0000" )

		class dlgstub:
			def __init__( self ):
				pass
			def Update( self, x, y ):
				pass

		try:        
		  NewRegion = rgnReader.SC4Region( None,250, dlgstub(), config )
		  NewRegion.show( dlgstub() )
		except AssertionError:
			wx.EndBusyCursor()	
			dlg1 = wx.MessageDialog(self, configName + ' seems not to be a valid config.bmp',
			 'Region creation error',
			 wx.OK | wx.ICON_ERROR
			 )
			dlg1.ShowModal()
			dlg1.Destroy()
			return
				  
		self.regionName = name    
		self.region = NewRegion;
		self.region.height = Numeric.reshape( r, self.region.shape )
		del r
		self.zoomLevel = 1
		self.zoomLevelPow = 0
		self.back.SetVirtualSize((self.region.height.shape[1],self.region.height.shape[0]))
		self.SetFocus()
		self.CreateRgnOk()
		self.btnEditMode.Enable( True )
		wx.EndBusyCursor()		   
		
	def CreateRgnFromPNG( self ):
		self.CreateRgnInit()
		dlg = CreateRgnFromFile( self, "16-bit PNG", "PNG File |*.png" )
		ret = dlg.ShowModal()
		paths = dlg.fileName.GetValue()
		configName = dlg.configFileName.GetValue()
		configSize = ( dlg.sizeX.GetValue(),dlg.sizeY.GetValue() )
		fromConfig = dlg.fromConfig.GetValue()
		dlg.Destroy()
		if ret == wx.ID_CANCEL:
		  return

		name = os.path.split( paths )[1]
		name = os.path.splitext( name )[0]
		
		im = Image.open( paths )
		if not( im.size[0] == configSize[0]*64+1 and im.size[1] == configSize[1]*64+1) : 
		  dlg1 = wx.MessageDialog(self, paths + ' has not correct dimensions\n'+'It should be (%d by %d) but it is (%d by %d)\nDo you want to resize the image to fit region dimensions?'%(configSize[0]*64+1,configSize[1]*64+1,im.size[0],im.size[1]),
		   'Import warning',
		   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
		   )
		  res = dlg1.ShowModal()
		  dlg1.Destroy()
		  if res == wx.ID_YES:            
			im = im.resize( (configSize[0]*64+1, configSize[1]*64+1),Image.BICUBIC )
		  else:
			return          
		if im.mode != "I":
			dlg1 = wx.MessageDialog(self, configName + ' seems not to be a valid 16 bit grescale image',
			 'Region creation error',
			 wx.OK | wx.ICON_ERROR
			 )
			dlg1.ShowModal()
			dlg1.Destroy()
			return

		dlgProg = wx.ProgressDialog("Loading PNG",
							   "Please wait while loading the region",
							   maximum = configSize[1]*configSize[0]+10,
							   parent=self,
							   style = 0 )
		  
		wx.BeginBusyCursor()	
		heights = Numeric.zeros( ( configSize[1]*64+1,configSize[0]*64+1), Numeric.uint16 )
		i = 0
		for y in xrange( configSize[1] ):
			for x in xrange( configSize[0] ):
				i += 1
				dlgProg.Update( i, "Please wait while loading the region" )
				imSmall = im.crop( (x*64,y*64,x*64+65,y*64+65) )
				r = Numeric.fromstring( imSmall.tostring(), Numeric.int32 )
				r = Numeric.reshape( r, ( 64+1,64+1 ) )                          
				r = r.astype(Numeric.uint16)
				heights[ y*64:y*64+65,x*64:x*64+65 ] = r
				del r
				del imSmall
				
		
		dlgProg.Close()
		dlgProg.Destroy()        
		self.Refresh()
		wx.Yield()
		
		if fromConfig:
		  config = Image.open( configName )
		else:
		  config = rgnReader.BuildBestConfig( configSize )#Image.new( "RGB", configSize, "#FF0000" )

		class dlgstub:
			def __init__( self ):
				pass
			def Update( self, x, y ):
				pass

		try:        
		  NewRegion = rgnReader.SC4Region( None,250, dlgstub(), config )
		  NewRegion.show( dlgstub() )
		except AssertionError:
			wx.EndBusyCursor()	
			dlg1 = wx.MessageDialog(self, configName + ' seems not to be a valid config.bmp',
			 'Region creation error',
			 wx.OK | wx.ICON_ERROR
			 )
			dlg1.ShowModal()
			dlg1.Destroy()
			return
				  
		self.regionName = name    
		self.region = NewRegion;
		self.region.height = Numeric.reshape( heights, self.region.shape )
		del heights
		self.zoomLevel = 1
		self.zoomLevelPow = 0
		self.back.SetVirtualSize((self.region.height.shape[1],self.region.height.shape[0]))
		self.SetFocus()
		self.CreateRgnOk()
		self.btnEditMode.Enable( True )
		wx.EndBusyCursor()	
		
	def CreateRgnFromRGB( self ):
		self.CreateRgnInit()
		dlg = CreateRgnFromFile( self, "RGB", "RGB File |*.png;*.bmp;*.jpg" )
		ret = dlg.ShowModal()
		paths = dlg.fileName.GetValue()
		configName = dlg.configFileName.GetValue()
		configSize = ( dlg.sizeX.GetValue(),dlg.sizeY.GetValue() )
		fromConfig = dlg.fromConfig.GetValue()
		dlg.Destroy()
		if ret == wx.ID_CANCEL:
		  return

		name = os.path.split( paths )[1]
		name = os.path.splitext( name )[0]
		
		resized = False
		im = Image.open( paths )
		if not( im.size[0] == configSize[0]*64+1 and im.size[1] == configSize[1]*64+1) : 
		  dlg1 = wx.MessageDialog(self, paths + ' has not correct dimensions\n'+'It should be (%d by %d) but it is (%d by %d)\nDo you want to resize the image to fit region dimensions?'%(configSize[0]*64+1,configSize[1]*64+1,im.size[0],im.size[1]),
		   'Import warning',
		   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
		   )
		  res = dlg1.ShowModal()
		  dlg1.Destroy()
		  if res == wx.ID_YES:            
			im = im.resize( (configSize[0]*64+1, configSize[1]*64+1),Image.NEAREST )
			resized = True
		  else:
			return          
		if im.mode != "RGB":
			dlg1 = wx.MessageDialog(self, configName + ' seems not to be a valid RGB image',
			 'Region creation error',
			 wx.OK | wx.ICON_ERROR
			 )
			dlg1.ShowModal()
			dlg1.Destroy()
			return
		  
		dlgProg = wx.ProgressDialog("Loading RGB",
							   "Please wait while loading the region",
							   maximum = configSize[1]*configSize[0]+10,
							   parent=self,
							   style = 0 )
		  
		wx.BeginBusyCursor()	
		heights = Numeric.zeros( ( configSize[1]*64+1,configSize[0]*64+1), Numeric.uint16 )
		print 'size',heights.shape
		i = 0
		print im.tile
		for y in xrange( configSize[1] ):
			subIm = None
			if resized == False and len( im.tile ) == 1 and im.tile[0][0] == 'raw':
				subIm = Image.open( paths )
				subIm.size = ( subIm.size[0], 65 )
				d, e, o, a = subIm.tile[0]
				subIm.tile = [( d, ( 0, 0, subIm.size[0], 65 ), o+(configSize[1]-y-1)*64*a[1], a )]
				
			for x in xrange( configSize[0] ):
				i += 1
				dlgProg.Update( i, "Please wait while loading the region" )
				if subIm == None:
					imSmall = im.crop( (x*64,y*64,x*64+65,y*64+65) )
				else:
					try:
						imSmall = subIm.crop( (x*64,0,x*64+65,65) )
					except:
						print x,y,[( d, ( 0, 0, subIm.size[0], 65 ), o+(configSize[1]-y-1)*64*a[1], a )], 65*a[1]
						raise
				r = Numeric.fromstring( imSmall.tostring(), Numeric.uint8 )
				r = Numeric.reshape( r, ( 64+1,64+1,3) )                          
				#r = r.astype(Numeric.uint16)
				red = r[:,:,0].astype( Numeric.uint16 )*Numeric.array( 4096/16, Numeric.uint16 )
				green = r[:,:,1].astype( Numeric.uint16 )*Numeric.array( 256/16, Numeric.uint16 )
				blue = r[:,:,2].astype( Numeric.uint16 )
				r = red
				r += green
				r += blue                          
				#r = r.astype( Numeric.uint16 )
				heights[ y*64:y*64+65,x*64:x*64+65 ] = r
				del red
				del green
				del blue
				del r
				del imSmall
				
		
		dlgProg.Close()
		dlgProg.Destroy()        
		self.Refresh()
		wx.Yield()
		
		if fromConfig:
		  config = Image.open( configName )
		else:
		  config = rgnReader.BuildBestConfig( configSize ) #Image.new( "RGB", configSize, "#FF0000" )

		class dlgstub:
			def __init__( self ):
				pass
			def Update( self, x, y ):
				print x, y
				pass

		try:        
		  NewRegion = rgnReader.SC4Region( None,250, dlgstub(), config )
		  NewRegion.show( dlgstub() )
		except AssertionError:
			wx.EndBusyCursor()	
			dlg1 = wx.MessageDialog(self, configName + ' seems not to be a valid config.bmp',
			 'Region creation error',
			 wx.OK | wx.ICON_ERROR
			 )
			dlg1.ShowModal()
			dlg1.Destroy()
			return
				  
		self.regionName = name    
		self.region = NewRegion;
		self.region.height = heights
		del heights
		self.zoomLevel = 1
		self.zoomLevelPow = 0
		self.back.SetVirtualSize((self.region.height.shape[1],self.region.height.shape[0]))
		self.SetFocus()
		self.CreateRgnOk()
		self.btnEditMode.Enable( True )
		wx.EndBusyCursor()	


	def ExportAsRGB( self, path, config, minX, minY, subRgn ):
		if os.path.isfile( path ):
		  dlg = wx.MessageDialog( self, path+" already exist\nOverwrite it ?","SC4Mapper",wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION )
		  ret = dlg.ShowModal()
		  dlg.Destroy()
		  if ret == wx.NO:
			return
			
		wx.BeginBusyCursor()	
		im = Image.new( "RGB", (config.size[0]*64+1,config.size[1]*64+1) )
		dlgProg = wx.ProgressDialog("Exporting as RGB",
							   "Please wait while exporting the region",
							   maximum = len( self.region.allCities ),
							   parent=self,
							   style = 0 )
		for i,city in enumerate( self.region.allCities ):
			dlgProg.Update(i,"Please wait while exporting the region" );
			citySave = rgnReader.CityProxy( self.region.waterLevel, city.cityXPos-minX, city.cityYPos-minY, city.cityXSize, city.cityYSize )
			heightMap = Numeric.zeros( (citySave.ySize, citySave.xSize), Numeric.uint16 )
			heightMap[::,::] =  self.region.height[ citySave.yPos+subRgn[1]:citySave.yPos+subRgn[1]+citySave.ySize,citySave.xPos+subRgn[0]:citySave.xPos+subRgn[0]+citySave.xSize ]	  
			red = ( (heightMap / Numeric.array(4096, Numeric.uint16) ) % Numeric.array(16, Numeric.uint16) )*Numeric.array(16, Numeric.uint16)
			red = red.astype( Numeric.uint8 )
			imRed = Image.fromstring( "L", ( heightMap.shape[1],heightMap.shape[0]), red.tostring() )
			green = ( (heightMap / Numeric.array(256, Numeric.uint16) ) % Numeric.array(16, Numeric.uint16) )*Numeric.array(16, Numeric.uint16)
			green = green.astype( Numeric.uint8 )
			imGreen = Image.fromstring( "L", ( heightMap.shape[1],heightMap.shape[0]), green.tostring() )
			blue = heightMap % Numeric.array(256, Numeric.uint16)
			blue = blue.astype( Numeric.uint8 )
			imBlue = Image.fromstring( "L", ( heightMap.shape[1],heightMap.shape[0]), blue.tostring() )
			imCity = Image.merge( "RGB", ( imRed, imGreen, imBlue ) )
			im.paste( imCity, ( citySave.xPos,citySave.yPos ) )
		dlgProg.Close()
		dlgProg.Destroy()
		self.Refresh()
		wx.Yield()
		
		try:
			im.save( path )
			pathCfg = os.path.splitext( path )[0]
			pathCfg += u"-config.bmp"
			config.save( pathCfg )
		except:
			wx.EndBusyCursor()	
			dlg1 = wx.MessageDialog(self, path + " can't be saved",
												'Export error',
									wx.OK | wx.ICON_ERROR
									)
			dlg1.ShowModal()
			dlg1.Destroy()
			return
		wx.EndBusyCursor()	
		wx.CallAfter( self.ShowSuccess, path )

	def ExportAsPNG( self, path, config, minX, minY, subRgn ):
		if os.path.isfile( path ):
		  dlg = wx.MessageDialog( self, path+" already exist\nOverwrite it?","SC4Mapper",wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION )
		  ret = dlg.ShowModal()
		  dlg.Destroy()
		  if ret == wx.NO:
			return
		wx.BeginBusyCursor()	
		
		im = Image.new( "I", (config.size[0]*64+1,config.size[1]*64+1) )
		dlgProg = wx.ProgressDialog("Exporting as PNG",
							   "Please wait while exporting the region",
							   maximum = len( self.region.allCities ),
							   parent=self,
							   style = 0 )
		for i,city in enumerate( self.region.allCities ):
			dlgProg.Update(i,"Please wait while exporting the region" );
			citySave = rgnReader.CityProxy( self.region.waterLevel, city.cityXPos-minX, city.cityYPos-minY, city.cityXSize, city.cityYSize )
			heightMap = Numeric.zeros( (citySave.ySize, citySave.xSize), Numeric.uint16 )
			heightMap[::,::] =  self.region.height[ citySave.yPos+subRgn[1]:citySave.yPos+subRgn[1]+citySave.ySize,citySave.xPos+subRgn[0]:citySave.xPos+subRgn[0]+citySave.xSize ]	  
			#heightMap *= Numeric.array( 10 ).astype( Numeric.float32 )	
			heightMap = heightMap.astype( Numeric.int32 )
			imCity = Image.fromstring( "I", ( heightMap.shape[1],heightMap.shape[0]), heightMap.tostring() )
			im.paste( imCity, ( citySave.xPos,citySave.yPos ) )
		dlgProg.Close()
		dlgProg.Destroy()
		self.Refresh()
		wx.Yield()
		try:
			im.save( path )
			pathCfg = os.path.splitext( path )[0]
			pathCfg += u"-config.bmp"			
			config.save( pathCfg )
		except:
			wx.EndBusyCursor()	
			dlg1 = wx.MessageDialog(self, path + " can't be saved",
												 'Export error',
									wx.OK | wx.ICON_ERROR
									)
			dlg1.ShowModal()
			dlg1.Destroy()
			return
		del im
		wx.EndBusyCursor()	
		wx.CallAfter( self.ShowSuccess, path )
		
	def ShowSuccess( self, path ):
		dlg1 = wx.MessageDialog(self, path + ' as been exported',
											'Export done',
								wx.OK | wx.ICON_INFORMATION
								)
		dlg1.ShowModal()
		dlg1.Destroy()
	
	def ExportAsSC4M( self, path, config, minX, minY, subRgn ):
		if os.path.isfile( path ):
		  dlg = wx.MessageDialog( self, path+" already exist\nOverwrite it ?","SC4Mapper",wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION )
		  ret = dlg.ShowModal()
		  dlg.Destroy()
		  if ret == wx.NO:
			return
			
		
		dlg1 = wx.FileDialog( self, message="Enter a valid hml file that will be displayed on import", defaultDir=os.getcwd(), defaultFile="", wildcard="HTML files (*.HTML)|*.html", style=wx.OPEN )
		if dlg1.ShowModal() == wx.ID_OK:
		  htmlFileName = dlg1.GetPaths()[0]           
		else:
		  htmlFileName = None
		dlg1.Destroy()

		
		wx.BeginBusyCursor()	
		
		dlgProg = wx.ProgressDialog("Exporting as SC4M",
							   "Please wait while exporting the region",
							   maximum = len( self.region.allCities ),
							   parent=self,
							   style = 0 )
		im1 = Image.new( "L", (config.size[0]*64+1,config.size[1]*64+1) )
		im2 = Image.new( "L", (config.size[0]*64+1,config.size[1]*64+1) )
		for i,city in enumerate( self.region.allCities ):
			dlgProg.Update(i,"Please wait while exporting the region" );
			citySave = rgnReader.CityProxy( self.region.waterLevel, city.cityXPos-minX, city.cityYPos-minY, city.cityXSize, city.cityYSize )
			heightMap = Numeric.zeros( (citySave.ySize, citySave.xSize), Numeric.uint16 )
			heightMap[::,::] =  self.region.height[ citySave.yPos+subRgn[1]:citySave.yPos+subRgn[1]+citySave.ySize,citySave.xPos+subRgn[0]:citySave.xPos+subRgn[0]+citySave.xSize ]	  
			#heightMap *= Numeric.array( 10 ).astype( Numeric.float32 )	
			heightMap = heightMap.astype( Numeric.int32 )
			imCity = Image.fromstring( "RGBA", ( heightMap.shape[1],heightMap.shape[0]), heightMap.tostring() )
			imCity1,imCity2 = imCity.split()[:2]
			im1.paste( imCity1, ( citySave.xPos,citySave.yPos ) )
			im2.paste( imCity2, ( citySave.xPos,citySave.yPos ) )
		dlgProg.Close()
		dlgProg.Destroy()
		self.Refresh()
		wx.Yield()
		
		s = "SC4M"        
		s += struct.pack( "L",0x0200 )
		s += struct.pack( "L",im1.size[1] )        
		s += struct.pack( "L",im1.size[0] ) 
		s += struct.pack( "f",0 )
		if htmlFileName is not None and os.path.isfile( htmlFileName ):
		  s += "SC4N" # author notes
		  filehtml = open( htmlFileName )
		  lines = filehtml.readlines()
		  line = "\n".join( lines )
		  filehtml.close()
		  s += struct.pack( "L", len( line ) )
		  s += line
		s += "SC4C"         # config.bmp included
		s += struct.pack( "L", config.size[0] )
		s += struct.pack( "L", config.size[1] )
		configStr = config.tostring()
		s += struct.pack( "L", len( configStr ) )
		s += configStr
		s += "SC4D" # elevation data
		try:              
			encoder = zlib.compressobj(9)
			raw = open(  path ,"wb" )            		
			raw.write( encoder.compress( s ) )
			raw.write( encoder.compress( im1.tostring() ) )
			del im1
			raw.write( encoder.compress( im2.tostring() ) )
			del im2
			raw.write( encoder.flush() )
			raw.close()
			pathCfg = os.path.splitext( path )[0]
			pathCfg += u"-config.bmp"
			config.save( pathCfg )
		except:
			wx.EndBusyCursor()	
			raise
			dlg1 = wx.MessageDialog(self, path + " can't be saved",
												 'Export error',
									wx.OK | wx.ICON_ERROR
									)
			dlg1.ShowModal()
			dlg1.Destroy()
			return
		wx.EndBusyCursor()	
		wx.CallAfter( self.ShowSuccess, path )
		
	def ExportRgn( self, event ):

	  dlg = wx.FileDialog(
		  self, message="Export region as ...", defaultDir=os.getcwd(), 
		  defaultFile= self.regionName , wildcard="SC4 Terrain files (*.SC4M)|*.SC4M""|16bit png files (*.png)|*.png|RGB files (*.bmp)|*.bmp", style=wx.FD_SAVE
		  )
	  if dlg.ShowModal() == wx.ID_OK:
		path = dlg.GetPath()		
		dlg.Destroy()
		ext = os.path.splitext( path )[1].upper()
		minX,minY,maxX,maxY,sizeX,sizeY,config = self.region.CropConfig()
		subRgn = [ minX*64+self.back.offX, minY*64+self.back.offY, maxX*64+1+self.back.offX, maxY*64+1+self.back.offY ]

		if  ext == ".SC4M":		  
		  self.ExportAsSC4M( path, config, minX, minY, subRgn  )
		if  ext == ".BMP":
		  self.ExportAsRGB( path, config, minX, minY, subRgn  )
		if ext == ".PNG":
		  self.ExportAsPNG( path, config, minX, minY, subRgn  )

	  else:
	    dlg.Destroy()
	  self.Refresh( False )

	def SaveRgn( self, event ):
		dlg = wx.TextEntryDialog(
				self, 'Enter the name of the new region',
				'Region name', self.regionName )
		if dlg.ShowModal() == wx.ID_OK:
		  name = dlg.GetValue()
		  dlg.Destroy()          
		else:          
		  dlg.Destroy()          
		  return None;
		
		path = os.path.join( self.mydocs, name )
		
		try:
		  os.makedirs( path )
		except WindowsError, error:
		  if error[0] == 183:
			dlg = wx.MessageDialog( self, 'A region with this name already exists or at least the region folder already exists\nDo you want to save anyway (removing previous region)?',
										  'Warning', wx.YES_NO|wx.NO_DEFAULT|wx.ICON_INFORMATION )
			ret = dlg.ShowModal()
			dlg.Destroy()
			if ret== wx.ID_NO:
			  return
			try:
			  allfiles = dircache.listdir( path )
			  valid = ['.SC4','.INI','.BMP', '.PNG' ]
			  allfiles = [ f for f in allfiles if os.path.splitext( f )[1].upper() in valid ]
			  for name in allfiles:
				os.unlink( os.path.join( path, name ) )
			except OSError:
			  dlg = wx.MessageDialog(self, 'A problem has occured while cleaning the region folder\nYou may try to clean it yourself',
								   'Error while saving region', wx.OK | wx.ICON_ERROR )
			  dlg.ShowModal()
			  dlg.Destroy()
			  return
		  else:
			dlg = wx.MessageDialog(self, 'A problem has occured while creating the region folder\nYou should enter a valid folder name as region name',
								 'Error while saving region', wx.OK | wx.ICON_ERROR )
			dlg.ShowModal()
			dlg.Destroy()
			return
		except OSError, error:
		  if error[0] == 22:
			dlg = wx.MessageDialog(self, 'A problem has occured while creating the region folder\nYou should enter a valid folder name as region name',
								 'Error while saving region', wx.OK | wx.ICON_ERROR )
			dlg.ShowModal()
			dlg.Destroy()
			return
		  elif error[0] == 17:
			dlg = wx.MessageDialog( self, 'A region with this name already exists or at least the region folder already exists\nDo you want to save anyway (removing previous region)?',
										  'Warning', wx.YES_NO|wx.NO_DEFAULT|wx.ICON_INFORMATION )
			ret = dlg.ShowModal()
			dlg.Destroy()
			if ret== wx.ID_NO:
			  return
			try:
			  allfiles = dircache.listdir( path )
			  valid = ['.SC4','.INI','.BMP', '.PNG' ]
			  allfiles = [ f for f in allfiles if os.path.splitext( f )[1].upper() in valid ]
			  for name in allfiles:
				os.unlink( os.path.join( path, name ) )
			except OSError:
			  dlg = wx.MessageDialog(self, 'A problem has occured while cleaning the region folder\nYou may try to clean it yourself',
								   'Error while saving region', wx.OK | wx.ICON_ERROR )
			  dlg.ShowModal()
			  dlg.Destroy()
			  return
		  else:
			dlg = wx.MessageDialog(self, 'A problem has occured while creating the region folder\nYou should enter a valid folder name as region name',
								 'Error while saving region', wx.OK | wx.ICON_ERROR )
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		wx.BeginBusyCursor()	
		self.region.folder = path
		dlg1 = wx.ProgressDialog("Saving region",
							 "Please wait while saving the region",
							 maximum = len( self.region.allCities),
							 parent=self,
							 style = 0 )
		minX,minY,maxX,maxY,sizeX,sizeY,config = self.region.CropConfig()
		subRgn = [ minX*64+self.back.offX, minY*64+self.back.offY, maxX*64+1+self.back.offX, maxY*64+1+self.back.offY ]
		config.save( os.path.join( path,"config.bmp" ) )
		try:
			saved = self.region.Save( dlg1, minX, minY, subRgn )
		except:
			saved = False
		wx.EndBusyCursor()	
		dlg1.Close()
		dlg1.Destroy()        
		if saved == False:
			dlg = wx.MessageDialog(self, 'A problem has occured while saving the cities files\nSome or all of the cities might not have been saved correctly',
								 'Error while saving region', wx.OK | wx.ICON_ERROR )
			dlg.ShowModal()
			dlg.Destroy()			
			return
		self.regionName = name
			  
	def OpenRgn( self,event ):
		self.btnEditMode.Enable( False )
		try:
		  r = self.LoadARegion()    
		except:
			raise
			r = None
			dlg = wx.MessageDialog(self, 'A problem has occured while reading the region\nMaybe it is too large for your RAM',
								 'Error while loading region',
								 wx.OK | wx.ICON_ERROR
								 #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
								 )
			dlg.ShowModal()
			dlg.Destroy()          
			
		if r == None:
			return

		self.btnEditMode.Enable( False )
		self.btnSave.Enable( True )
		self.btnExportRgn.Enable( True )
		self.btnSaveRgn.Enable( True )
		self.btnZoomIn.Enable( False )
		self.btnZoomOut.Enable( True )
		self.overlayCbx.Enable( True )
		self.back.offX = 0
		self.back.offY = 0

		self.region = r;
		self.zoomLevel = 1
		self.zoomLevelPow = 0
		self.btnEditMode.Enable( True )		
		self.back.SetVirtualSize((self.region.height.shape[1],self.region.height.shape[0]))
		
		self.SetFocus()
		self.SetTitle( "NHP SC4Mapper %s Version - "%MAPPER_VERSION+self.regionName )
		self.back.OnSize(None)		
		  
	

	def LoadARegion( self ):
		
		# In this case we include a "New directory" button. 
		dlg = wx.DirDialog( self, "Choose a directory:", defaultPath  = self.mydocs, style=wx.DEFAULT_DIALOG_STYLE|wx.DD_DIR_MUST_EXIST)
		if dlg.ShowModal() == wx.ID_OK:
		  self.regionPath = dlg.GetPath()
		else:
		  dlg.Destroy()
		  return None                           
		
		if not os.path.isdir( self.regionPath ):
			self.regionPath = os.path.split( self.regionPath )[0]
		#print self.regionPath
		# Only destroy a dialog after you're done with it.
		dlg.Destroy()
		self.waterLevel = 250

		wx.BeginBusyCursor()
		dlg = wx.ProgressDialog("Loading region",
							   "Please wait while loading the region",
							   maximum = 6,
							   parent=self,
							   style = 0 )
		  
		try:
  
		  dlg.Update( 0 )
		  NewRegion = rgnReader.SC4Region( self.regionPath,self.waterLevel, dlg )
		  if NewRegion.allCities == None:
			wx.EndBusyCursor()			
			dlg.Close()
			dlg.Destroy()   
			dlg = wx.MessageDialog(self, 'No cities found',
								   'Error while loading region',
								   wx.OK | wx.ICON_ERROR
								   )
			dlg.ShowModal()
			dlg.Destroy()          
			return None
		  NewRegion.show( dlg, True )
		  dlg.Close()
		  dlg.Destroy()        
  
		  if not NewRegion.IsValid():
			wx.EndBusyCursor()			
			dlg = wx.MessageDialog(self, 'This folder seems not to be a valid region',
								   'Error while loading region',
								   wx.OK | wx.ICON_ERROR
								   )
			dlg.ShowModal()
			dlg.Destroy()          
			return None
  
		  if NewRegion.IsValid() and NewRegion.config == None:
			wx.EndBusyCursor()			
			dlg = wx.MessageDialog(self, "There isn't any config.bmp",
								   'Warning while loading region',
								   wx.OK | wx.ICON_INFORMATION
								   #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
								   )
			dlg.ShowModal()
			dlg.Destroy()
		  wx.EndBusyCursor()			
		  self.regionName = os.path.splitext( os.path.split( self.regionPath )[1] )[0]
		  return NewRegion          
		except:
		  wx.EndBusyCursor()			
		  dlg.Destroy()
		  raise

class SplashScreen(wx.SplashScreen):
	def __init__(self):
		bmp = wx.Image( os.path.join( basedir, "splash.jpg" ),wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
		wx.SplashScreen.__init__(self, bmp,
								 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
								 1000, None, -1)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, evt):
		evt.Skip()
		self.Hide()
		self.ShowMain()

	def ShowMain(self):
		frame = OverView( None, "NHP SC4Mapper %s Version"%MAPPER_VERSION, (100,100) )
		frame.Show()
		

class SC4App( wx.App ):
	def OnInit( self ):
		splash = SplashScreen()
		splash.Show()
		return True


def main():
	mainPath = sys.path[0]
	os.chdir(mainPath)
	app = SC4App( False )
	app.MainLoop()

if getattr(sys, 'frozen', None):
	basedir = sys._MEIPASS
else:
	basedir = os.path.dirname(__file__)
print basedir

mainPath = sys.path[0]
os.chdir(mainPath)
main()

