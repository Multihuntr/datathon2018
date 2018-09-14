import collections
import numpy as np

def stop_dict(routes_dict):
  '''
  Produces a dictionary look-up for the stops in routes_dict

  Args:
      routes_dict (dict(route_id->list((stop_id, seq_no, dist)))): hashed
          access to route information

  Returns:
      dict(stop_id->list((route_id, innerIdx))): hashed access to routes
        from a stop
  '''
  d = collections.defaultdict(lambda: [])
  for route_id, route in routes_dict.items():
    for inner_idx, (stop_id, _, _) in enumerate(route):
      d[stop_id].append((route_id, inner_idx))
  return d

def as_dict(the_list, key_idxs=1):
  '''
  Produces a dictionary look-up for `the_list`

  Args:
      the_list (list): list of primitive values
      key_idxs (int, optional): how many indices to take off the front as keys
  '''
  d = collections.defaultdict(lambda: [])
  for thing in the_list:
    d[thing[:key_idxs]].append(thing[key_idxs:])
  return d

def route_dict(routes_list):
  '''
  Produces a dictionary look-up for routes.
  Elements of the dictionary are sorted by seq_no

  Args:
      routes_list (list((route_id, stop_id, seq_no, dist))): flat

  Returns:
      dict(route_id->list((stop_id, seq_no, dist))): hashed
        access to route information
  '''
  d = as_dict(routes_list)
  for k, v in d.items():
    v.sort(key=lambda x: x[1])
  return d


def intersection_dict(intersection_list):
  '''
  Produces a dictionary look-up for intersections

  Args:
      intersection_list (list(route_id1, route_id2,
          stop_id1, stop_id2, seq_no1, seq_no2)): flat list

  Returns:
      dict((route_id1, route_id2)->list((stop_id1, stop_id2, seq_no1, seq_no2))): Description
  '''
  return as_dict(intersection_list, 2)


def intersection(a, b, t=200):
  c = np.array([(x.lat, x.lon) for x in a])
  d = np.array([(x.lat, x.lon) for x in b])
  dists = to_metres(c[:, None], d[None])
  idx = np.argmin(dists)
  if dists[idx] < t:
    return tuple(idx)
  return None, None

# Radius of earth in metres
R = 6371000
def to_metres(x, y):
  # https://www.movable-type.co.uk/scripts/latlong.html
  x_lat = np.deg2rad(x[..., 0])
  y_lat = np.deg2rad(y[..., 0])
  lat = np.deg2rad(y[..., 0] - x[..., 0])
  lon = np.deg2rad(y[..., 1] - x[..., 1])
  a = np.sin(lat/2) * np.sin(lat/2) + \
      np.cos(x_lat) * np.cos(y_lat) + \
      np.sin(lon/2) * math.sin(lon/2)
  c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
  return R * c

def interpolate_time(path, time, offset=0):
  dists = np.array([x.dist for x in path])
  total_dist = np.sum(dists)
  prop = dists/total_dist
  return prop*time + offset

def mk_path(route, a, b):
  s = min(a, b)
  e = max(a, b)
  return route[s:e]

def paths(stop_id, stops, routes, intersections, legs):
  '''
  Generator for path segments, given a generator of legs of journeys.
  Only produces paths when legs are in adjacent routes
  (3+ step journeys ignored; under the assumption breadth-first searching
  of all routes would be too computationally expensive)

  Args:
      stop_id (int): Starting stopId
      stops (dict(stopId->list((routeId, innerIdx)))): All stops with their associated
              routes and their index location within those routes
      routes (dict(routeId->(list((stopId, dist))))): Each route has
              all stops and their distance along the route
      intersections (dict((routeId1, routeId2)->list((stopId1, stopId2)))): Routes
              that have intersections, lists the bounds of those intersections
      legs (gen(stopId, time)): A generator for the other stops people have gone to

  Yields:
      list(stopId, dist), list(time): (Part of) a single person's path
  '''
  stopId_a = stopId
  routeId_a, idx_a = stops[stopId_a]
  route_a = routes[routeId_a]
  for stopId_b, time in legs:
    routeId_b, idx_b = stops[stopId_b]
    if routeId_b == routeId_a:
      path = mk_path(route_a, idx_a, idx_b)
      yield path, interpolate_time(path, time)
    else:
      pair = (routeId_a, routeId_b)
      if pair in intersections:
        route_b = routes[routeId_b]
        s1, s2 = intersections[pair]
        path1 = mk_path(route_a, idx_a, s1)
        path2 = mk_path(route_b, s2, idx_b)
        dist1 = path_dist(path1)
        dist2 = path_dist(path2)
        tot_dist = dist1+dist2
        time1 = time*dist1/tot_dist
        time2 = time*dist2/tot_dist
        yield path1, interpolate_time(path1, time1)
        yield path2, interpolate_time(path2, time2, time1)

def aggregate_paths(paths):
  stop_info = {}
  for path in paths:
    pass