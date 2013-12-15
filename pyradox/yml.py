import os
import yaml
import pyradox.config
import pyradox.primitive

cache = {}

def getLocalization(key, sources = ['text'], game = pyradox.config.defaultGame):
    if isinstance(sources, str):
        sources = [sources]
    for source in sources:
        if source not in cache:
            languageKey = 'l_%s' % pyradox.config.language
            filename = os.path.join(pyradox.config.basedirs[game], 'localisation', '%s_%s.yml' % (source, languageKey))

            # if not os.path.exists(filename): continue
            
            f = open(filename, encoding='utf-8-sig')
            data = yaml.load(f, Loader=yaml.BaseLoader)
            f.close()
            cache[source] = data[languageKey]

        if key in cache[source]:
            return pyradox.primitive.makeString(cache[source][key])
        elif key.upper() in cache[source]:
            return pyradox.primitive.makeString(cache[source][key.upper()])
    
    return None

def getLocalizationDesc(key, sources = ['text']):
    return getLocalization('%s_desc' % key, sources)
    
def mergeLocalizations(localization, defaultSource, basedirs = [pyradox.config.defaultBasedir], sources = ['text'], omitUnmodified = True):
    # merges localization and basedirs * sources where localization and basedirs are in descending order of priority
    # as are sources, with localization and basedirs having higher priority

    # localization is of the form localization['key'] = 'value'
    # defaultSource is where any keys in localization will be placed if they are not found in any of the sources
    # basedirs is a list of base directories (the eu4.exe directory for base game, or mod directories)
    # sources is a list of strings excluding '_l_english.txt' defining which files will be searched
    # you may want to include defaultSource as the first element of sources
    
    # returns dict of form result['sourcename']['key'] = 'value'
    # unmodified sources may be omitted

    # initialize result with source dicts
    
    result = {}
    result[defaultSource] = {}
    for source in sources:
        result[source] = {}

    # read existing data
    for basedir in reversed(basedirs):
        for source in sources:
            filename = os.path.join(basedir, 'localisation', '%s_l_english.yml' % (source, ))

            # skip non-existent
            if not os.path.exists(filename): continue

            f = open(filename, encoding='utf-8-sig')
            data = yaml.load(f, Loader=yaml.BaseLoader)
            f.close()

            if data is None or 'l_english' not in data:
                print("No strings in localization file %s." % filename) 
                continue

            result[source].update(data['l_english'])

    # update with new data
    modifiedSources = set()
    modifiedSources.add(defaultSource)
    
    for key, value in localization.items():
        for source in reversed(sources):
            if key in result[source]:
                result[source][key] = value
                modifiedSources.add(source)
                break
        else:
            # fallback to default
            result[defaultSource][key] = value

    if not omitUnmodified: return result

    finalResult = {}
    for source in modifiedSources:
        finalResult[source] = result[source]

    return finalResult

def writeLocalizations(localizations, basedir):
    # writes localizations to basedir
    # localizations is of the form localizations['sourcename']['key'] = 'value'

    localizationPath = os.path.join(basedir, 'localisation')
    os.makedirs(localizationPath, exist_ok=True)

    for source, data in localizations.items():
        data = { 'l_english' : data }

        filename = os.path.join(basedir, 'localisation', '%s_l_english.yml' % source)
        
        f = open(filename, 'w', encoding='utf-8-sig')
        yaml.dump(data, f, default_style='"', default_flow_style=False)
        f.close()
