FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
  postgresql-contrib=10+190 \
  postgresql=10+190 \
  postgresql-10-postgis-2.4=2.4.3+dfsg-4 \
  postgresql-10-postgis-scripts=2.4.3+dfsg-4

RUN apt-get install -y unzip python3-pip
RUN pip3 install psycopg2-binary

RUN ln -fs /usr/share/zoneinfo/Australia/Melbourne /etc/localtime && \
  dpkg-reconfigure -f noninteractive tzdata

RUN usermod -u 123 postgres && \
  groupmod -g 128 postgres && \
  find / -path /proc -prune -o -uid 101 -exec chown -h 123 {} + && \
  find / -path /proc -prune -o -gid 103 -exec chgrp -h 128 {} +

RUN /usr/share/locales/install-language-pack en_AU.UTF-8

RUN echo "host    myki            loader          172.17.0.1/32           trust" >> /etc/postgresql/10/main/pg_hba.conf && \
    echo "host    myki            loader          172.17.0.3/32           trust" >> /etc/postgresql/10/main/pg_hba.conf

ADD postgresql.conf /etc/postgresql/10/main/postgresql.conf

# USER postgres

CMD service postgresql start && bash