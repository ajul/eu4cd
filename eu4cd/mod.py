import os
import yaml

import eu4cd.gamedata
import pyradox.txt

def writeMod(filepath, gamepath, tag, countryBasename, countryData, ideas, events, localization):
    basedir, basename = os.path.split(filepath)
    root, ext = os.path.splitext(basename)
    moddir = os.path.join(basedir, root)
    
    # create mod file if not already existing
    if not os.path.exists(filepath):
        f = open(filepath, 'w')
        contents = 'name="%s"\n' % root
        contents += 'path="mod/%s"\n' % root
        contents += 'tags={}\n'
        f.write(contents)
        f.close()

    # write ideas
    overwriteFile(os.path.join(moddir, 'common', 'ideas', '00_00_%s_%s_ideas.txt' % (root, tag)), str(ideas))

    # write events
    overwriteFile(os.path.join(moddir, 'events', '%s_%s_events.txt' % (root, tag)), str(events))

    # write countries
    overwriteFile(os.path.join(moddir, 'history', 'countries', countryBasename), str(countryData))

    # write localization
    localizationPath = os.path.join(moddir, 'localisation')
    os.makedirs(localizationPath, exist_ok=True)

    defaultSource = '%s_%s' % (root, tag)

    if tag in localization:
        basedirs = [moddir, gamepath]
        sources = [defaultSource, 'countries', 'text']
    else:
        basedirs = [moddir]
        sources = [defaultSource]
        
    mergedLocalizations = pyradox.yml.mergeLocalizations(localization, defaultSource, basedirs = basedirs, sources = sources)
    pyradox.yml.writeLocalizations(mergedLocalizations, os.path.join(basedir, root))

def overwriteFile(filepath, data):
    basedir, basename = os.path.split(filepath)
    os.makedirs(basedir, exist_ok=True)
    f = open(filepath, "w")
    f.write(data)
    f.close()
    
def updateFile(filepath, data):
    basedir, basename = os.path.split(filepath)
    os.makedirs(basedir, exist_ok=True)
    if os.path.exists(filepath):
        existing = pyradox.txt.parseFile(filepath)
        existing.update(data)
        f = open(filepath, "w")
        f.write(str(existing))
        f.close()
    else:
        f = open(filepath, "w")
        f.write(str(data))
        f.close()
