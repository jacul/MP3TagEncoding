
# MP3TagEncoding

Change an mp3 file's ID3 encoding

## Introduction

Some of my mp3 files' ID3 tags are in encodings other than UTF-8. They don't play very well in iTunes. So I wrote this script to update them to correct encoding(UTF-8).

This script is tested under macOS High Sierra, with Python 2.7.

## Prerequisites

You will need [Mutagen](http://mutagen.readthedocs.io/en/latest/index.html) to run this script. Kudos to Mutagen's author, it's the best library I can find to udpate ID3.

## Installing

You don't need anything else to run this script. Simply download the `MP3TagEncoding.py` to any location, and give it proper permissions.

## Flow

This script provides two ways of updating mp3 files. One is to generate a config file, then update according to this config file. The other is to update mp3 files interactively. Right now the interactive mode only supports updating one entire file at a time and options are only yes and no.

### Update in config mode

#### Step 1

The script will take currect folder as default, and scan all mp3 files. If given a path,

```
./MP3TagEncoding.py ~/Music
```

The script will recursively scan all files in this folder, and generate a config file in JSON under current folder. You can inspect the JSON file and see if all those changes are matching.

One typical config:

```
{
    "path": "/Users/user/Music/sample.mp3", 
    "tags": {
        "artist": [
            {
                "value": [
                    "name in one random encoding",
                    "name in another encoding",
                    "...."
                ], 
                "preferred": "name in UTF-8"
            }
        ]
    }
}
```

You can change the `preferred` key's value if it's not the correct one. In most cases, this is done automatically.

#### Step 2

Feed the config file to the script, using -c

```
./MM3TagEncoding.py -c <path to generated config file>
```

The script will update the mp3 files in the config, and only udpate the specified tags, using `preferred` value. All unrelated tags won't be touched.

Done!

### Update in interactive mode

The script will ask you whether to update a file or not. Upon choosing yes, the mp3 file will be updated immediately.

For one file:

```
./MM3TagEncoding.py -i ~/Music/sample.mp3
```

For all files in a folder and its subfolder:
```
./MM3TagEncoding.py -i ~/Music/
```

-i option also applies to config file. 

```
./MM3TagEncoding.py -i -c <path to config file>
```

## Take caution of your mp3 files

Always make a backup before updating. I'm not responsible to any loss due to the use of this script.

## Add your encodings

This script by default comes with gb2312 and GBK encoding for detection. If the original encoding of your mp3 files is different than those, you can add your own encoding, so that they'll be used for candidate tag values.

In `MM3TagEncoding.py` line  13

```
encodings = ['gb2312', 'GBK', 'utf-8']
```

The last one needs to be `utf-8` to ensure that the correct tags (already encoded in UTF-8) won't show up as tags that need update.

## Behind the scene

The generation of `preferred` key follows two rules:

* Check if this tag's candidate value is part of the file name. If it is, the file name has higher chance of being correct.

* Get the shortest value from all the candidates. In most cases, bad encoding only lengthens the output. But I do find cases where the shortest value isn't the correct one.

This process can be improved. No plan on it yet.