import copy

with open('conf/mapbox', 'r') as f:
  access_key = f.read().rstrip('\n')

default_layout = {
  'autosize':True,
  'margin':{'l':0, 'r':0, 't':0, 'b':0},
  'mapbox':{
    'accesstoken': access_key,
    'center': {'lat': -37.813629, 'lon': 144.963058},
    'style': 'dark',
    'bearing': 0,
    'zoom': 11
  },
  'showlegend': False
}

def layout(p):
  layout_ = copy.deepcopy(default_layout)
  if p is not None:
    if 'mapbox.zoom' in p:
      layout_['mapbox']['zoom'] = p['mapbox.zoom']
    if 'mapbox.bearing' in p:
      layout_['mapbox']['bearing'] = p['mapbox.bearing']
    if 'mapbox.pitch' in p:
      layout_['mapbox']['pitch'] = p['mapbox.pitch']
    if 'mapbox.center' in p:
      layout_['mapbox']['center'] = p['mapbox.center']
  return layout_