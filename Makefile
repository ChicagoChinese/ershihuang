build:
	cd site; hugo

server:
	cd site; hugo server --buildDrafts --navigateToChanged

generate:
	python generate.py
