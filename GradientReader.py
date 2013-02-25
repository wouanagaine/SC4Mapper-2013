""" this will read gradients files for coloring the landscape """
import ConfigParser 

def HTMLColorToRGB(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)

def ReadGradientConfig( fileName ):
    try:
      cp = ConfigParser.ConfigParser()
      cp.read( fileName )
      values = cp.items("background")
      values =[ (0,HTMLColorToRGB(v[1])) for v in values ]
      values.sort( key = lambda x:x[0] )
      bgColor={}
      for v in values:
          bgColor[v[0]] = v[1]
      
      values = cp.items("land")
      values =[ (int(v[0]),HTMLColorToRGB(v[1])) for v in values ]
      values.sort( key = lambda x:x[0] )
      paletteLand={}
      for v in values:
          paletteLand[v[0]] = v[1]
      values = cp.items("water")
      values =[ (int(v[0]),HTMLColorToRGB(v[1])) for v in values ]
      values.sort( key = lambda x:x[0] )
      paletteWater={}
      for v in values:
          paletteWater[v[0]] = v[1]      
      print paletteWater
      print paletteLand
      return bgColor[0],paletteWater,paletteLand
    except:
      return (0,128,255),{ 0:(123,189,214), 200:(0,8,74) },{ 0:(123,189,214),100:(0,206,0),1000:(255,255,255)}
      
    
paletteWater = {}
paletteLand = {}
bgColor = (0,128,255)

def Init( fileName ):
    global paletteWater
    global paletteLand
    global bgColor
    bgColor,paletteWater, paletteLand = ReadGradientConfig( fileName )    
    print bgColor,paletteWater, paletteLand