###
### universities.py
###

import random

### This file provides data and functions about universities that is useful for multiple analyses.

skipaffiliations = ['Computer Science', 
                    'Electrical and Computer Engineering',
                    'Computer Engineering'
                   ]

canonicalize = { 
    'University of North Carolina at Chapel Hill': 'University of North Carolina',
    'UNC': 'University of North Carolina',
    'Massachusetts Institute of Technology': 'MIT',
    'University of Illinois': 'University of Illinois Urbana-Champaign',
    'University of Illinois at Urbana-Champaign': 'University of Illinois Urbana-Champaign',
    'UIUC': 'University of Illinois Urbana-Champaign',
    'MIT-IBM Watson AI Lab': 'MIT',
    'Google Brain': 'Google',
    'The Ohio State University': 'Ohio State University',
    'The University of Alabama at Birmingham': 'University of Alabama at Birmingham',
    'Penn State': 'Pennsylvania State University',
    'Penn State University': 'Pennsylvania State University',
    'CSAIL': 'MIT',
    'University of Wisconsin-Madison': 'University of Wisconsin',
    'Google Research': 'Google',
    'Intel Research': 'Intel',
    'Duke': 'Duke University',
    'Princeton': 'Princeton University',
    'Duke Univeristy': 'Duke University',
    'The University of Texas': 'University of Texas',
    'UT Austin': 'University of Texas',
    'UC Los Angeles': 'UCLA',   
    'Virginia Tech University': 'Virginia Tech',
    'University of Pittsburg': 'University of Pittsburgh',
    'Vanderbilt': 'Vanderbilt University',
}

# SRI List of UVA "peers and aspiring peers"
uvapeers = [
    'University of Virginia',
    'Duke University',
    'Emory University',
    'Northwestern University',
    'Ohio State University',
    'Rutgers University',
    'University of Alabama at Birmingham',
    'University of Michigan',
    'University of North Carolina',
    'University of Pittsburgh',
    'University of Washington',
    'Vanderbilt University',
    'Virginia Tech',
    ]

universities = uvapeers
# [
#     'University of Virginia',
#     'Duke University',
#     'Emory University',
#     'George Mason University',
#     'Northwestern University',
#     'Ohio State University',
#     'Rutgers University',
#     'University of Alabama at Birmingham',
#     'University of Michigan',
#     'University of North Carolina',
#     'University of Pittsburgh',
#     'University of Washington',
#     'Vanderbilt University',
#     'Virginia Tech',
# ]

selected = [
    'University of Virginia',
    'Duke University',
    'Ohio State University',
    'University of Michigan',
    'University of North Carolina',
    'University of Pittsburgh',
    'University of Washington',
    'Virginia Tech',
]

uname = {
    'University of Virginia': 'UVA',
    'Emory University': 'Emory',
    'Duke University': 'Duke',
    'Northwestern University': 'NWU', # orthwestern',
    'George Mason University': 'GMU',
    'Ohio State University': 'OSU',
    'Rutgers University': 'Rutgers',
    'University of Alabama at Birmingham': 'UAB',
    'University of Michigan': 'UMich',
    'University of North Carolina': 'UNC',
    'University of Pittsburgh': 'Pitt',
    'University of Washington': 'UWash',
    'Vanderbilt University': 'Vanderbilt',
    'Virginia Tech University': 'VT',
    'Virginia Tech': 'VT',

    'University of Pennsylvania': 'UPenn',
    'University of Wisconsin': 'UWisc',
    'University of Maryland': 'UMd',
    'University of Texas': 'UTAustin',
    'Northeastern University': 'NEU',
    'Brown University': 'Brown', 
    'Johns Hopkins University': 'JHU',
    'Michigan State University': 'MSU',
    'Princeton University': 'Princeton',

    'peers': 'Peers',
    'instate': 'In-State',
    'outofstate': 'Out-of-State',
    'all': 'Total'
}

# instate = ['George Mason University', 'Virginia Tech']
# instate = ['Virginia Tech']

peers = []
for u in uvapeers:
    if not u == 'University of Virginia':
        peers.append(u)

ucolor = {
    'University of Virginia': '#E57200', #'#232D4B', # UVA Blue (#E57200, # UVA Orange) from https://brand.virginia.edu/design-assets/colors
    'Emory University': '#007dba', # light blue
    'Duke University': '#00539B', 
    'Northwestern University': '#4E2A84',
    'George Mason University': '#006633',
    'Ohio State University': '#ba0c2f',
    'Rutgers University': 'red',
    'University of Alabama at Birmingham': '#1E6B52',
    'University of Michigan': '#FFCB05',
    'University of North Carolina': '#007FAE',
    'University of Pittsburgh': '#FFB81C',
    'University of Washington': '#32006e',
    'Vanderbilt University': '#CFAE70',
    'Virginia Tech University': '#861F41',
    'Virginia Tech': '#861F41',

    'University of Pennsylvania': '#990000',
    'University of Wisconsin': '#C5050C',
    'University of Maryland': '#E21833',
    'University of Texas': '#bf5700',
    'Michigan State University': '#18453B',
    'Northeastern University': '#000000',
    'Brown University': '#4E3629', 
    'Johns Hopkins University': '#002D72',
    'Princeton University': '#E77500',

    'peers': 'grey',
    'outofstate': 'grey',
    'instate': 'darkblue',
    'all': 'black'
}

def cleanAffiliation(affiliation):
    """
    Attempt to extract the most useful institution name from the kludgey affiliation.
    """

    # select just the clause that contains "Univ"
    univaffil = None
    firstname = None

    for affname in affiliation.split(','):
        affname = affname.strip()

        affname.replace("Univeristy", "University")
        affname.replace("University of California", "UC")
        
        if affname in canonicalize:
            affname = canonicalize[affname]
            
        if affname in skipaffiliations:
            continue

        if affname.startswith("Department") or affname.startswith("Dept"):
            continue
            
        if not firstname:
            firstname = affname

        if "Univ" in affname or "UC" in affname:
            if univaffil:
                pass
                # print("Multiple univ in affiliation: " + affiliation + " for paper: " + paper["Title"])
            else:
                univaffil = affname
    
        if "Tech" in affname or "Institute" in affname:
            firstname = affname
            
    if not univaffil:
        univaffil = firstname
        # print("No univ for affiliation: " + affiliation)

    return univaffil

def university_name(univ):
    if univ in uname:
        return uname[univ]
    else:
        return univ
    
def university_color(univ):
    if univ in ucolor:
        return ucolor[univ]
    else: 
        # Give univ a random color
        print("Selecting random color for: " + univ)
        ucolor[univ] = "#{0:02x}{1:02x}{2:02x}".format(random.choice(range(256)),
                                                       random.choice(range(256)),
                                                       random.choice(range(256)))
        return ucolor[univ]