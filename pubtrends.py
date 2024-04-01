###
### pubtrends.py
###
### Code for analyzing publication trends from the OpenAlex data, with topic
### scores assigned by model.
###
### Written for UVA AI Research Task Force report.
###

import csv
import matplotlib.pyplot as plt
from datetime import datetime

from universities import *

datafile = 'data/publications.scores.mult.viz.csv'

areas = [
        'neural networks',	
        'artificial intelligence',
        'quantitative methods',
        'applied work',	
        'machine learning',
        'natural language processing',
        'data analysis',
        'data mining',
        'bioinformatics',
        'statistics'
    ]

areaname = { 
        'neural networks': "Neural Networks",	
        'artificial intelligence': "Artificial Intelligence",
        'quantitative methods': "Quantitative Methods",
        'applied work': "Applied Work",	
        'machine learning': "Machine Learning",
        'natural language processing': "NLP",
        'data analysis': "Data Analysis",
        'data mining': "Data Mining",
        'bioinformatics': "Bioinformatics",
        'statistics': "Statistics"
}

startyear = 1980
endyear = 2023 # not enough data for 2024

with open(datafile, 'r') as file:
    csv_reader = csv.reader(file)

    header = next(csv_reader)
    header_dict = {col: index for index, col in enumerate(header)}
    
    date_col = header_dict['publication_date']
    univ_col = header_dict['University']
    cite_col = header_dict['cited_by_count']
    year_col = header_dict['Year']
    area_col = header_dict['Area']
    areacolumn = {}
    
    for area in areas:
        assert area in header_dict
        areacolumn[area] = header_dict[area]

    next(csv_reader) 

    years = range(startyear, (endyear + 1))
    t1 = 0.25
    t2 = 0.75

    data = {}

    fulluniversities = universities.copy()
    fulluniversities.append('peers') # all others

    for area in areas:
        data[area] = {}

        for univ in fulluniversities:
            data[area][univ] = {}

            for year in years:
                data[area][univ][year] = { 'count': 0, 'total_score': 0, 'num_above_t1': 0, 'num_above_t2': 0,
                                           'mean_score': 0}

    print("Reading CSV file...")
    countrows = 0
    for row in csv_reader:
        countrows += 1
        if countrows % 10000 == 0:
            print ("Reading rows %d..." % (countrows))

        year = row[year_col].strip()
        univ = cleanAffiliation(row[univ_col].strip())

        if univ not in universities:
            if univ == 'George Mason University':
                # GMU is included in the pubtrends data, but is not in the list of peers
                continue
            else:
                print("Unknown univ: " + univ)
                assert False

        yr = int(year)
        if yr < startyear or yr > endyear:
            continue # just skip papers outside years

        for area in areas:
            areacol = areacolumn[area]
            data[area][univ][yr]['count'] += 1
            score = float(row[areacol])
            assert score >= 0.0 and score <= 1.0
            data[area][univ][yr]['total_score'] += score
            data[area][univ][yr]['num_above_t1'] += 1 if score >= t1 else 0
            data[area][univ][yr]['num_above_t2'] += 1 if score >= t2 else 0

            if univ in peers:
                pu = 'peers'
            else:
                assert univ == 'University of Virginia'
                pu = None
            if pu:
                data[area][pu][yr]['count'] += 1
                data[area][pu][yr]['total_score'] += score
                data[area][pu][yr]['num_above_t1'] += 1 if score >= t1 else 0
                data[area][pu][yr]['num_above_t2'] += 1 if score >= t2 else 0            

print("Finished reading CSV file")
totalpapers = 0
totalbyarea = {}

universities = uvapeers # + ['George Mason University']

for area in areas:
    totalbyarea[area] = 0
    for year in years:
        print ("%s %d:" % (area, year))
        for univ in universities:
            dobj = data[area][univ][year]
            count = dobj['count']
            mean_score = dobj['total_score'] / count
            dobj['mean_score'] = mean_score
            if univ in peers:
                data[area]['peers'][year]['mean_score'] += mean_score

            print("%s: count = %d, mean score = %f, t1 count = %d, t2 count = %d" % (univ, count, mean_score, 
                                                                                        dobj['num_above_t1'],
                                                                                        dobj['num_above_t2']))

propname = {
    'mean_score': 'Mean Topic Score',
    'num_above_t1': 'Number of Papers',
    'num_above_t2': 'Number of Papers'
}

for area in areas:
    if area in ['applied work', 'quantitative methods', 'data analysis']:
        continue

    for property in ['mean_score', 'num_above_t1', 'num_above_t2']:
        graphname = areaname[area] # + " - " + propname[property]
        for graphtype in ['group', 'selected', 'all']:
            plt.figure(figsize=(10, 6))    
            plt.rcParams['font.family'] = 'Times New Roman' # Helvetica'        
            if graphtype == 'group':
                for univ in ['University of Virginia', 'peers']:
                    divisor = 1
                    if univ == 'peers':
                        divisor = len(peers)

                    plt.plot(years, 
                             [(data[area][univ][year][property] / divisor) for year in years],
                             label=uname[univ],
                             marker='o',
                             linewidth = 4 if univ=='University of Virginia' else 4, 
                             alpha = 1.0 if univ=='University of Virginia' else 0.8,
                             color = ucolor[univ])
            else:
                for univ in (selected if graphtype == 'selected' else universities):
                    plt.plot(years, 
                            [data[area][univ][year][property] for year in years],
                            label=uname[univ],
                            marker = ('o' if univ == 'University of Virginia' else '.'),
                            linewidth = 4 if univ == 'University of Virginia' else 2, 
                            alpha = 1.0 if univ == 'University of Virginia' else 0.5,
                            color =  ucolor[univ])
                    
            plt.xlabel('Year', fontsize=32)
            plt.ylabel(propname[property], fontsize=32)
            # plt.title(graphname, fontsize=32)
            if graphname == "Neural Networks" or graphname == "Statistics": # title on bottom            
                vtitle = 0.1
            else:
                vtitle = 0.9

            plt.text(0.5, vtitle, graphname, 
                     fontsize = 32 if property=='num_above_t2' else 40, # fontfamily='Times New Roman',
                    ha='center', va='center', 
                    fontweight='bold',
                    transform=plt.gca().transAxes)

            if property == 'num_above_t2':
                if graphtype == 'selected':
                    plt.legend(fontsize=28, loc='center left', 
                               frameon = False, fancybox = False,
                               framealpha = 1.0, labelspacing = 0.3,
                               columnspacing = 1.0, ncol=2)
                else:
                    if areaname[area] == 'Artificial Intelligence':
                        plt.text(0.94, 0.25, "UVA", 
                         color = ucolor["University of Virginia"],
                         fontsize=32, # fontfamily='Times New Roman',
                         fontweight='bold',
                         ha='center', va='center', transform=plt.gca().transAxes)
                        plt.text(0.85, 0.76, "Peers", 
                         color = ucolor["peers"],
                         fontsize=32, # fontfamily='Times New Roman',
                         ha='center', va='center', transform=plt.gca().transAxes)
                        
            if property == 'mean_score' and areaname[area] == 'Artificial Intelligence': 
                plt.text(0.22, 0.07, "UVA", 
                         color = ucolor["University of Virginia"],
                         fontsize=36, # fontfamily='Times New Roman',
                         fontweight='bold',
                         ha='center', va='center', transform=plt.gca().transAxes)
                plt.text(0.80, 0.65, "Peers", 
                         color = ucolor["peers"],
                         fontsize=36, # fontfamily='Times New Roman',
                         ha='center', va='center', transform=plt.gca().transAxes)

            plt.xticks(fontsize=32)
            plt.yticks(fontsize=32)
            plt.tight_layout()
            print("Writing plot: " + graphname)
            graphfile = area + '-' + graphtype + '-' + property

            # for easier uploading to overleaf (which doesn't allow > 40 files in one upload!)
            # this is the list of graphs actually used in the report...
            if graphfile in ['artificial intelligence-group-num_above_t2', 
                             'artificial intelligence-selected-num_above_t2',
                             'machine learning-group-num_above_t2', 
                             'machine learning-selected-num_above_t2',
                             'artificial intelligence-group-mean_score',
                             'bioinformatics-group-mean_score', 
                             'machine learning-group-mean_score',
                             'natural language processing-group-mean_score',
                             'neural networks-group-mean_score',
                             'statistics-group-mean_score']:
                plt.savefig('pubsoutput/' + graphfile + '.pdf')
            else:
                plt.savefig('output/' + graphfile + '.pdf')
            plt.close()
