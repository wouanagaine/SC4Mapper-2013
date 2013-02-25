"""
This implement the about box by using html window and the about box when displaying the 'coppyrigh' in SC4M files
"""
import sys

import wx                  # This module uses the new wx namespace
import wx.html
import wx.lib.wxpTag
import os
import webbrowser


class MyHtmlWindow(wx.html.HtmlWindow):
    """ just subclassing to make link open in the default user webbrowser"""
    def __init__(self, parent, id, size):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size,style=wx.NO_FULL_REPAINT_ON_RESIZE)

    def OnLinkClicked(self, linkinfo):
      webbrowser.open_new( linkinfo.GetHref() )


class AuthorBox( wx.Dialog ):
  def __init__( self, parent, htmlText ):
    """ display author note about the SC4M file"""
    wx.Dialog.__init__(self, parent, -1, 'SC4M Author notes',)
    html = MyHtmlWindow(self, -1, size=(420, -1))
    #html.LoadPage( "about.html" )
    print type( htmlText )
    html.SetPage( htmlText )

    btn = html.FindWindowById(wx.ID_OK)
    ir = html.GetInternalRepresentation()
    html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
    self.SetClientSize(html.GetSize())
    self.CentreOnParent(wx.BOTH)
      