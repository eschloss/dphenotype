web: bin/start-nginx bin/start-pgbouncer uwsgi uwsgi.ini
worker: bin/start-pgbouncer newrelic-admin run-program celery worker -A eschadmin -l info --without-gossip --autoscale=3,1
