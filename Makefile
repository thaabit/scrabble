restart:
	make stop && make build && make run

build:
	docker-compose build

run:
	docker-compose up

stop:
	docker-compose down

test:
	docker-compose run api pytest -v
