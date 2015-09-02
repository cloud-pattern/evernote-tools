#renamer.py | Robert Florance | 09.01.15

import sys

keys_filepath = "keys.txt"
old_title_charcount = 38
is_sandbox = True
notebook_name = "First Notebook"
tag_name = None 
offset = 0
limit = 5

keys = Renamer.get_keys(keys_filepath)

if len(sys.argv) > 1 and sys.argv[1] == "p":
    keys["token"] = keys["prod_token"]
    keys["url"] = keys["prod_url"]
    is_sandbox = False
    print "***running on production***"

if len(sys.argv) > 2:
    notebook_name = sys.argv[2]

if len(sys.argv) > 3:
    tag_name = sys.argv[3]
    
rn = Renamer(keys["customer_key"],
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
print "there were %s rename candidates" % len(noteslist)

while len(noteslist) > 0:
    for note_meta in noteslist:
        note = rn.get_note(note_meta, notestore)
        old_title = rn.get_note_title(note)
        if len(old_title) == old_title_charcount:
            print "matching title found: %s" % old_title
            new_title = rn.get_note_firstline(note)
            rn.update_title(note, notestore, new_title)
            print "title updated to: %s" % new_title
            rn.append_body(note, notestore, old_title)
            print "appended old title to body"
    offset += limit
    noteslist = rn.get_notemeta_list(notestore, notebook, tag, offset, limit)
        

   #ipython crap
   #n0 = rn.get_note(noteslist[0], notestore)
   #n0s = BS(n0.content)
   #n0f = n0s.findAll('en-note')[0]
   #n1 = rn.get_note(noteslist[1], notestore)
   #n1s = BS(n1.content)
   #n1f = n1s.findAll('en-note')[0]
   #n2 = rn.get_note(noteslist[2], notestore)
   #n2s = BS(n0.content)
   #n2f = n2s.findAll('en-note')[0]
   #retrieved_notes = [n0, n1, n2]
    
    
    
    
        

