echo -n "Choose db password: "
read -s password
echo $password > conf/pass
psql --file=create_database.sql
psql -c "alter user loader with password '$password';"
psql --file=../auxillary/gtfs/gtfs.sql --dbname=myki
psql --file=myki.sql --dbname=myki
psql --file=car.sql --dbname=myki

python3 car_speeds_to_sql.py $1/car_speeds/melbourne_vehicle_traffic.csv

python3 unzip.py ../auxillary

pushd ../auxillary/gtfs
for i in $(ls -d ./*/); do
  pushd $i && psql --file=../gtfs_load.sql --dbname=myki && popd
done
popd
psql --file=../auxillary/gtfs/to_gis.sql --dbname=myki
psql --file=../auxillary/gtfs/stop_times_calendar.sql --dbname=myki
psql --file=myki_gtfs_correspondence.sql --dbname=myki

psql --file=permissions.sql --dbname=myki

python3 unzip.py $1
python3 to_sql.py $1



