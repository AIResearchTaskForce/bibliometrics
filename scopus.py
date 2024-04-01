### 
### scopus.py
###
### Code for analyzing publications in scopus datasets.
###
### Written for UVA AI Research Task Force report.
###

from collections import namedtuple
import time
import re
import csv

import matplotlib.pyplot as plt
from universities import *

# Scopus queries to get the data:
#
# - CONFNAME ( "ICML" ) AND PUBYEAR > 2020 AND ( LIMIT-TO ( DOCTYPE , "cp" ) ) AND ( LIMIT-TO ( EXACTSRCTITLE , "Proceedings Of Machine Learning Research" ) )
# - SRCTITLE ( "Advances in Neural Information Processing Systems" ) AND ( LIMIT-TO ( DOCTYPE , "cp" ) )
# - SRCTITLE ( "International Conference on Learning Representations" ) AND ( LIMIT-TO ( EXACTSRCTITLE , "Iclr 2022 10th International Conference On Learning Representations" ) OR LIMIT-TO ( EXACTSRCTITLE , "Iclr 2021 9th International Conference On Learning Representations" ) OR LIMIT-TO ( EXACTSRCTITLE , "8th International Conference On Learning Representations Iclr 2020" ) OR LIMIT-TO ( EXACTSRCTITLE , "7th International Conference On Learning Representations Iclr 2019" ) OR LIMIT-TO ( EXACTSRCTITLE , "6th International Conference On Learning Representations Iclr 2018 Conference Track Proceedings" ) OR LIMIT-TO ( EXACTSRCTITLE , "5th International Conference On Learning Representations Iclr 2017 Conference Track Proceedings" ) OR LIMIT-TO ( EXACTSRCTITLE , "4th International Conference On Learning Representations Iclr 2016 Conference Track Proceedings" ) OR LIMIT-TO ( EXACTSRCTITLE , "2nd International Conference On Learning Representations Iclr 2014 Conference Track Proceedings" ) OR LIMIT-TO ( EXACTSRCTITLE , "3rd International Conference On Learning Representations Iclr 2015 Conference Track Proceedings" ) OR LIMIT-TO ( EXACTSRCTITLE , "1st International Conference On Learning Representations Iclr 2013 Conference Track Proceedings" ) )
#      (Note: selected to avoid including workshops)

datafiles = [
    ("data/neurips-all-scopus.csv", "NeurIPS"),
    ("data/AAAI-2007-2023-scopus.csv", "AAAI"),
    ("data/ICML-1988-2020-scopus.csv", "ICML"),
    ("data/ICML-2021-2023-scopus.csv", "ICML"),
    ("data/iclr-all-scopus.csv", "ICLR"),
]

affiliations = {}
papersbyplace = {}
papersbyplace['all'] = {}

conferences = {}

# For the main graphs, used 2012-2022; for some of the conference graphs used 2000-2023.

minyear = 2012
maxyear = 2022

# minyear = 2000
# maxyear = 2023

allyears = range(minyear, maxyear + 1)

def read_papers(fname, conf):
    papers = []
    
    if conf not in conferences:
        conferences[conf] = {}
        papersbyplace['all'][conf] = {}

        for nyear in allyears:
            conferences[conf][nyear] = set()
            papersbyplace['all'][conf][nyear] = []

    with open(fname, encoding='ISO-8859-1') as csvfile:
        sreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        headers = next(sreader)
        for row in sreader:
           papers.append({key: value for key, value in zip(headers, row)})

    print ("Read papers: " + str(len(papers)))
    
    for paper in papers:
        if len(paper["Title"].strip()) < 2:
            pass
        if not paper["Affiliations"]:
            pass # print("No Affiliations for paper: " + paper["Title"])

        conference = paper["Conference name"]
        year = int(paper["Year"]) # Conference date"][-4:])

        if year < minyear or year > maxyear:
            continue # skip papers out of year range

        conferences[conf][year].add(conference)
        paper['papersbyplace'] = set()
        
        papersbyplace['all'][conf][year].append(paper)

        for affiliation in paper["Affiliations"].split(';'):
            if affiliation in affiliations:
                affiliations[affiliation].append(paper)
            else:
                affiliations[affiliation] = [paper]

            affil = cleanAffiliation(affiliation)

            if affil not in papersbyplace:
                papersbyplace[affil] = {}

            # there's gotta be a better way to do this...
            if conf not in papersbyplace[affil]:
                papersbyplace[affil][conf] = {}
                for nyear in allyears:
                    papersbyplace[affil][conf][nyear] = []

            # without this, counts number of paper-affiliations
            if paper not in papersbyplace[affil][conf][year]: 
                papersbyplace[affil][conf][year].append(paper)

            paper['papersbyplace'].add(affil)
        
    return papers

papers = []
confs = set()

for (file, conf) in datafiles:
    confs.add(conf)
    papers += read_papers(file, conf)

print("Papers: %d, Affiliations: %d, Cleaned: %d" % (len(papers), len(affiliations), len(papersbyplace)))

confcolor = {
    'NeurIPS': '#118ab2',
    'AAAI': '#06d6a0',
    'ICML': '#ef476f',
    'ICLR': '#ffd166'
}

if True: # generate Total Citings
    years = allyears # [conferences[conference]['year'] for conference in conferences if conferences[conference]['name'] == cname]

    for mean in [True, False]:
        graphname = 'Average Citations per Paper' if mean else 'Total Citations'
        plt.figure(figsize=(10, 6))    
        plt.rcParams['font.family'] = 'Times New Roman' # Helvetica'        

        basesize = 28

        clist = list(confs)
        clist.sort(key=lambda conf: sum([int(paper['Cited by']) 
                                        for paper in papersbyplace['all'][conf][maxyear]]), 
                    reverse=True)

        for conf in clist:
            cyears = []
            for year in years:
                if mean and conf == 'ICLR' and year < 2016:
                    print("Skipping ICLR " + str(year))
                    # don't include early years of ICLR, too many citings with too few paper!
                    # ICLR 2015 includes
                    # Adam: A method for stochastic optimization (44142 citings)
                    # Very deep convolutional networks for large-scale image recognition (23858)
                    # so ends up averaging over 2500 citings per paper, which really messes up the graphs... 
                elif len(papersbyplace['all'][conf][year]) > 0:
                    cyears.append(year)

            print("conf: " + conf + " cyears: " + str(cyears))
            plt.plot(cyears, 
                    [sum([int(paper['Cited by']) 
                        for paper in papersbyplace['all'][conf][year]]) 
                        / (len(papersbyplace['all'][conf][year]) if mean else 1) 
                    for year in cyears],
                    label = conf,
                    linewidth = 2,
                    marker = 'o',
                    color = confcolor[conf])
            
        # plt.xlabel('Year', fontsize=36)
        plt.ylabel('Mean Citings per Paper' if mean else 'Total Citings', fontsize=basesize)
        plt.xticks(fontsize=basesize)
        plt.yticks(fontsize=basesize)
        plt.grid(False)    
        plt.tight_layout()
        print("Writing plot: " + graphname)
        plt.savefig('scopusoutput/confcitings' + ('-mean' if mean else '-total') + '.pdf')
        plt.close()

if True: # generate Total Papers
    # Totals for conferences
    graphname = 'Total Papers'
    years = allyears # [conferences[conference]['year'] for conference in conferences if conferences[conference]['name'] == cname]

    plt.figure(figsize=(10, 6))    
    plt.rcParams['font.family'] = 'Times New Roman' # Helvetica'        
    basesize = 28

    clist = list(confs)
    clist.sort(key=lambda conf: len(papersbyplace['all'][conf][maxyear - 1]), reverse=True)

    for conf in clist:
        cyears = []
        for year in years:
            if len(papersbyplace['all'][conf][year]) > 0:
                cyears.append(year)

        plt.plot(cyears, 
                [len(papersbyplace['all'][conf][year]) for year in cyears],
                label = conf,
                linewidth = 2,
                marker = 'o',
                color = confcolor[conf])
        
    plt.ylabel('Number of Papers', fontsize=basesize)
    plt.legend(fontsize=basesize, loc='upper left', 
                frameon = False,
                fancybox = False,
                framealpha = 1.0,
                labelspacing = 0.3,
                columnspacing = 1.0,
                ncol=1)
    plt.xticks(fontsize=basesize)
    plt.yticks(fontsize=basesize)
    plt.grid(False)    
    plt.tight_layout()
    print("Writing plot: " + graphname)
    plt.savefig('scopusoutput/conftotals.pdf')
    plt.close()

plotunis = uvapeers

plotunis = [
    'University of Washington',
    'University of Michigan',
    'Ohio State University',
    'Duke University',
    'University of Virginia',
    'Rutgers University',
#    'Princeton University',
    'University of Pittsburgh',
    'Virginia Tech',
    'University of North Carolina',
    # 'Stanford University',
    # 'MIT',
    # 'Google',
    'University of Texas'
#    'Vanderbilt University',
]

if True: # Generate University paper graphs
    plotunis.sort(key=lambda uni: sum([len(papersbyplace[uni][conf][maxyear])
                                        for conf in conferences]), reverse=True)
    graphname = 'All Conferences'
    years = allyears 
    plt.figure(figsize=(15, 6))    

    for univ in plotunis:   
        plt.plot(allyears, 
                [sum([(len(papersbyplace[univ][conf][year]) / len(papersbyplace['all'][conf][year])) if len(papersbyplace['all'][conf][year]) > 0 else 0
                    for conf in conferences])
                for year in allyears],
                label = university_name(univ),
                marker = 'o',
                linewidth = 3 if univ=='University of Virginia' else 1.5, 
                alpha = 1.0 if univ=='University of Virginia' else 0.5,
                color = university_color(univ))
            
    basesize = 22

    plt.ylabel('Fraction of Papers', fontsize=basesize)
    plt.legend(fontsize=basesize, 
            loc=(1.02, 0.1), # -0.12),
                frameon = False,
                fancybox = False,
                framealpha = 1.0,
                labelspacing = 0.3,
                columnspacing = 1.0,
                ncol=1)
    plt.xticks(fontsize=basesize)
    plt.yticks(fontsize=basesize)
    plt.grid(False)
            
    plt.tight_layout()
    print("Writing plot: " + graphname)
    plt.savefig('scopusoutput/' + 'allconfs' + '.pdf')
    plt.close()

if True: # graph papers for each conference
    for conf in confs:
        graphname = conf + ' Total Papers by University'
        years = allyears # [conferences[conference]['year'] for conference in conferences if conferences[conference]['name'] == cname]
        cyears = []
        for year in years:
            if len(papersbyplace['all'][conf][year]) > 0:
                cyears.append(year)

        plt.figure(figsize=(10, 6))    

        for univ in plotunis:   
            plt.plot(cyears, 
                    [len(papersbyplace[univ][conf][year]) for year in cyears],
                    label = university_name(univ),
                    marker = 'o',
                    linewidth = 2 if univ=='University of Virginia' else 1, 
                    alpha = 1.0 if univ=='University of Virginia' else 0.5,
                    color = university_color(univ))
            
        plt.xlabel('Year', fontsize=16)
        plt.ylabel('Number of Papers', fontsize=16)
        plt.title(graphname, fontsize=20)

        plt.legend(fontsize=14, loc='center left', frameon = False, fancybox = False,
                    framealpha = 1.0, labelspacing = 0.3, columnspacing = 1.0, ncol=2)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.grid(False)
            
        plt.tight_layout()
        print("Writing plot: " + graphname)
        plt.savefig('scopusoutput/' + conf + '.pdf')
        plt.close()

if True: # Generate University citation graphs
    graphname = 'Citations Across All Conferences'
    years = allyears 
    plt.figure(figsize=(15, 6))    
    basesize = 22

    for univ in plotunis:   
        plt.plot(allyears, 
                 [sum([int(paper['Cited by']) 
                        for paper in papersbyplace[univ][conf][year]
                        for conf in conferences]) 
                    / max(1, sum([int(paper['Cited by']) 
                            for paper in papersbyplace['all'][conf][year]
                            for conf in conferences]))
                     for year in allyears],    
                label = university_name(univ),
                marker = 'o',
                linewidth = 3 if univ=='University of Virginia' else 1.5, 
                alpha = 1.0 if univ=='University of Virginia' else 0.5,
                color = university_color(univ))

    plt.ylabel('Fraction of Citings', fontsize=basesize)
    plt.legend(fontsize=basesize, loc=(1.02, 0.1), frameon = False, fancybox = False,
                framealpha = 1.0, labelspacing = 0.3, columnspacing = 1.0, ncol=1)
    plt.xticks(fontsize=basesize)
    plt.yticks(fontsize=basesize)
    plt.grid(False)            
    plt.tight_layout()
    print("Writing plot: " + graphname)
    plt.savefig('scopusoutput/' + 'fraccitings' + '.pdf')
    plt.close()

if True: # graph citings for each conference
    for conf in confs:
        graphname = conf + ' Citings by University'
        years = allyears # [conferences[conference]['year'] for conference in conferences if conferences[conference]['name'] == cname]
        cyears = []
        for year in years:
            if len(papersbyplace['all'][conf][year]) > 0:
                cyears.append(year)

        plt.figure(figsize=(10, 6))    

        for univ in plotunis:   
            plt.plot(cyears, 
                     [sum([int(paper['Cited by']) 
                           for paper in papersbyplace[univ][conf][year]]) 
                        / sum([int(paper['Cited by']) 
                            for paper in papersbyplace['all'][conf][year]])
                     for year in cyears],    
                    label = university_name(univ),
                    marker = 'o',
                    linewidth = 2 if univ=='University of Virginia' else 1, 
                    alpha = 1.0 if univ=='University of Virginia' else 0.5,
                    color = university_color(univ))
            
        plt.xlabel('Year', fontsize=16)
        plt.ylabel('Fraction of Citings', fontsize=16)
        plt.title(graphname, fontsize=20)

        plt.legend(fontsize=14, loc='center left', frameon = False, fancybox = False,
                   framealpha = 1.0, labelspacing = 0.3, columnspacing = 1.0, ncol=2)

        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.grid(False)
            
        plt.tight_layout()
        print("Writing plot: " + graphname)
        plt.savefig('scopusoutput/' + conf + '-citings.pdf')
        plt.close()
