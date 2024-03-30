# Building and running separately to avoid unnecessary rebuilds
# vs. docker-compose up --build
start:
	docker build --build-arg UPDATE_CONDA=false -t ds-and-ml . && docker-compose up -d
