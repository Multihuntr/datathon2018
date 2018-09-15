import collections

import db

import numpy as np

def get_stops_dict():
  stops = db.stops()
  d = {}
  for stop_id, lat, lon in stops:
    d[stop_id] = {'lat': lat, 'lon': lon}
  return d

stops_dict = get_stops_dict()

def aggregate_from(stop_id):
  aggregates = collections.defaultdict(lambda: {
    'total_time_to': 0.0,
    'people': 0
  })
  journeys = db.journeys_about(stop_id)
  for idx, journey in enumerate(journeys):
    print('{:06d}'.format(idx), end='\r', flush=True)
    for trip_id, leg_time, stops in journey:
      o_stop_ids, dists = zip(*stops)
      dists = np.array(dists)
      dists -= np.min(dists)
      times_to = dists / np.max(dists) * leg_time
      for o_stop_id, time_to in zip(o_stop_ids, times_to):
        aggregates[o_stop_id]['total_time_to'] += time_to
        aggregates[o_stop_id]['people'] += 1
  return aggregates

def obtain_stop_data(stop_id):
  aggregates = aggregate_from(stop_id)
  lats = []
  lons = []
  times = []
  peoples = []
  for k, v in aggregates.items():
    lats.append(stops_dict[k]['lat'])
    lons.append(stops_dict[k]['lon'])
    times.append(v['total_time_to'])
    peoples.append(v['people'])
  return lats, lons, times, peoples

if __name__ == '__main__':
  a = obtain_stop_data(7093)
