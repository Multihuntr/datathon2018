# An awkward folder structure

Either positively describable as an organic evolution of folders based on requirements, or negatively as an admittedly poorly planned folder structure

## auxillary

You should extract the gtfs zip from [data.vic.gov](https://www.data.vic.gov.au/data/dataset/ptv-timetable-and-geographic-information-2015-gtfs) directly in this folder such that you have folders numbered `//auxillary/gtfs/1/` with an `agency.txt`, `stop_times.txt` and [all that jazz](https://developers.google.com/transit/gtfs/reference/). The scripts in this folder are for loading the gtfs data into the database (but not really processing it)

## docker

Dockerfile descriptions of required software for each of the database and presentation server.

## database_code

This is where all the \*.sql, \*.sh and \*.py files are kept that are used to load the database from the `auxillary` folder and where ever the myki touch data is. It includes files that loads the myki data. At no point do we store all of the touchon/touchoff data. We can always read it again, anyway, and it ends up taking up a lot of harddrive space when we're not going to use it.

Running `database_code/init.sh location/of/myki/touch/data` should populate the database (although it will take a few days to load **ALL** the myki data, as it attempts to find journeys based on the touchon/touchoff information, and I couldn't get it any faster).

## server_code

This is where the [dash](https://dash.plot.ly/) application lives. It reads from the database created by `database_code/init.sh`
