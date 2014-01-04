#!/usr/bin/python
 
from appscript import *
 
 
def fix_itunes_names():
    iTunes = app(u'/Applications/iTunes.app')
    selection = iTunes.windows[1].selection.get()
 
    for track in selection:
        track.artist.set( track.artist().strip() )
        track.name.set( track.name().strip() )
        track.album.set( track.album().strip() )
 
if __name__ == '__main__':
    fix_itunes_names()
