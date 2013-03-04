import wx
import sys
import struct
import time
import QFS
import tools3D
import numpy as Numeric
import Image
import ImageDraw
import PngImagePlugin
import JpegImagePlugin
import BmpImagePlugin
import GradientReader
import math
import dircache
import os.path
from math import *


Image._initialized=2
generic_saveValue = 3
COMPRESSED_SIG = 0xFB10

def Normalize( p1 ):
	dx = float(p1[0])
	dy = float(p1[1])
	dz = float(p1[2])
	norm = sqrt( dx*dx + dy*dy + dz*dz )
	try:
		return ( p1[0]/norm, p1[1]/norm, p1[2]/norm )
	except:
		return ( 0, 0, 0 )
  
def ComputeOneRGB( bLight ,height, waterLevel, region):      
	lightDir = Normalize( (1, -5, -1) )
	rawRGB = tools3D.onePassColors( bLight, height.shape, waterLevel, height, GradientReader.paletteWater, GradientReader.paletteLand, lightDir )
	rgb = Numeric.fromstring( rawRGB, Numeric.int8 )
	rgb = Numeric.reshape( rgb, ( height.shape[0], height.shape[1], 3 )  )
	return rgb

class SC4Entry( object ):
	def __init__( self, buffer, idx ):
		self.compressed = False	  
		self.buffer = buffer
		t, g, i,self.fileLocation, self.filesize  = struct.unpack("3Lll", buffer)
		self.TGI = { 't':t ,'g':g,'i':i }
		self.initialFileLocation = self.fileLocation
		self.order = idx
			
	def ReadFile( self, sc4, readWhole = True , decompress = False ):    
		self.rawContent = None
		if readWhole:
			sc4.seek( self.fileLocation )
			self.rawContent = sc4.read( self.filesize )
			if decompress:
				if len( self.rawContent ) >= 8:
					compress_sig = struct.unpack( "H", self.rawContent[ 0x04:0x04+2 ] )[0]    
					if compress_sig == COMPRESSED_SIG:
						self.compressed = True    
			if self.compressed:
				if decompress: print 'Compressed file'
				uncompress = QFS.decode( self.rawContent[4:] )
				self.content = uncompress
			else:
				if decompress: print 'Uncompressed file'
				self.content = self.rawContent
 
	def IsItThisTGI( self, tgi ):
		return tgi[0] == self.TGI['t'] and tgi[1] == self.TGI['g'] and tgi[2] == self.TGI['i']
		
	def GetDWORD( self, pos ):
		return struct.unpack( "I", self.content[ pos:pos+4 ] )[0]

	def GetString( self, pos, length ):
		return self.content[ pos:pos+length ]
		  
class SaveFile( object ):      
	"""Class to be able to create a SC4 save file to hold city information, starting from a blank city"""
	def __init__( self, fileName ):
		"""load filename which should be a blank city"""
		self.fileName = fileName
		self.sc4 = open( self.fileName,"rb" )
		self.ReadHeader()
		self.ReadEntries()      

	def ReadHeader( self ):    
		"""read the SC4 DBPF header"""
		self.header = self.sc4.read( 96 )
		self.header = self.header[0:0x30]+'\0'*12+self.header[0x30+12:96]
		raw = struct.unpack("4s17I24s", self.header)
		self.indexRecordEntryCount = raw[9]
		self.indexRecordPosition = raw[10]
		self.indexRecordLength = raw[11]
		self.holeRecordEntryCount = raw[12]
		self.holeRecordPosition = raw[13]
		self.holeRecordLength = raw[14]
		self.dateCreated = raw[3]
		self.dateUpdated = raw[4]
		self.fileVersionMajor = raw[1]
		self.fileVersionMinor = raw[2]
		self.indexRecordType = raw[8]
	
	def ReadEntries( self ):
		"""Create entries for writing them later""" 
		self.entries = []
		self.sc4.seek( self.indexRecordPosition )    
		header = self.sc4.read( self.indexRecordLength )
		for idx in xrange( self.indexRecordEntryCount ):      
			entry = SC4Entry( header[ idx*20: idx*20+20], idx )
			if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ) or entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
				entry.ReadFile( self.sc4, True, True )
			else:
				entry.ReadFile( self.sc4 )
			self.entries.append( entry )
		self.sc4.close();

	def Save( self, cityXPos, cityYPos, heightMap, saveName ):
		"""Save a city
			read all entries
			create a save file
			replace the height,city info and region picture entry
			save all entries
		"""
		global generic_saveValue
		time.sleep(.1)
		self.heightMap = heightMap
		xSize = self.heightMap.shape[0]
		ySize = self.heightMap.shape[1]
		newData = QFS.encode( struct.pack( 'H', 0x2 ) + self.heightMap.tostring() )
		newData = struct.pack( "l", len( newData ) ) + newData 
		self.indexRecordPosition = 96
		self.dateUpdated = int( time.time() )+generic_saveValue*65535
		generic_saveValue += 1
		self.header = self.header[0:0x1C]+struct.pack( "I", self.dateUpdated )+self.header[0x1C+4:0x28]+struct.pack( "l", self.indexRecordPosition )+self.header[0x28+4:96]
		self.sc4 = open( self.fileName,"rb" )
		for entry in self.entries:
			if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ) or entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
				entry.ReadFile( self.sc4, True, True )
			if entry.rawContent == None:
				entry.ReadFile( self.sc4, True )     
		self.sc4.close()       
		while 1:
			try:
				self.sc4 = open( saveName,"wb" )
				break
			except IOError:        
				dlg = wx.MessageDialog( None, "file %s seems to be ReadOnly\nDo you want to skip?(Yes)\nOr retry ?(No)"%(saveName),"Warning",wx.YES_NO|wx.ICON_QUESTION)
				result = dlg.ShowModal()
				dlg.Destroy()
				if result == wx.ID_YES:
					return False
		self.sc4.write( self.header )
		self.sc4.truncate( self.indexRecordPosition )
		self.sc4.seek( self.indexRecordPosition )
		pos = self.indexRecordPosition + self.indexRecordLength
		for entry in self.entries:
			entry.fileLocation = pos
			newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "l", entry.fileLocation ) + entry.buffer[ 0x0C+4: ]
			if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ): #heights
				newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "l", entry.fileLocation ) + struct.pack( "l", len( newData ) )+ entry.buffer[ 0x10+4: ]
				entry.rawContent = newData
				entry.compressed = 1
				entry.filesize = len( newData )
			if entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ): #city info
				v = self.dateUpdated
				entry.content = entry.content[ 0 : 0x04 ] + struct.pack( "I", cityXPos ) + struct.pack( "I", cityYPos ) + entry.content[ 0x0C:39 ] + struct.pack( "I", v ) + entry.content[ 39+4: ]
				newDataCity  = entry.rawContent[:]
				newDataCity  = QFS.encode( entry.content )
				newDataCity  = struct.pack( "l", len( newDataCity ) ) + newDataCity 
				newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "l", entry.fileLocation ) + struct.pack( "l", len( newDataCity ) )+ entry.buffer[ 0x10+4: ]
				entry.rawContent = newDataCity
				entry.compressed = 1
				entry.filesize = len( newDataCity )
			if entry.IsItThisTGI( (0x8a2482b9,0x4a2482bb,0x00000000) ): #region view
				n = os.path.splitext( saveName )[0]
				png = open( n+".PNG","rb" )
				pngData = png.read()
				png.close()
				os.unlink( n+".PNG" )
				newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "I", entry.fileLocation ) + struct.pack( "I", len( pngData ) )+ entry.buffer[ 0x10+4: ]
				entry.rawContent = pngData
				entry.compressed = 0
				entry.filesize = len( pngData )
			if entry.IsItThisTGI( (0x8a2482b9,0x4a2482bb,0x00000002) ): #alpha region view
				n = os.path.splitext( saveName )[0]
				png = open( n+"_alpha.PNG" ,"rb" )
				pngData = png.read()
				png.close()
				os.unlink( n+"_alpha.PNG" )
				newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "I", entry.fileLocation ) + struct.pack( "I", len( pngData ) )+ entry.buffer[ 0x10+4: ]
				entry.rawContent = pngData
				entry.compressed = 0
				entry.filesize = len( pngData )
			self.sc4.write( newbuffer)
			pos += entry.filesize
		for entry in self.entries:
			self.sc4.write( entry.rawContent )
		self.sc4.close()
		return True

def Save( city, folder,color,waterLevel ):
	"""Save a city file, build the thumbnail for region view"""
	mainPath = sys.path[0]
	os.chdir(mainPath)    
	if city.cityXSize == 1:
		name = 'City - Small.sc4'
	if city.cityXSize == 2:
		name = 'City - Medium.sc4'
	if city.cityXSize == 4:
		name = 'City - Large.sc4'
	city.fileName = folder+"/"+"City - New city(%03d-%03d).sc4"%( city.cityXPos, city.cityYPos )	
	BuildThumbnail( city, color ,waterLevel )
	saved = SaveFile( name )
	return saved.Save( city.cityXPos, city.cityYPos, city.heightMap, city.fileName )
	
def BuildThumbnail(city,colors,waterLevel):
	"""Build the region view images (normal&alpha)"""
	n = os.path.splitext( city.fileName )[0]
	minx,miny,maxx,maxy,r = tools3D.generateImage( waterLevel,city.heightMap.shape, city.heightMap.tostring(), colors )
	print city.heightMap.shape, len( colors )
	print minx,miny,maxx,maxy
	maxx += 2
	offset = len(r)/2
	im = Image.fromstring( "RGB", ( 514,428 ), r[:offset]) 
	im = im.crop( [minx,miny,maxx,maxy] )
	im.save( n+".PNG" )
	im = Image.fromstring( "RGB", ( 514,428 ), r[offset:]) 
	im = im.crop( [minx,miny,maxx,maxy] )
	im.save( n+"_alpha.PNG" )
	return

class SC4File( object ):
	"""A file representing a saved city on the regions folder"""
	def __init__( self, fileName ):
		"""the file is open here, and closed in ReadEntries"""
		self.fileName = fileName
		self.sc4 = open( self.fileName,"rb" )

	def AtPos( self, x,y ):
		"""check if the city is at a specific coordinate ( in config.bmp coordinate )"""
		return x == self.cityXPos and y == self.cityYPos

	def Split( self ):
		"""spliting a city, only for medium or large city, divide the city in 4 smallers cities"""
		if self.cityXSize==1:
			return []
		return [ CityProxy( 250, self.cityXPos                 , self.cityYPos                 , self.cityXSize/2, self.cityYSize/2 )
			   , CityProxy( 250, self.cityXPos+self.cityXSize/2, self.cityYPos                 , self.cityXSize/2, self.cityYSize/2 )
			   , CityProxy( 250, self.cityXPos+self.cityXSize/2, self.cityYPos+self.cityYSize/2, self.cityXSize/2, self.cityYSize/2 )
			   , CityProxy( 250, self.cityXPos				   , self.cityYPos+self.cityYSize/2, self.cityXSize/2, self.cityYSize/2 )
			   ]

	def ReadHeader( self ):    
		self.header = self.sc4.read( 96 )
		self.header = self.header[0:0x30]+'\0'*12+self.header[0x30+12:96]
		raw = struct.unpack("4s17I24s", self.header)
		self.indexRecordEntryCount = raw[9]
		self.indexRecordPosition = raw[10]
		self.indexRecordLength = raw[11]
		self.holeRecordEntryCount = raw[12]
		self.holeRecordPosition = raw[13]
		self.holeRecordLength = raw[14]
		self.dateCreated = raw[3]
		self.dateUpdated = raw[4]
		self.fileVersionMajor = raw[1]
		self.fileVersionMinor = raw[2]
		self.indexRecordType = raw[8]

		print os.path.split( self.fileName )[1], self.indexRecordPosition, self.indexRecordEntryCount, self.indexRecordLength
	
	def ReadEntries( self ):
		"""Read all entries, only a few are read deeply and only the height entry is kept"""
		self.entries = []
		self.sc4.seek( self.indexRecordPosition )    
		header = self.sc4.read( self.indexRecordLength )
		for idx in xrange( self.indexRecordEntryCount ):      
			entry = SC4Entry( header[ idx*20: idx*20+20], idx )
			if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ) or entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
				entry.ReadFile( self.sc4, True, True )	  
			if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ):
				print 'This was the terrain'
				self.heightMapEntry = entry
			if entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
				print 'This was the city info', entry.compressed
				print 'version ',hex(entry.GetDWORD( 0x00 ))
				version = entry.GetDWORD( 0x00 )
				self.cityXPos = entry.GetDWORD( 0x04 )
				self.cityYPos = entry.GetDWORD( 0x08 )
				self.cityXSize = entry.GetDWORD( 0x0C )
				self.cityYSize = entry.GetDWORD( 0x10 )
				print 'city tile X = ', self.cityXPos 
				print 'city tile Y = ', self.cityYPos 
				print 'city size X = ', self.cityXSize
				print 'city size Y = ', self.cityYSize
				offsetLen = 64
				if version == 0xD0001:
					offsetLen = 64
				if version == 0xA0001:
					offsetLen = 63
				if version == 0x90001:
					offsetLen = 59
				sizeName = entry.GetDWORD( offsetLen )
				print 'name city length', sizeName
				if( sizeName < 100 ):
					self.cityName = entry.GetString( offsetLen + 4, sizeName )
					print self.cityName
				else:
					print 'xxxxxxxxxxxxxxxxxxxxoldv', version
					self.cityName = "weird name"
		print 'finished reading the sc4' 
		print '--'*20       
		self.ySize = self.cityYSize * 64 +1                
		self.xSize = self.cityXSize * 64 +1
		self.xPos = self.cityXPos * 64
		self.yPos = self.cityYPos * 64
		header = None
		self.sc4.close()
	
class CityProxy( object ):
	"""A proxy for an empty city"""
	def __init__( self, waterLevel, xPos, yPos, xSize, ySize ):
		self.cityXPos = xPos
		self.cityYPos = yPos
		self.cityXSize = xSize
		self.cityYSize = ySize
		self.cityName = 'Not created yet'
		self.ySize = self.cityYSize * 64 +1                
		self.xSize = self.cityXSize * 64 +1
		self.xPos = self.cityXPos * 64
		self.yPos = self.cityYPos * 64
		self.fileName = None

	def AtPos( self, x,y ):
		"""check if the city is at a specific coordinate ( in config.bmp coordinate )"""
		return x == self.cityXPos and y == self.cityYPos
	
	def Split( self ):
		"""spliting a city, only for medium or large city, divide the city in 4 smallers cities"""
		if self.cityXSize==1:
			return []
		return [ CityProxy( 250, self.cityXPos                 , self.cityYPos                 , self.cityXSize/2, self.cityYSize/2 )
			   , CityProxy( 250, self.cityXPos+self.cityXSize/2, self.cityYPos                 , self.cityXSize/2, self.cityYSize/2 )
			   , CityProxy( 250, self.cityXPos+self.cityXSize/2, self.cityYPos+self.cityYSize/2, self.cityXSize/2, self.cityYSize/2 )
			   , CityProxy( 250, self.cityXPos				   , self.cityYPos+self.cityYSize/2, self.cityXSize/2, self.cityYSize/2 )
			   ]

def WorkTheconfig( config, waterLevel ):
	"""Read the config.bmp, verify it, and create the city proxies for it"""
	verified = Numeric.zeros( config.size, Numeric.int8 )
	def Redish( value ):
		"""True for small city"""
		(r,g,b) = value
		if r > g and r > b and r > 250 :
			return True
		return False
	def Greenish( value ):
		"""True for medium city"""
		(r,g,b) = value
		if g > r and g > b and g > 250:
			return True
		return False
	def Blueish( value ):
		"""True for big city"""
		(r,g,b) = value
		if b > r and b > g  and b > 250:
			return True
		return False
	def VerifyMedium( x,y ):
		"""Verify the 2x2 pixels from x,y are green"""
		rgbs = (config.getpixel( (x+1, y) ), config.getpixel( (x, y+1)), config.getpixel( (x+1, y+1) ) )
		for rgb in rgbs:
			if not Greenish( rgb ):
				assert 0
		verified[ x,y ]=1
		verified[ x+1,y ]=1
		verified[ x,y+1 ]=1
		verified[ x+1,y+1 ]=1
	def VerifyLarge( x,y ):
		"""Verify the 4x4 pixels from x,y are blue"""
		rgbs = (
		 config.getpixel( (x+1, y) ),config.getpixel( (x+2, y) ),config.getpixel( (x+3, y) ),
		 config.getpixel( (x, y+1) ),config.getpixel( (x+1, y+1) ),config.getpixel( (x+2, y+1) ),config.getpixel( (x+3, y+1) ),
		 config.getpixel( (x, y+2) ),config.getpixel( (x+1, y+2) ),config.getpixel( (x+2, y+2) ),config.getpixel( (x+3, y+2) ),
		 config.getpixel( (x, y+3) ),config.getpixel( (x+1, y+3) ),config.getpixel( (x+2, y+3) ),config.getpixel( (x+3, y+3) )
		 )
		for rgb in rgbs:
			if not Blueish( rgb ):
				assert 0
		for j in xrange(4):
			for i in xrange(4):
				verified[ x+i,y+j ]=1
	big = 0
	bigs = []
	small = 0
	smalls = []
	medium = 0
	mediums = []	
	for y in xrange( config.size[1] ):
		for x in xrange( config.size[0] ):
			if verified[ x,y ] == 0:
				rgb = config.getpixel( (x,y) )
				if Blueish( rgb ):    
					try:                
						VerifyLarge( x,y )
						bigs.append( (x,y) )                    
						big += 1
					except:
						print x,y, "not blue"
						raise
				if Greenish( rgb ):
					try:                
						VerifyMedium( x,y )
						mediums.append( (x,y) )
						medium += 1
					except:
						print x,y, "not green"
						raise
				if Redish( rgb ):
					smalls.append( (x,y ) )
					small += 1
	print "big cities = ", big
	print "medium cities = ", medium
	print "small cities = ", small
	cities = [ CityProxy( waterLevel, c[0],c[1], 1,1 ) for c in smalls ] + [ CityProxy( waterLevel, c[0],c[1], 2,2 ) for c in mediums ] + [ CityProxy( waterLevel, c[0],c[1], 4,4 ) for c in bigs ]
	return cities

def BuildBestConfig( configSize ):
	"""Create a config.bmp that will be filled with as most big cities as it can, then medium then small"""
	im = Image.new( "RGB", configSize, "#0000FF" )	
	nbBigX = configSize[0]/4
	nbMediumX = 0
	nbSmallX = 0
	rX = configSize[0]%4
	if rX == 1 or rX == 3:
		nbSmallX = 1
	if rX == 3 or rX == 2:
		nbMediumX = 1
	nbBigY = configSize[1]/4
	nbSmallY = 0
	nbMediumY = 0
	rY = configSize[1]%4
	if rY == 1 or rY == 3:
		nbSmallY = 1
	if rY == 3 or rY == 2:
		nbMediumY = 1
	print configSize[0],rX, nbBigX,'(B)',nbMediumX,'(M)',nbSmallX,'(S)'
	im.paste( "#00FF00", (nbBigX*4,0,configSize[0],configSize[1])  )
	im.paste( "#00FF00", (0,nbBigY*4,configSize[0],configSize[1])  )
	im.paste( "#FF0000", (nbBigX*4+nbMediumX*2,0,configSize[0],configSize[1])  )
	im.paste( "#FF0000", (0,nbBigY*4+nbMediumY*2,configSize[0],configSize[1])  )
	return im

class SC4Region( object ):
	"a SC4 region, contains cities, layout and height map"
	def __init__( self, folder, waterLevel, dlg, config = None ):
		self.waterLevel = waterLevel
		if config is not None:
			self.folder = None
			allCityFileNames = []
			self.config = config
		else:
			self.folder = folder
			allfiles = dircache.listdir( folder )
			allCityFileNames = [ x for x in allfiles if os.path.splitext( x )[1] == ".sc4" ]    
			try:
				self.config = Image.open( encodeFilaneme( os.path.join( folder,"config.bmp" ) ) )
			except:      
				self.config = None
		self.allCities = [] 
		
		if self.config:
			self.config = self.config.convert( 'RGB' )
			self.originalConfig = self.config.copy()
			self.allCities = WorkTheconfig( self.config, waterLevel )
		else:
			self.originalConfig= None
		
		for save in allCityFileNames:
			if dlg is not None: dlg.Update( 1, "Please wait while loading the region"+"\nReading "+save )
			sc4 = SC4File( os.path.join( folder, save ) )
			sc4.ReadHeader()
			sc4.ReadEntries()      
			for i,city in enumerate( self.allCities ):
				if city.AtPos( sc4.cityXPos, sc4.cityYPos ):
					if city.__class__ == CityProxy and city.cityXPos == sc4.cityXPos and city.cityYPos == sc4.cityYPos and city.cityXSize == sc4.cityXSize and city.cityYSize == sc4.cityYSize:
						self.allCities = self.allCities[:i]+self.allCities[i+1:]
					else:            
						dlg1 = wx.MessageDialog( None, 'It seems that the config.bmp does not match the savegames present in the region folder','error', wx.OK | wx.ICON_ERROR )
						dlg1.ShowModal()
						dlg1.Destroy()
						self.allCities = None
						return
		  	self.allCities.append( sc4 )
		self.config = self.BuildConfig()
		self.originalConfig = self.BuildConfig()  
		if dlg is not None: dlg.Update( 1, "Please wait while loading the region" )
	
	def CropConfig( self ):
		"find the bbox of valid cities and return the new resized config"
		sizeX = sizeY = 0
		minX = minY = maxX = maxY = None
		for city in ( self.allCities ):
			if minX == None or city.cityXPos < minX:
				minX = city.cityXPos
			if minY == None or city.cityYPos < minY:
				minY = city.cityYPos
			if maxX == None or city.cityXPos+city.cityXSize > maxX:
				maxX = city.cityXPos+city.cityXSize
			if maxY == None or city.cityYPos+city.cityYSize > maxY:
				maxY = city.cityYPos+city.cityYSize
		sizeX = maxX-minX
		sizeY = maxY-minY
		config = self.config.crop( (minX, minY, maxX, maxY ) )
		print 'crop size',minX,minY,maxX,maxY,sizeX,sizeY
		return minX,minY,maxX,maxY,sizeX,sizeY,config

	def BuildConfig( self ):
		"""Build a nice config.bmp with slight colors changes, also fill the missingCities"""
		sizeX = sizeY = 0
		bigs = []
		smalls = []
		mediums = []
		for city in ( self.allCities ):
			if city.cityXSize == 4:
				bigs.append( (city.cityXPos,city.cityYPos ) )
			if city.cityXSize == 2:
				mediums.append( (city.cityXPos,city.cityYPos ) )
			if city.cityXSize == 1:
				smalls.append( (city.cityXPos,city.cityYPos ) )
			if city.cityXPos + city.cityXSize > sizeX:
				sizeX = city.cityXPos + city.cityXSize
			if city.cityYPos + city.cityYSize > sizeY:
				sizeY = city.cityYPos + city.cityYSize
		if self.originalConfig :	
			sizeX = self.originalConfig.size[0]
			sizeY = self.originalConfig.size[1]
		config = Image.new( "RGB", (sizeX,sizeY) )
		draw = ImageDraw.Draw(config)
		for c in smalls:
			reds = ( "#FF7777", "#FF0000" )
			color = c[0]+c[1]      
			draw.rectangle( [ c, (c[0],c[1])], fill=reds[color%2] )
		for c in mediums:
			colors = ( "#00FF00","#99FF00","#00FF99","#55FF55" )
			color = c[0]+c[1]      
			draw.rectangle( [ c, (c[0]+1,c[1]+1)], fill=colors[color%4] )
		for c in bigs:
			colors = ( "#0000FF","#4000FF","#8000FF","#C000FF","#0040FF","#4040FF","#8040FF","#C040FF",
		  			   "#0080FF","#4080FF","#8080FF","#C080FF","#00C0FF","#40C0FF","#80C0FF","#C0C0FF", )
			color = c[0]+c[1]      
			draw.rectangle( [ c, (c[0]+3,c[1]+3)], fill=colors[color%16] )
		self.missingCities = []
		for y in xrange( sizeY ):
			for x in xrange( sizeX ):
				if self.GetCityUnder( (x,y) ) == None:
					self.missingCities.append( (x,y ) )	
		return config

	def DeleteCityAt( self, pos ):
		"find the city at a certain x,y and remove it"
		for i,city in enumerate( self.allCities ):
			if pos[0] >= city.cityXPos and pos[0] < city.cityXPos+city.cityXSize and pos[1] >= city.cityYPos and pos[1] < city.cityYPos+city.cityYSize :
				self.allCities = self.allCities[:i]+self.allCities[i+1:]
				break

	def GetCityUnder( self, pos ):
		"find the city at a certain x,y"
		for city in ( self.allCities ):
			if pos[0] >= city.cityXPos and pos[0] < city.cityXPos+city.cityXSize and pos[1] >= city.cityYPos and pos[1] < city.cityYPos+city.cityYSize :
				return city
		return None

	def GetCitiesUnder( self, pos, size ):
		"find all cities under rect"
		cities = []
		for city in ( self.allCities ):
			def collide( x1,y1,w1,h1,x2,y2,w2,h2 ):
				return not (x1 >= x2+w2 or x1+w1 <= x2 or y1 >= y2+h2 or y1+h1 <= y2)
			if collide( pos[0],pos[1],size,size, city.cityXPos, city.cityYPos, city.cityXSize, city.cityYSize ):
				cities.append( city )
		return cities

	def IsValid( self ):
		"the region is valid if there is at least one city or the config.bmp is ok"
		return len( self.allCities ) > 0 or self.config != None

	def Save( self, dlg, minX, minY, subRgn ):
		"save the region to SC4File"
		print "saving"
		saved = True
		for i,city in enumerate( self.allCities ):      
			dlg.Update( i, "Please wait while saving the region"+"\nSaving "+" City - New city(%03d-%03d).sc4"%( city.cityXPos, city.cityYPos ) )
			citySave = CityProxy( self.waterLevel, city.cityXPos-minX, city.cityYPos-minY, city.cityXSize, city.cityYSize )
			citySave.heightMap = Numeric.zeros( (citySave.ySize, citySave.xSize), Numeric.uint16 )
			citySave.heightMap[::,::] =  self.height[ citySave.yPos+subRgn[1]:citySave.yPos+subRgn[1]+citySave.ySize,citySave.xPos+subRgn[0]:citySave.xPos+subRgn[0]+citySave.xSize ]	  
			citySave.heightMap = citySave.heightMap.astype( Numeric.float32 ) / Numeric.asarray( 10, Numeric.float32 )
			x1 = citySave.xPos
			y1 = citySave.yPos
			x2 = x1 + citySave.xSize
			y2 = y1 + citySave.ySize
			print x1,y1,x2,y2
			print citySave.yPos+subRgn[2],'to',citySave.yPos+subRgn[2]+citySave.ySize,'and',citySave.xPos+subRgn[0],'to',citySave.xPos+subRgn[0]+citySave.xSize
			lightDir = Normalize( (1, -5, -1) )
			rawRGB = tools3D.onePassColors( False, citySave.heightMap.shape, self.waterLevel, citySave.heightMap, GradientReader.paletteWater, GradientReader.paletteLand, lightDir )	  
			print citySave.heightMap.shape,len(rawRGB)
			try:
				if not Save( citySave, self.folder,rawRGB,self.waterLevel ):
					saved = False
			except:
				print 'problem while saving',citySave.fileName,city.cityXPos,city.cityYPos,city.cityXSize,city.cityYSize
				saved = False
			citySave.heightMap = None
		return saved

	def show( self, dlg, readFiles = False ):
		"compute size/shape and load the heightmap if readFiles is True"
		imgSize = [0,0]
		if self.config:
			imgSize[0] = self.config.size[0]
			imgSize[1] = self.config.size[1]
		for city in self.allCities:
			x = city.cityXPos + city.cityXSize
			y = city.cityYPos + city.cityYSize
			if imgSize[0] < x :
				imgSize[0] = x
			if imgSize[1] < y :
				imgSize[1] = y
		self.imgSize = [ a * 64 + 1 for a in imgSize ]              
		self.shape = [self.imgSize[1],self.imgSize[0]]
		if readFiles == False:
			return
		dlg.Update( 2, "Please wait while loading the region\nBuilding textures" )		
		self.height = Numeric.zeros( self.shape, Numeric.uint16 )
		for city in self.allCities:
			if hasattr( city, "heightMapEntry" ):
				self.height[ city.yPos:city.yPos+city.ySize,city.xPos:city.xPos+city.xSize ] = Numeric.reshape( (Numeric.fromstring( city.heightMapEntry.content[2:], Numeric.float32 )*Numeric.array( 10, Numeric.float32 )).astype( Numeric.uint16 ), (city.ySize, city.xSize) )
				del city.heightMapEntry
			else:
				self.height[ city.yPos:city.yPos+city.ySize,city.xPos:city.xPos+city.xSize ] = Numeric.ones( (city.ySize, city.xSize), Numeric.uint16 )*Numeric.array( self.waterLevel-50 ).astype( Numeric.uint16 )
			city.height = None
		dlg.Update( 2, "Please wait while loading the region\nBuilding textures" )		
		print 'region read'
		return


GradientReader.Init('basicColors.ini')
