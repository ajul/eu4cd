import os
import yaml

import pyradox.txt

def writeMod(filepath, tag, countryBasename, countryData, ideas, events, localization):
    basedir, basename = os.path.split(filepath)
    root, ext = os.path.splitext(basename)
    
    # create mod file if not already existing
    if not os.path.exists(filepath):
        f = open(filepath, 'w')
        contents = 'name="%s"\n' % root
        contents += 'path="mod/%s"\n' % root
        contents += 'tags={}\n'
        f.write(contents)
        f.close()

    # write ideas
    if ideas is not None:
        overwriteFile(os.path.join(basedir, root, 'common', 'ideas', '00_00_%s_%s_ideas.txt' % (root, tag)), str(ideas))

    # write events
    if events is not None:
        overwriteFile(os.path.join(basedir, root, 'events', '%s_%s_events.txt' % (root, tag)), str(events))

    # write countries
    if countryData is not None:
        overwriteFile(os.path.join(basedir, root, 'history', 'countries', countryBasename), str(countryData))

    # write localization
    if localization is not None:
        localizationPath = os.path.join(basedir, root, 'localisation')
        os.makedirs(localizationPath, exist_ok=True)

        localization = { 'l_english' : localization }

        f = open(os.path.join(localizationPath, '%s_%s_l_english.yml' % (root, tag)), 'w', encoding='utf-8-sig')
        yaml.dump(localization, f, default_flow_style=False, default_style='"')
        f.close()

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
