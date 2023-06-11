build:
	cd site; hugo

server:
	cd site; hugo server --baseURL http://127.0.0.1 --buildDrafts --navigateToChanged

generate:
	python generate.py
