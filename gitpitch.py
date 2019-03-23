import json
import pprint
import sys
import traceback
from string import Template
import argparse
import re

parser = argparse.ArgumentParser(description='Process some PITCHME.md.')
parser.add_argument('--game', dest='game', help='Game name. ')
args = parser.parse_args()


pp         = pprint.PrettyPrinter(indent=2, depth=5, width=50, compact=False)
pp.pprint(args);

integer    = 1
string     = ""
list       = []
dict       = {}
max_pixels = 500
test = ""
for x in args.game.split(" "):
    test += x.title()

filename = "".join(args.game.split(" "))+ ".json"
cover_image = "0.jpg"
outfile = 'PITCHME.md'


def to_warning(x):
    print("ERROR")
    print(x)
    print(type(x))
    print("ERROR")
    stack = traceback.extract_stack()
    print(type(stack))
    print(stack)
    print("ERROR")
    for line in stack:
        print(type(line))
        print(line)
    print("ERROR")
    sys.exit(0)

def from_int ( int ):
    if type(int) != integer.__class__:
        to_warning(int)
    return from_str(str(int))

def from_str ( str ):
    if type(str) != string.__class__:
        to_warning(str)
#    if len(str) > 0 and not re.search(r"^[\[\]{}:,]$", str):
#        str = '"' + str +  '"'
    return { "type": "string", "string": str, "length": len(str) }

def from_dict ( dict ):
    if type(dict) != dict.__class__:
        to_warning(dict)
    advDict = { "type": "list", "set": [], "size": 0, "length": 0}
    #advDict["set"].append(from_str("{"))
    for key in dict:
        if type(key) == string.__class__:
            advDict["set"].append(from_str(key))
        elif type(key) == integer.__class__:
            advDict["set"].append(from_int(key))
        else:
            to_warning(key)
    #   advDict["set"].append(from_str(":"))
        if type(dict[key]) == list.__class__:
            advDict["set"].append(from_list(dict[key]))
        elif type(dict[key]) == dict.__class__:
            advDict["set"].append(from_dict(dict[key]))
        elif type(dict[key]) == integer.__class__:
            advDict["set"].append(from_int(dict[key]))
        elif type(dict[key]) == string.__class__:
            advDict["set"].append(from_str(dict[key]))
        else:
            to_warning(dict[key])
    #   advDict["set"].append(from_str(","))
    #advDict["set"].append(from_str("}"))
    advDict["size"] = len(advDict["set"])
    for x in advDict["set"]:
        advDict["length"] += x["length"]
    for x in advDict["set"]:
        advDict["length"] += x["length"]
    return advDict

def from_list ( list ):
    if type(list) != [].__class__:
        to_warning(list)
    advList = { "type": "list", "set": [], "size": 0, "length": 0 }
    #advList["set"].append(from_str("["))
    for item in list:
        if type(item) == list.__class__:
            advList["set"].append(from_list(item))
        elif type(item) == dict.__class__:
            advList["set"].append(from_dict(item))
        elif type(item) == integer.__class__:
            advList["set"].append(from_int(item))
        elif type(item) == string.__class__:
            advList["set"].append(from_str(item))
        else:
            to_warning(list)
    #    advList["set"].append(from_str(","))
    #advList["set"].append(from_str("]"))
    advList["size"] = len(advList["set"])
    for x in advList["set"]:
        advList["length"] += x["length"]
    return advList
slide = ""
slide_ctr = 1
cover = Template("---?image=images/$cover_image&size=85% 85%&color=black\n")
seperator = Template("\n---\n\n")
header = Template("")
lgrid_start = Template("@snap[north-west span-50]\n@color[red]($breadCrumbs)<BR>\n")
list_start = Template("@color[blue]($title)\n@ol[list-bullets-black](false)\n")
list_item = Template("- $item\n")
list_stop = Template("@olend\n\n")
lgrid_stop = Template("@snapend\n\n")
rgrid = Template("@snap[north-east span-50]\n![Slide: $slide](images/$slide)\n@snapend\n\n")
haveHeader = 0

def start_slide(breadCrumbs, orTitle=""):
    global haveHeader
    start = ""
    title = ""
    if orTitle:
        title = orTitle
    else:
        title = breadCrumbs.pop()
    if haveHeader == 0:
        start += seperator.substitute()
        start += header.substitute()
        start += lgrid_start.substitute({"breadCrumbs": ': '.join(breadCrumbs)})
        start += list_start.substitute({"title":title})
        haveHeader = 1
    return start

def add_items(x):
    return list_item.substitute({"item": x["string"]})

def stop_slide():
    global haveHeader
    global slide_ctr
    global slide
    slide = str(slide_ctr) + ".jpg"
    slide_ctr += 1
    stop = ""
    if haveHeader == 1:
        stop += list_stop.substitute()
        stop += lgrid_stop.substitute()
        stop += rgrid.substitute({"slide": slide})
        haveHeader = 0

    return stop

def gitpitch_list(part, pastCrumbs):
    global haveHeader
    slides = ""
    for x in part["set"]:
        breadCrumbs = []
        breadCrumbs.extend(pastCrumbs)
        # A String and a list
        # A String and a String
        if x["type"] == "list" and x["size"] == 2 and x["set"][0]["type"] == "string" and x["set"][1]["type"] == "list":
            slides += stop_slide()
            breadCrumbs.append(x["set"][0]["string"])
            slides += gitpitch_list(x["set"][1], breadCrumbs)
        elif x["type"] == "list":
            slides += gitpitch_list(x, breadCrumbs)
        elif x["type"] == "string":
            if not haveHeader:
                slides += start_slide(breadCrumbs, x["string"])
            else:
                slides += add_items(x)
        else:
            to_warning(x)
    return slides

def main():
    with open(filename) as f:
        ret = json.load(f)
    gitpitch = ""
    gitpitch += cover.substitute({"cover_image": cover_image})

    if type(ret) == dict.__class__:
        gitpitch += gitpitch_list(from_list([ret]), [])
    else:
        gitpitch += gitpitch_list(from_list(ret), [])

    with open(outfile, 'w') as o:
        o.write(gitpitch)

if __name__ == "__main__":
    main()
    sys.exit(0)
