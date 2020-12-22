build:
	docker build -t registry.antonskvortsov.com/eda .
	docker push registry.antonskvortsov.com/eda
	ssh antonskvortsov.com docker pull registry.antonskvortsov.com/eda
