# To run tests: make ADMIN_USER=user ADMIN_PASSWORD=pass test

test:
	curl -XDELETE "http://${ADMIN_USER}:${ADMIN_PASSWORD}@localhost:5984/nvpy-test"
	curl -XPUT "http://${ADMIN_USER}:${ADMIN_PASSWORD}@localhost:5984/nvpy-test"
	python2 nvpy/couchdb_remote_test.py

clean-test:
	curl -XDELETE "http://${ADMIN_USER}:${ADMIN_PASSWORD}@localhost:5984/nvpy-test"
