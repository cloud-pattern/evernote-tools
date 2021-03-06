#counter.py | Robert Florance | 090215

import sys
from entls import Entls

keys_filepath = "keys.txt"
old_title_charcount = 38
is_sandbox = True
notebook_name = "First Notebook"
tag_name = None 
offset = 0
limit = 5

keys = Entls.get_keys(keys_filepath)

if len(sys.argv) > 1 and sys.argv[1] == "p":
    keys["token"] = keys["prod_token"]
    keys["url"] = keys["prod_url"]
    is_sandbox = False
    print "***running on production***"

if len(sys.argv) > 2:
    notebook_name = sys.argv[2]

if len(sys.argv) > 3:
    tag_name = sys.argv[3]
    
rn = Entls(keys["customer_key"],
             keys["customer_secret"],
             keys["token"],
             keys["url"],
             is_sandbox)

#client = rn.get_client_oauth()
client = rn.get_client_dev()

notestore = rn.get_notestore(client)

notebook = rn.get_notebook_by_name(notestore, notebook_name)
if notebook == None:
    print "no such notebook"

tag = None
if tag_name != None: 
    found_tag = rn.get_tag_by_name(notestore, tag_name)
    if found_tag != None:
        tag = found_tag
    else:   
        print "no such tag, ignored"

noteslist = rn.get_notemeta_list(notestore, notebook, tag, offset, limit)

print len(noteslist)    
    

