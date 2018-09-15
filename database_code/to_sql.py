import csv
import collections
import datetime
import json
import os
import math
import subprocess
import sys

import psycopg2
import psycopg2.extras

import db


running_stats = collections.defaultdict(lambda: 0)


def parse_date(date_str):
  return datetime.datetime.strptime(date_str,  '%Y-%m-%d %H:%M:%S')

seen_strings = []
def index_int(s):
  try:
    return int(s)
  except:
    if s in seen_strings:
      i = seen_strings.index(s)
    else:
      i = len(seen_strings)
      seen_strings.append(s)
    return -i

def seen_strings_gen():
  for i, s in enumerate(seen_strings):
    yield '{:s},{:s}'.format(i,s)
sql_parent = "INSERT INTO parent_routes VALUES(%s)"

type_names = ['Mode','BusinessDate','DateTime','CardID','CardType','VehicleID','ParentRoute','RouteID','StopID']
types =      [   int,          None,parse_date,     int,       int,        int,    index_int,      int,     int]
column_names = ['mode', 'ts', 'card_id', 'card_type', 'vehicle_id', 'parent_route', 'route_id', 'stop_id']

def get_rows(in_file):
  global running_stats
  stop_id_matching = dict(db.stop_id_matching())
  stop_ids = set(db.stop_ids())
  rows = []
  with open(in_file) as in_f:
    reader = csv.reader(in_f, delimiter='|')
    for idx, line in enumerate(reader):
      print('               {:8d}'.format(idx), end='\r', flush=True)
      parsed_line = [t(v) for (t,v) in zip(types, line) if t is not None]
      row = dict(zip(column_names, parsed_line))
      # Some stops are in the myki data that are not in the gtfs data
      if row['stop_id'] in stop_id_matching:
        row['stop_id'] = stop_id_matching[row['stop_id']]
      # If we can't find anything that matches, then we can't possibly use this line
      if row['stop_id'] not in stop_ids:
        running_stats['w_no_stop'] += 1
        continue
      rows.append(row)
  return rows

def combine_touches(ons, offs):
  touches = collections.defaultdict(lambda: [])

  for on in ons:
    on['on'] = True
    touches[on['card_id']].append(on)

  for off in offs:
    off['on'] = False
    touches[off['card_id']].append(off)

  return touches

def time_diff(a, b):
  return abs((a-b).total_seconds())

seconds_two_hours = 2*60*60
seconds_half_hour = 0.5*60*60
def chains_by_card(card):
  '''
  Creates a list of chains.
  A chain is defined as temporally consecutive pairs of (touchon, touchoff)

  Args:
      card (list(touch)): list of touches card has made

  Returns:
      list(list((touchon, touchoff))): temporally consecutive legs of journey
  '''
  global running_stats
  card.sort(key=lambda v: v['ts'])
  chains = []
  chain = []
  for x in range(len(card)-1):
    # If they changed their mind
    if card[x]['stop_id'] == card[x+1]['stop_id']:
      continue
    # If we have a pair within 2 hours, add it to the chain else,
    # if it's more than 30 minutes between the current touch and the next
    # then keep the chain going (assuming it goes off->on for this step)
    if card[x]['on'] and not card[x+1]['on'] \
        and time_diff(card[x]['ts'], card[x+1]['ts']) < seconds_two_hours:
      chain.append((card[x], card[x+1]))
    elif not (not card[x]['on'] and card[x+1]['on']
        and time_diff(card[x]['ts'], card[x+1]['ts']) < seconds_half_hour):
      if len(chain) > 0:
        if len(chain) > 1:
          running_stats['starting_multi_chains'] += 1
        running_stats['starting_chains'] += 1
        chains.append(chain)
        # New chain
        chain = []
  return chains

def chains_by_timing(touches):
  chains = []
  for card_id, card in touches.items():
    chains.extend(chains_by_card(card))
  return chains

def chains_by_consecutive_dist(chains):
  global running_stats
  out_chains = []
  for idx, chain in enumerate(chains):
    print('        {:7d}'.format(idx), end='\r', flush=True)
    start = 0
    for x in range(len(chain)-1):
      a = chain[x][1]['stop_id']
      b = chain[x+1][0]['stop_id']
      if not db.stop_dist(a, b, 600):
        running_stats['distance_breakages'] += 1
        out_chains.append(chain[start:x+1])
        start = x+1
    out_chains.append(chain[start:])
  return out_chains

def chains_by_matching_trip(chains):
  '''
  Removes legs of chain that do not have stops in the same trip

  Args:
      chains (list(list((touchon, touchoff)))): Legs of potential journey
  '''
  global running_stats
  out_chains = []
  for idx, chain in enumerate(chains):
    print('        {:7d}'.format(idx), end='\r', flush=True)
    new_chain = []
    for x in range(len(chain)):
      trip_id, a_seq, b_seq = a_valid_trip(*chain[x])
      if trip_id is None:
        running_stats['trip_breakages'] += 1
      if trip_id is not None:
        new_chain.append((trip_id, a_seq, b_seq, *chain[x]))
      elif len(new_chain) > 0:
        out_chains.append(new_chain)
    if len(new_chain) > 0:
      out_chains.append(new_chain)
  return out_chains

def a_valid_trip(touchon, touchoff):
  '''
  Args:
      touchon (dict): myki transaction
      touchoff (dict): myki transaction

  Returns:
      trip_id: a valid trip id given the two transactions
      touchon_seq: the sequence number of touchon stop in trip
      touchoff_seq: the sequence number of touchoff stop in trip
  '''
  hits = db.stops_share_trip(touchon['stop_id'], touchon['ts'],
          touchoff['stop_id'], touchoff['ts'])
  if len(hits) > 0:
    return hits[0]
  return None, None, None

def load_files(on_file, off_file):
  '''Loads the files from disk as chains of journey legs'''
  ons = get_rows(on_file)
  offs = get_rows(off_file)
  # Touches grouped by card
  card_touches = combine_touches(ons, offs)
  chains = chains_by_timing(card_touches)
  chains = chains_by_consecutive_dist(chains)
  chains = chains_by_matching_trip(chains)
  return chains

def chain_to_rows(chain):
  return [(leg[0],
           leg[3]['stop_id'],
           leg[4]['stop_id'],
           leg[1],
           leg[2],
           (leg[4]['ts']-leg[3]['ts']).total_seconds()) for leg in chain]

def journey_rows(root):

  on_fol =  "ScanOnTransaction"
  off_fol = "ScanOffTransaction"

  for sample in range(0, 10):
    sample_dir = 'Samp_{:d}'.format(sample)
    for year in range(2018, 2019):
      for week in range(16, 54):
        print('                         Samp_{:d} : {:d}-Week{:d}'.format(sample, year, week), end='\r', flush=True)
        on_dir   = os.path.join(root, sample_dir,  on_fol, str(year), "Week{:d}".format(week))
        off_dir  = os.path.join(root, sample_dir, off_fol, str(year), "Week{:d}".format(week))
        if not os.path.isdir(on_dir):
          continue
        on_file  = os.path.join(on_dir,   os.listdir(on_dir)[0])
        off_file = os.path.join(off_dir, os.listdir(off_dir)[0])
        chains = load_files(on_file, off_file)
        for chain in map(chain_to_rows, chains):
          yield chain

if __name__ == '__main__':

  conn = db.new_connection()
  cur = conn.cursor()

  root = sys.argv[1]

  rows = journey_rows(root)

  sql_journey = 'INSERT INTO journey VALUES(default) RETURNING journey_id;'
  sql_leg = 'INSERT INTO journey_leg VALUES(' + ', '.join(['%s']*9) + ');'

  for idx, row in enumerate(rows):
    print('{:7d}'.format(idx), end='\r', flush=True)
    cur.execute(sql_journey)
    journey_id = cur.fetchone()
    for leg_idx, leg in enumerate(row):
      first_last = leg_idx == 0 or leg_idx == len(row)-1
      cur.execute(sql_leg, journey_id+(leg_idx,first_last)+leg)

  conn.commit()
  conn.close()

  with open('running_stats.json', 'w') as f:
    json.dump(running_stats, f)
    f.write('\n')