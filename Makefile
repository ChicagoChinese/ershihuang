build:
	cd site; hugo

server:
	cd site; hugo server --baseURL http://127.0.0.1 --buildDrafts --buildFuture --navigateToChanged

generate:
	python generate.py

new:
	python new-translation.py

all:
	python generate-all.py
