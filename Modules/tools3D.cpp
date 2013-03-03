/*
Copyright (c) 2013, Wouanagaine
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
#include <Python.h>
#include <malloc.h>
#include <memory.h>
#include <math.h>
#include <vector>
#include <map>

template< typename T1, typename T2 > 
T1 min( T1 a, T2 b )
{
	return a<b ? a : b;
}
	
inline 
float Lerp( float a, float b, float alpha )
{
    return (1.f-alpha)*a+b*alpha;
}

float Dot( float* v1, float* v2 )
{
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2];
}

inline
void ComputeNormal( float* norm, int x, int y, int xSize, int ySize, float* height)
{
	memset( norm, 0, sizeof( float )*3 );
	if( x == 0 || x == xSize-1 || y == 0 || y == ySize -1 )
	{

		return;
	}
	float* pCurr = &height[x+y*xSize ];
	float dx = *(pCurr-1)- *(pCurr+1);
	float dy = *(pCurr-xSize)- *(pCurr+xSize);
	float dz = 2.f;
	float mag = (float)sqrt( dx*dx + dy*dy +dz*dz );
	norm[0] = dx/mag;
	norm[1] = dz/mag;
	norm[2] = dy/mag;
}


struct RGBColor
{
    RGBColor( int _r, int _g, int _b ):r(_r),g(_g),b(_b) {}
    int r,g,b;
};

struct Gradient
{
    explicit Gradient( PyObject* p )
    : colors_()
    {
    	if( PyDict_Check( p ) )
    	{
    		PyObject *key, *value;
    		int pos = 0;
    
    		while (PyDict_Next(p, &pos, &key, &value)) 
    		{
    			int k;
    			int r,g,b;
    			if( PyInt_Check( key ) )
    			{
    				k = PyInt_AsLong( key );
    				//printf("key ok %d\n",k );
    			}
    			else
    			{
    				printf("key not ok\n" );
    			}
    			if( PyTuple_Check( value ) )
    			{
    			    r = PyInt_AsLong( PyTuple_GetItem( value,0 ) );
    			    g = PyInt_AsLong( PyTuple_GetItem( value,1 ) );
    			    b = PyInt_AsLong( PyTuple_GetItem( value,2 ) );
    			    //printf("value ok %d\n",r,g,b );
    			    colors_.insert( std::make_pair( k, RGBColor( r,g,b) ) );
    			}
    			else
    				printf("value not ok\n" );
            }        
        }        
        printf("----\n" );
    }

    RGBColor GetColor( int value ) const
    {
        std::map<int, RGBColor >::const_iterator it = colors_.begin();
        std::map<int, RGBColor >::const_iterator itEnd = colors_.end();
        if( value < it->first )
        {
            return it->second;
        }
        std::map<int, RGBColor >::const_iterator justInCase = it;
        while( it != itEnd )
        {
            if( value < it->first )
            {
                float distTot = it->first - justInCase->first;
                float distCur = value-justInCase->first;
                float alpha = distCur/distTot;
                float r = Lerp( justInCase->second.r, it->second.r, alpha );
                float g = Lerp( justInCase->second.g, it->second.g, alpha );
                float b = Lerp( justInCase->second.b, it->second.b, alpha );
                return RGBColor( r,g,b );
            }
            justInCase = it;
            ++it;
        }        
        return justInCase->second;            
    }
    std::map<int, RGBColor > colors_;    
};

unsigned char* OnePassColors( bool bLight, int xSize, int ySize, float waterLevel, float* height, const Gradient& waterGrad, const Gradient& landGrad, float* lightDir )
{
	int x,y;
	unsigned char* colors;
	colors = (unsigned char*)malloc( xSize*ySize*3 );
	memset( colors, 0xFF, xSize*ySize*3 );
	float vertex[3];
	float h,l,v;
	float* pCurrHeight = height;
	unsigned char* pCurrColor = colors;
	for( y = 0; y < ySize; ++y )
	{
		for( x = 0; x < xSize; ++x, ++pCurrHeight )
		{
			float h = *pCurrHeight;
			if( !(*pCurrColor == 255 && *(pCurrColor+1) == 255 && *(pCurrColor+2) == 255 ) )
			{
				pCurrColor+=3;
				continue;
			}
			float norm[3];
			ComputeNormal( norm, x, y, xSize, ySize, height );
			float n = norm[1]*255.f;
			unsigned char c = 0xFF;
			l = Dot( norm, lightDir );
			if( l < 0 )
			{
				v = (l) * 64.f;
				c = 191-(int)v;
			}							
			if( n < 20 )
			{
				*(pCurrColor++) = c/2;
				*(pCurrColor++) = c/2;
				*(pCurrColor++) = c/2;
			}
			else if( h < waterLevel )
			{
				float v = waterLevel - h;
                RGBColor col = waterGrad.GetColor( v );
				
				int r = col.r * c;
				int g = col.g * c;
				int b = col.b * c;
				r >>= 8;
				g >>= 8;
				b >>=8;				
				*(pCurrColor++) = r;
				*(pCurrColor++) = g;
				*(pCurrColor++) = b;
			}
			else
			{
				
				float v = h  - waterLevel;
                RGBColor col = landGrad.GetColor( v );
                
				int r = col.r * c;
				int g = col.g * c;
				int b = col.b * c;
				r >>= 8;
				g >>= 8;
				b >>=8;				
				*(pCurrColor++) = r;
				*(pCurrColor++) = g;
				*(pCurrColor++) = b;
			}
			// propagate shadows
			vertex[0] = x;
			vertex[1] = h/7.f;
			vertex[2] = y;
			while( bLight )
			{
                vertex[0] += 1;
                vertex[1] += lightDir[1];
                vertex[2] += -1;
                if( vertex[1] < 0 )
                    break;
                if( vertex[0] < 0 )
					break;
                if( vertex[2] < 0 )
                    break;
                if( vertex[0] >= xSize )
                    break;
                if( vertex[2] >= ySize )
                    break;

                h = height[ (int) vertex[0] + (int)vertex[2] * xSize ];
                    
                if( h/7.f < vertex[1] )
				{
					int lx = (int)vertex[0];
					int ly = (int)vertex[2];
					c=127;
					ComputeNormal( norm, lx, ly, xSize, ySize, height );
					float n = norm[1]*255.f;
					unsigned char* pOld = pCurrColor;
					pCurrColor = &colors[ (lx + ly*xSize)*3 ];

					if( n < 20 )
					{
						*(pCurrColor++) = c/2;
						*(pCurrColor++) = c/2;
						*(pCurrColor++) = c/2;
					}
					else if( h < waterLevel )
					{
						float v = waterLevel - h;
						RGBColor col = waterGrad.GetColor( v );
						
						int r = col.r * c;
						int g = col.g * c;
						int b = col.b * c;
						r >>= 8;
						g >>= 8;
						b >>=8;				
						*(pCurrColor++) = r;
						*(pCurrColor++) = g;
						*(pCurrColor++) = b;
					}
					else
					{
						float v = h  - waterLevel;
						RGBColor col = landGrad.GetColor( v );
		                
						int r = col.r * c;
						int g = col.g * c;
						int b = col.b * c;
						r >>= 8;
						g >>= 8;
						b >>=8;				
						*(pCurrColor++) = r;
						*(pCurrColor++) = g;
						*(pCurrColor++) = b;
					}
					pCurrColor = pOld;
				}
			}
		}
	}
	return colors;
}

unsigned char* GenerateImage( float waterLevel,int xSize, int ySize, float* heights, unsigned char* colors, int* pMinx,int* pMiny,int* pMaxx,int* pMaxy )
{
	int* minYmap = new int[514];
	int* maxYmap = new int[514];
	memset( maxYmap, 0, 514*4 );
	memset( minYmap, 0x7f, 514*4 );
	unsigned char* im = (unsigned char*)malloc( 514*428*6 );
	memset( im, 0, 514*428*6 );
    int miny  = 428;
    int maxy = 0;
    int minx  = 514;
    int maxx = 0;
	int secondOffset = 514*428*3;
	for( int y = 0; y < ySize; ++y )
		for( int x = 0; x < xSize; ++x )
		{
			float x2 = float(x)*(512.f-150.f)/256.f + 150.f-(150.f*float(y)/256.f);
			float y2 = float(y)*(181.f)/256.f+75.f*float(x)/256.f;
			float yBase = y2;
			float h = heights[ y*xSize + x ];
			if( h < waterLevel )
				h = waterLevel;
			h  *= 21.f/250.f;
			y2 -= h;
			y2 += 428-256;
			yBase += 428-256;
			if( y2 < 0.f )
				y2 = 0.f;
			if( y2 < miny )
				miny = y2;
			if( yBase > maxy )
				maxy = yBase;
			if(x2 < minx)
				minx = x2;
			if (x2 > maxx)
				maxx = x2;
			if( minYmap[ (int)x2 ] > y2 )
				minYmap[ (int)x2 ] = (int)y2;
			if( maxYmap[ (int)x2 ] < y2 )
				maxYmap[ (int)x2 ] = (int)y2;
			unsigned char r = colors[(y*xSize+x)*3+0];
			unsigned char g = colors[(y*xSize+x)*3+1];
			unsigned char b = colors[(y*xSize+x)*3+2];
			for( int j = (int)y2; j<(int)yBase;++j)
			{
				im[ ((int)x2+((int)j)*514)*3+0 ]=r; 
				im[ ((int)x2+((int)j)*514)*3+1 ]=g; 
				im[ ((int)x2+((int)j)*514)*3+2 ]=b; 
				im[ secondOffset+((int)x2+((int)j)*514)*3+2 ]=255;
			}
		}
	for( int x = minx; x < maxx; ++x )
	{
		im[ secondOffset+(x+(minYmap[x])*514)*3+0 ]=255;
		im[ secondOffset+(x+(minYmap[x])*514)*3+1 ]=255;
		im[ secondOffset+(x+(maxYmap[x])*514)*3+0 ]=255;
		im[ secondOffset+(x+(maxYmap[x])*514)*3+1 ]=255;
	}
	*pMinx = minx;
	*pMiny = miny;
	*pMaxx = maxx;
	*pMaxy = maxy;
	delete[] minYmap;
	delete[] maxYmap;
	return im;
}

extern "C"
{

static PyObject *Py_OnePassColors( PyObject *self, PyObject *args )
{
	char* bufferH;
	int lenH;
	float waterLevel;
	float lightDir[3];
	unsigned char* out;
	PyObject *pRet ;
	PyObject *pWGrad ;
	PyObject *pLGrad ;
	int bLight;
	int xSize, ySize;
	if (!PyArg_ParseTuple(args, "i(ii)fs#OO(fff)", &bLight,&ySize,&xSize, &waterLevel, &bufferH, &lenH, &pWGrad,&pLGrad,&lightDir[0], &lightDir[1],&lightDir[2] ) )
        return NULL;
	Py_BEGIN_ALLOW_THREADS
	out = ( unsigned char*)OnePassColors( bLight, xSize, ySize, waterLevel, (float*)bufferH, Gradient( pWGrad ), Gradient( pLGrad ), lightDir );
	Py_END_ALLOW_THREADS
	pRet = Py_BuildValue( "s#", out, xSize*ySize*3 ); 
	free( out );
    return pRet;
}

static PyObject* Py_GenerateImage( PyObject *self, PyObject *args )
{
	int xSize,ySize,lenH,lenC;
	char* bufH;
	char* bufC;
	unsigned char* out;
	float waterLevel;
	int xmin,ymin,xmax,ymax;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "f(ii)s#s#", &waterLevel,&ySize,&xSize,&bufH,&lenH,&bufC,&lenC))
        return NULL;
	out = GenerateImage( waterLevel,xSize, ySize,(float*)bufH,(unsigned char*)bufC,&xmin,&ymin,&xmax,&ymax );
	pRet = Py_BuildValue( "iiiis#", xmin,ymin,xmax,ymax,out,514*428*6 ); 
	free( out );	
    return pRet;
}

static PyObject* PyT_GetVersion( PyObject *self, PyObject *args )
{
	PyObject* pRet;
	pRet = Py_BuildValue( "s", "v1.0d" );
	return pRet;
}

static PyMethodDef tools3DMethods[] =
{
	{"onePassColors", Py_OnePassColors, METH_VARARGS, "generate color map" },
	{"generateImage", Py_GenerateImage, METH_VARARGS, "generate thumbs" },
	{"GetVersion", PyT_GetVersion,METH_VARARGS,"get dll version" },
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC inittools3D(void)
{
    (void) Py_InitModule("tools3D", tools3DMethods);
}

}
