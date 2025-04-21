import re
import numpy as np

def debug(*args):
    import sys
    print(*args, file=sys.stderr)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('auth_tsv')
    parser.add_argument('affil_tsv')
    parser.add_argument('--discard', type=int, default=3,
                        help='Number of lines to discard from the top of the authors spreadsheet, default %(default)')
    parser.add_argument('--discard-affil', type=int, default=1,
                        help='Number of lines to discard from the top of the affiliations spreadsheet, default %(default)')
    parser.add_argument('--num_ordered', type=int, default=1,
                        help='The number of authors in the list that are already ordered correctly (first author paper)')


    # Here we assume the spreadsheet has columns (with the last one optional):
    #
    # Lastname  |  First names  |  x  |  x  |  ORCID  |  Affiliations  |  Inst Acks  |  Personal Acks  |  ...
    #
    parser.add_argument('--lastname_index', type=int, default=0,
                        help='Index of author last name in spreadsheet')
    parser.add_argument('--firstname_index', type=int, default=1,
                        help='Index of author non-last names in spreadsheet')
    parser.add_argument('--orcid_index', type=int, default=4,
                        help='Index of author ORCID in spreadsheet')
    parser.add_argument('--affil_index', type=int, default=5,
                        help='Index of author affiliation acronyms in spreadsheet')
    parser.add_argument('--ack_index', type=int, default=6,
                        help='Index of institutional acknowledgements in spreadsheet')
    parser.add_argument('--persack', type=bool, default=False,
                        help='If True, there is a separte column for personal acknowledgements on top of institutional ones.')
    parser.add_argument('--persack_index', type=int, default=7,
                        help='Index of personal acknowledgements in spreadsheet')

    opt = parser.parse_args()

    # Export Google spreadsheet as TSV...
    f  = open(opt.auth_tsv) #'authors-cat.tsv'
    f2 = open(opt.affil_tsv) #'affils-cat.tsv'

    # A regex for finding initials in names, like "Rob, Bob G."
    initial_rex = re.compile(r'(\w[.]) ?(\w)')

    # Parse authors spreadsheet
    # discard header lines (column headers, etc)
    for i in range(opt.discard):
        line = f.readline()
        debug('Discarding:', line)

    authors = []
    acks = []
    if opt.persack:
        pers_acks = []
    lastnames = []
    for line in f.readlines():
        words = line.replace('\n','').replace('  ', ' ').split('\t')

        lastname  = words[opt.lastname_index ]
        firstname = words[opt.firstname_index]
        orcid     = words[opt.orcid_index]
        affils    = words[opt.affil_index]
        ack       = words[opt.ack_index]

        if opt.persack:
            pers_ack  = words[opt.persack_index]

        # Split affiliations by semicolons OR commas
        # (because people can't follow instructions...)
        affils = [a.strip() for a in affils.split(';')]
        aa = []
        for a in affils:
            aa.extend([a.strip() for a in a.split(',')])
        affils = aa
        # drop any empty strings
        affils = [a for a in affils if len(a)]

        lastname  = lastname.strip()
        firstname = firstname.strip()
        name = firstname + ' ' + lastname
        # The author list is sorted by lastname
        lastnames.append(lastname)

        # Search for and stick "~" characters in initials, to produce
        # better Latex spacing.
        while True:
            m = initial_rex.search(name)
            if not m:
                break
            #debug('Match:', name, '->', m)
            #debug(m[0], '/', m[1], '/', m[2])
            name = name[:m.start()] + m[1]+'~'+m[2] + name[m.end():]
        # Hi Moritz :)
        name = name.replace('ü', '\\"{u}')

        acks.append(ack)
        if opt.persack:
            pers_acks.append(pers_ack)
        authors.append((name, orcid, affils))

    # Parse affiliation acronym expansion spreadsheet
    f = f2
    for i in range(opt.discard_affil):
        line = f.readline()
        debug('Discarding:', line)
    affilmap = {}
    for line in f.readlines():
        words = line.replace('\n','').replace('  ', ' ').split('\t')
        full,acro = words
        affilmap[acro] = full

    debug('Last names:', lastnames)

    # Sort by last name
    num_ordered = opt.num_ordered
    I = np.argsort(lastnames[num_ordered:])
    I = np.concatenate((np.arange(num_ordered), I+num_ordered))
    debug("Unsorted authors:", lastnames, "len:", len(lastnames))
    authors = [authors[i] for i in I]
    debug('Sorted authors:', authors,"len:", len(authors))

    # ApJ format
    if True:
        for auth,orcid,affil in authors:
            orctxt = ''
            if len(orcid):
                orctxt = '[%s]' % orcid
            print('\\author%s{%s}' % (orctxt, auth))
            for aff in affil:
                print('  \\affiliation{%s}' % affilmap.get(aff, aff))

    # Nature format
    if False:
        txt = []
        uaffils = []
        txt.append('\\author{')
        for iauth,(auth,orcid,affil) in enumerate(authors):
            sups = []
            for aff in affil:
                if aff in uaffils:
                    i = uaffils.index(aff)
                else:
                    i = len(uaffils)
                    uaffils.append(aff)
                sups.append(i+1)
            sep = ',' if iauth < len(authors)-1 else ''

            affiltxt = ''
            if len(sups):
                affiltxt = '$^{%s}$' % (','.join(['%i'%i for i in sups]))
            txt.append('%s%s%s \\allowbreak' % (auth, affiltxt, sep))

        txt.append('}')
        txt.append('\\newcommand{\\affils}{')
        txt.append('\\begin{affiliations}')
        for aff in uaffils:
            #txt.append('\\item{%s}' % aff)
            debug('Looking up', aff)
            txt.append('\\item{%s}' % affilmap.get(aff, aff))
        txt.append('\\end{affiliations}')
        txt.append('}')
        print('\n'.join(txt))

    acks = [acks[i] for i in I]
    if opt.persack:
        pers_acks = [pers_acks[i] for i in I]
    print('% Unique acks:')
    print(r'\newcommand{\allacks}{')
    for ack in acks:
        #debug('% ', ack)
        if len(ack):
            print(ack.replace('&', r'\&'))
            print('%')
    if opt.persack:
        for pers_ack in pers_acks:
            if len(pers_ack):
                print(pers_ack.replace('&', r'\&'))
                print('%')
    print(r'}')

if __name__ == '__main__':
    main()
