.PHONY: recreatedb
recreatedb:
	rm -f db.sqlite3
	poetry run python eda/manage.py migrate
	poetry run python eda/manage.py createsuperuser
