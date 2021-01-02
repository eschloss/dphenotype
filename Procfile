web: bin/start-nginx bin/start-pgbouncer-stunnel uwsgi uwsgi.ini
worker: bin/start-pgbouncer-stunnel newrelic-admin run-program celery worker -A eschadmin -l info --without-gossip --autoscale=3,1
