import os
import yaml

import pyradox.txt

def writeMod(filepath, ideas=None, events=None, countries=None, localization=None):
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
        ideasPath = os.path.join(basedir, root, 'common', 'ideas', '00_country_ideas_eu4cd_%s.txt' % root)
        updateFile(ideasPath, ideas)

    # write events
    if events is not None:
        eventPath = os.path.join(basedir, root, 'events', 'eu4cd_%s_events.txt' % root)
        updateFile(eventPath, events)

    # write countries
    if countries is not None:
        countriesDir = os.path.join(basedir, root, 'history', 'countries')
        os.makedirs(countriesDir, exist_ok=True)
        for countryBasename, data in countries.items():
            f = open(os.path.join(countriesDir, countryBasename), 'w')
            f.write(str(data))
            f.close()

    # write localization
    if localization is not None:
        localizationPath = os.path.join(basedir, root, 'localisation')
        os.makedirs(localizationPath, exist_ok=True)

        localization = { 'l_english' : localization }

        # TODO: update existing
        f = open(os.path.join(localizationPath, 'eu4cd_%s_l_english.yml' % root), 'w')
        yaml.dump(localization, f, default_flow_style=False)
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
