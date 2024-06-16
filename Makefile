.PHONY: recreatedb
recreatedb:
	rm -f db.sqlite3
	poetry run python eda/manage.py migrate
	poetry run python eda/manage.py createsuperuser

.PHONY: docker
docker:
	docker buildx build -f Dockerfile --platform linux/amd64 --push -t ghcr.io/askvrtsv/eda:latest .