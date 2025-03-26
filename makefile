# Use this makefile to 1) download the right sheet, 2) run the authorship wrangler.
# Then put \include{authors.tex} into your main.tex and call it a day :)
# Usage: make authors
# Author: Calvin Leung

PATH_TO_PAPER='/Users/kiyo/working/outrigger-overview-paper'
PATH_TO_AUTHORSHIP_REPO=`pwd`
AUTHOR_URL="https://docs.google.com/spreadsheets/d/1ul1W1ZCgfLSmvVmRkNAw4uw1KmOIEh-SrBW00KStl3Y"


authors:
	curl -L $(AUTHOR_URL)"/export?gid=0&format=tsv" > $(PATH_TO_PAPER)/authors.tsv
	curl -L $(AUTHOR_URL)"/export?gid=2085366068&format=tsv" > $(PATH_TO_PAPER)/affils.tsv
	python $(PATH_TO_AUTHORSHIP_REPO)/authors.py $(PATH_TO_PAPER)/authors.tsv $(PATH_TO_PAPER)/affils.tsv --discard 1 > $(PATH_TO_PAPER)/authors.tex
