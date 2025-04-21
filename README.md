# authorship
A little script to wrangle CHIME/FRB author lists

Here is a Google Sheets template you can use for authors to sign up:
https://docs.google.com/spreadsheets/d/1AJSt2wNmhyU-DhWLPmaiFRoPkTuKINc68Ij4x937EKg/edit

When you are ready, open each of the two sheets (Authors and
Affiliations), and go to File->Download->Tab Separated Values and save the two TSV files.

Then run
```
python3 authors.py authors.tsv affils.tsv > auth.tex
```

For a demo of what it will look like, run
```
pdflatex apj
pdflatex apj
```

In Overleaf or wherever you are writing your paper, it is usually easiest to include the `auth.tex` file (using `\input{auth.tex}`); see the example `apj.tex` file for a usage example.

Usually we end up reorganizing the acknowledgments by hand, to put institutional ones first, followed by alphabetical individual acknowledgments.

NOTE: if this is a first author paper there is a ```--num_ordered``` flag which tells the script how many are already ordered correctly
