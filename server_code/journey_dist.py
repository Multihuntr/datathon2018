import collections

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
from plotly import graph_objs as go
import numpy as np

import db
import mapbox


def get_stops_dict():
  stops = db.stops()
  d = {}
  for stop_id, name, lat, lon in stops:
    d[stop_id] = {'name': name, 'lat': lat, 'lon': lon}
  return d

stops_dict = get_stops_dict()
stops_opt = [{'label': s['name'], 'value': k} \
  for k, s in list(stops_dict.items())[:200]]

def to_colour_text(ar, low=3, hi=97):
  # ar = np.log2(ar)
  # std_ = np.std(ar)
  # mean_ = np.mean(ar)
  min_ = np.percentile(ar, low)
  max_ = np.percentile(ar, hi)
  colour = (ar-min_)/(max_-min_)*255
  colour = colour.clip(0.0, 255.0)
  return ['rgb({:f}, 0.0, {:f})'.format(x, (255.0-x)) for x in colour]

def there_are_nones(journey):
  for _, _, stops in journey:
    for id_, dist in stops:
      if dist is None:
        return True
  return False

def aggregate_from(stop_id, disp_only=None):
  aggregates = collections.defaultdict(lambda: {
    'total_time_to': 0.0,
    'people': 0
  })
  journeys = db.journeys_about(stop_id)
  nearby_stops = db.nearby_stops(stop_id)
  # There are 4 cases
  #  x stop,    - by bus,    = rest of journey
  # Journey: x ---- x == x ---- x
  #          1      2    3      4
  # We ignore case 2/3
  for idx, (journey_id, journey) in enumerate(journeys):
    if disp_only is not None and idx > disp_only:
      print('Breaking on', idx)
      break
    if disp_only is not None and idx < disp_only:
      print('Skipping', idx)
      continue

    # Quick check to see if there are Nones in the journey
    if there_are_nones(journey):
      print('Skipping', idx, 'because of a None.')
      continue
    # print('{:06d}'.format(idx), end='\r', flush=True)
    # print(journey_id, journey)
    first_stop_id, last_stop_id = journey[0][2][0][0], journey[-1][2][-1][0]
    # print(first_stop_id, stop_id, nearby_stops)
    forward = first_stop_id==stop_id or first_stop_id in nearby_stops
    backward = last_stop_id==stop_id or last_stop_id in nearby_stops
    if not (forward or backward):
      # print('Skipping', idx, 'because it\'s in the middle')
      continue
    total_time = sum(x[1] for x in journey)
    o_stop_ids = []
    dists = []
    journey_dist = 0
    for trip_id, leg_time, stops in journey:
      leg_o_stop_ids, leg_dists = zip(*stops)
      leg_dists = np.array(leg_dists)
      leg_dists -= np.min(leg_dists)
      leg_dists += journey_dist
      journey_dist += np.max(leg_dists)
      o_stop_ids.extend(leg_o_stop_ids)
      dists.extend(leg_dists.tolist())
    dists = np.array(dists)
    times_to = dists / journey_dist * total_time
    # If the journey is ending at the stop, then reverse the times
    if not forward:
      times_to = total_time - times_to
    # print(forward)
    # print(total_time)
    # print(o_stop_ids)
    # print(times_to)
    # print('=-=-=-=-=-=+_+_+_+_=-=-=_+-+-=-=-=-=-=-+-+-+-+-+-+-+-')
    for o_stop_id, time_to in zip(o_stop_ids, times_to):
      aggregates[o_stop_id]['total_time_to'] += time_to
      aggregates[o_stop_id]['people'] += 1
  return aggregates

def obtain_stop_data(stop_id, disp_only=None):
  aggregates = aggregate_from(stop_id, disp_only)
  ids = []
  lats = []
  lons = []
  times = []
  peoples = []
  for k, v in aggregates.items():
    ids.append(k)
    lats.append(stops_dict[k]['lat'])
    lons.append(stops_dict[k]['lon'])
    times.append(v['total_time_to'])
    peoples.append(v['people'])
  return ids, lats, lons, times, peoples

def div():
  return html.Div([
    html.Div([
      html.H1(
        'Journey Distances',
        className='moderate-text unselectable',
        style={'float':'left'}),
      html.H3(
        'Select some stops to filter',
        className='moderate-text unselectable',
        style={'float':'right'}
      ),
      dcc.Dropdown(id='journey-selected-stops',
        placeholder='Select a stop to map journey distance/times...'),
    ], style={'height': '50px'}),
    dcc.Graph(
      id='journey-dist-graph'
    )
  ], style={'height': '100%'})

def show_stops(prev_layout):
  texts = []
  lats = []
  lons = []
  for k,v in stops_dict.items():
    texts.append('{:d};{:s}'.format(k,v['name']))
    lats.append(v['lat'])
    lons.append(v['lon'])
  return {
    'data': [
      go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        text=texts
      )
    ],
    'layout': mapbox.layout(prev_layout)
  }

def callbacks(app):
  @app.callback(
    Output('journey-dist-graph', 'figure'),
    [Input('journey-selected-stops', 'value')],
    [State('journey-dist-graph', 'selectedData'),
     State('journey-dist-graph', 'relayoutData')])
  def disp_journeys(one_selected, selected, prev_layout):
    if one_selected is None:
      return show_stops(prev_layout)
    one_selected = int(one_selected)
    ids, lats, lons, times, peoples = obtain_stop_data(one_selected, None)
    times = np.array(times)
    peoples = np.array(peoples)
    avgs = times/peoples
    txt = ['{:d} ; {:5.2f} | {:d}'.format(id_, avg, people) \
      for id_,avg,people in zip(ids, avgs, peoples)]
    time_colour_txt = to_colour_text(avgs)
    layout = mapbox.layout(prev_layout)
    return {
      'data': [
        go.Scattermapbox(
          lat=(stops_dict[one_selected]['lat'],),
          lon=(stops_dict[one_selected]['lon'],),
          mode='markers',
          text='Ref',
          marker={
            'color': 'green',
            'size': 30
          }
        ),
        go.Scattermapbox(
          lat=lats,
          lon=lons,
          mode='markers',
          text=txt,
          marker={
            'color': time_colour_txt,
            'size': 10
          }
        )
      ],
      'layout': layout
    }

  @app.callback(
    Output('journey-selected-stops', 'options'),
    [Input('journey-dist-graph', 'selectedData')])
  def disp_stops(selected):
    opts = []
    if selected is None or 'points' not in selected:
      opts = stops_opt
    else:
      for p in selected['points']:
        id_, _ = p['text'].split(';')
        opts.append({'label': stops_dict[int(id_)]['name'], 'value': id_})
    return opts


if __name__ == '__main__':
  a = obtain_stop_data(7093)
