import copy
import random

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
from plotly import graph_objs as go
import numpy as np

import db

with open('conf/mapbox', 'r') as f:
  access_key = f.read().rstrip('\n')

max_hrs = 24*5
spds = np.array([db.car_speeds(h) for h in range(max_hrs)])
lat = spds[:, :, 0]
lon = spds[:, :, 1]
spd = spds[:, :, 2]
spd_std = np.std(spd)
spd_mean = np.mean(spd)
min_val = spd_mean-2*spd_std
max_val = spd_mean+2*spd_std
spd_colour = (spd-min_val)/(max_val-min_val)*255
spd_colour = spd_colour.clip(0.0, 255.0)
spd_colour_txt = [ ['rgb({:f}, 0.0, {:f})'.format(x, (255.0-x)) for x in hour] for hour in spd_colour]


weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def div():
  return html.Div([
    dcc.Graph(
      id='car-speeds-graph'
    ),
    html.Span([
      html.H1('Car speeds', className='unselectable', style={'float':'left'}),
      html.Div([
        html.P(id='car-speed-information'),
        dcc.Slider(
          id='car-speeds-slider',
          min=0,
          max=max_hrs-1,
          value=0,
          marks={
            (idx*24+12): {'label': weekdays[idx]} for idx in range(5)
          }
        )
      ], style={'width': 'calc(100% - 430px)', 'margin-left': '270px'}),
      html.Span([
        html.Button(id='left-button', className='fas fa-chevron-circle-left fa-sm', style={'float': 'left'}),
        html.Button(id='right-button', className='fas fa-chevron-circle-right fa-sm', style={'float': 'right'})
      ], style={'float': 'right', 'width': '125px', 'padding-right': '10px', 'margin-top': '-30px'})
    ], className='moderate-text unselectable')
  ], style={'height': '100%'})

default_layout = {
  'autosize':True,
  'margin':{'l':0, 'r':0, 't':0, 'b':0},
  'mapbox':{
    'accesstoken': access_key,
    'center': {'lat': np.mean(lat), 'lon': np.mean(lon)},
    'style': 'dark',
    'bearing': 0,
    'zoom': 11
  }
}

def callbacks(app):
  @app.callback(
    Output('car-speed-information', 'children'),
    [Input('car-speeds-slider', 'value')])
  def show_time(h):
    day_str = weekdays[h//24]
    hr_in_day = h%24
    return '{:s} {:02d}:00'.format(day_str, hr_in_day)

  @app.callback(
    Output('car-speeds-graph', 'figure'),
    [Input('car-speeds-slider', 'value')],
    [State('car-speeds-graph', 'relayoutData')])
  def show_dots(h, prev_layout):
    layout = copy.deepcopy(default_layout)
    if prev_layout is not None:
      if 'mapbox.zoom' in prev_layout:
        layout['mapbox']['zoom'] = prev_layout['mapbox.zoom']
      if 'mapbox.bearing' in prev_layout:
        layout['mapbox']['bearing'] = prev_layout['mapbox.bearing']
      if 'mapbox.pitch' in prev_layout:
        layout['mapbox']['pitch'] = prev_layout['mapbox.pitch']
      if 'mapbox.center' in prev_layout:
        layout['mapbox']['center'] = prev_layout['mapbox.center']
    return {
      'data': [
        go.Scattermapbox(
          lat=lat[h],
          lon=lon[h],
          mode='markers',
          text=spd[h],
          marker={
            'color': spd_colour_txt[h],
            'size': 15
          }
        )
      ],
      'layout': layout
    }

  @app.callback(
    Output('car-speeds-slider', 'value'),
    [],
    [State('car-speeds-slider', 'value'),
     State('left-button', 'n_clicks_timestamp'),
     State('right-button', 'n_clicks_timestamp')],
    [Event('left-button', 'click'),
     Event('right-button', 'click')])
  def inc_slider(curr, left_time, right_time):
    if right_time is None:
      return (curr - 1) % max_hrs
    if left_time is None:
      return (curr + 1) % max_hrs
    if right_time < left_time:
      return (curr - 1) % max_hrs
    return (curr + 1) % max_hrs

