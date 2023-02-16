web: bin/start-nginx bin/start-pgbouncer uwsgi uwsgi.ini
worker: bin/start-pgbouncer celery -A config worker -l info --without-gossip --autoscale=3,1 --without-heartbeat

