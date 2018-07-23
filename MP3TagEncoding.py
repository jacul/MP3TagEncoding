#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import codecs
import datetime

from mutagen.easyid3 import EasyID3 as ID3

encodings = ['gb2312', 'utf-8']

def analyse_files(scan_files):
    """
    Analyse the mp3 files provided in path.
    scan_files can be a folder. This will generate a config file for all mp3 files within this folder recursively.
    scan_files can be the path of one single mp3 file. Then the config file will contain only this file.
    When scan_files is empty, scan current folder recursively.
    """
    if len(scan_files) == 0:
            scan_files.append('.')

    json_file = []

    while (len(scan_files) > 0):
        file = scan_files.pop(0)
        if os.path.isfile(file):
            result = read_tags(file)
            if result is not None:
                print json.dumps(result, indent = 4).decode('unicode-escape').encode('utf-8')
                json_file.append(result)
        else:
            for (dirpath, dirnames, filenames) in os.walk(file):
                scan_files[0:0] = [os.path.join(dirpath, f) for f in filenames if f.lower().endswith('.mp3')]
                scan_files[0:0] = [os.path.join(dirpath, d) for d in dirnames]
                break

    filename = 'id3conf-' + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.json'
    with codecs.open(filename, 'w') as output:
        str_ = json.dumps(json_file, indent = 4).decode('unicode-escape').encode('utf-8')
        output.write(str_)
    
    
def read_tags(file):
    """
    Read all the tags in one mp3 file and return in a JSON object
    file: a MP3 file
    """
    id3 = ID3(file)
    tags = {}
    for key in id3.keys():
        tag_value = id3[key]
        tag_value_array = []
        for value in tag_value:
            encoded_value = []
            try:
                encoded = value.encode('ascii')
                encoded_value.extend(all_possible_decode(encoded))
            except Exception as e:
                encoded = value.encode('raw_unicode_escape')
                encoded_value.extend(all_possible_decode(encoded))
                
                encoded = value.encode('utf-8')
                encoded_value.extend(all_possible_decode(encoded))    
                    
            preferred = preferred_value(encoded_value)

#            print 'preferred', preferred, type(preferred), [preferred]
#            print 'all', encoded_value
            if preferred != encoded_value[-1]:
#                print 'preferred', preferred, type(preferred), [preferred]
#                print 'last', encoded_value[-1], type(encoded_value[-1]), [encoded_value[-1]]
                tag_value_dict = {'value' : encoded_value,
                                  'preferred' : preferred}
                tag_value_array.append(tag_value_dict)
        if tag_value_array:
            tags[key] = tag_value_array
    if tags:
        dict = {'path' : file}
        dict['tags'] = tags
        return dict
    else:
        return None

def all_possible_decode(tag):
    values = []
    for encoding in encodings:
        try:
            values.append(tag.decode(encoding).encode('utf-8'))
        except Exception as e:
            pass
    return values

def preferred_value(all_possible_values):
    """ Returns the most suitable value for all values decoded by provided encodings"""
    """ Now returns the shortest value """
    sorted_values = sorted(all_possible_values, key=len)
    return (sorted_values or [None])[0]
    
def update_using_config(config):
    """
    Update mp3 files in config file with provided strings
    config: a JSON file
    """
    try:
        json_data = json.load(open(config, 'r'))
    except Exception as e:
        print "Error opening file: " + e
        raise

    for mp3_json in json_data:
        file = mp3_json['path']
        tags = mp3_json['tags']
        update_mp3_with_tags(file, tags)
    
def update_mp3_with_tags(file, tags):
    """
    Update a mp3 file's ID3 with provided tags
    file: Path to a mp3 file
    tags: Provided tags
    """
    try:
        id3 = ID3(file)
        print "updating file", file.rsplit('/', 1)[-1]
        for key in tags.iterkeys():
            values = tags[key]
            new_tag_value = [single_tag_dict['preferred'] for single_tag_dict in values]
            print "    updating key", key, 'from', id3[key], 'to', new_tag_value
            id3[key] = new_tag_value
            
        id3.save()
            
    except Exception as e:
        print 'Error', e
        pass        

def main():
    try:
        scan_files = []
        config_file = ''
        found_config = False
        
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                option = arg[1].lower()
                if option == 'c':
                    found_config = True
            else:
                if found_config:
                    config_file = arg
                    found_config = False
                else :
                    scan_files.append(arg)
        
        # If a config file is provided, update mp3 files accordingly
        if len(config_file) != 0:
            update_using_config(config_file)
            print "Job done"
            sys.exit(0)
        
        # If no directory is specified, use current folder
        analyse_files(scan_files)
        
    except KeyboardInterrupt:
        print "Aborting process"
        pass
    except Exception:
        exit(0)

if __name__ == "__main__":
    main()