#renamer.py | Robert Florance | 09.01.15

import sys
import evernote
from evernote.api.client import EvernoteClient
import evernote.edam.notestore.NoteStore as NoteStore
from evernote.edam.type.ttypes import NoteSortOrder
from BeautifulSoup import NavigableString
from BeautifulSoup import BeautifulSoup as BS

class Renamer:

    def __init__(self, customer_key, customer_secret, token, url, is_sandbox):
        self.customer_key = customer_key
        self.customer_secret = customer_secret
        self.token = token
        self.url = url
        self.is_sandbox = is_sandbox

    def get_client_oauth(self):
        client = EvernoteClient(consumer_key = self.customer_key, 
                                consumer_secret = self.customer_secret,
                                sandbox = self.is_sandbox)
        request_token = client.get_request_token(self.url)

        print client.get_authorize_url(request_token)
        auth_url = raw_input()
        vals = parse_query_string(auth_url)

        auth_token = client.get_access_token(
            request_token['oauth_token'],
            request_token['oauth_token_secret'],
            vals['oauth_verifier'])
        return client

    def get_client_dev(self):
        client = EvernoteClient(token = self.token, sandbox = self.is_sandbox)
        return client

    def get_notestore(self, client):
        return client.get_note_store()

    def get_notebook(self, notestore, guid):
        for notebook in notestore.listNotebooks():
            if notebook.guid == guid:
                return notebook

    def get_notemeta_list(self, notestore, notebook, tag, offset, limit):
        filter = evernote.edam.notestore.ttypes.NoteFilter(order=NoteSortOrder.UPDATED)
        filter.notebookGuid = notebook.guid
        if tag != None:
            filter.tagGuids = [tag.guid]
        spec = NoteStore.NotesMetadataResultSpec(includeTitle = True,
                                                 includeTagGuids = True)

        meta = notestore.findNotesMetadata(self.token, filter, offset, limit, spec)
        return meta.notes

    def get_note(self, note, notestore):
            return notestore.getNote(self.token, note.guid, True, False, False, False)

    def get_note_title(self, note):
        return note.title

    def get_title_length(self, note):
        return len(note.title)

    def get_note_firstline(self, note):
        notesoup = BS(note.content)
        first = notesoup.findAll('en-note')[0]
        line = first.contents[0].text
        return line

    def update_title(self, note, notestore, new_title):
        note.title = new_title
        note = notestore.updateNote(note)
        return note

    def append_body(self, note, notestore, text):
        notesoup = BS(note.content)
        notesoup.findAll('en-note')[0].contents[-1].append(NavigableString(text))
        note.content = str(notesoup)
        note = notestore.updateNote(note)

    def get_note_tags(self, note):
        return 0

    def get_tag_by_name(self, notestore, tag_name):
        tag_list = notestore.listTags()
        for tag in tag_list:
            if tag.name == tag_name:
                return tag
    
    def get_notebook_by_name(self, notestore, notebook_name):
        notebook_list = notestore.listNotebooks()
        for notebook in notebook_list:
            if notebook.name== notebook_name:
                return notebook

    @staticmethod
    def parse_query_string(authorize_url):
        uargs = authorize_url.split('?')
        vals = {}
        if len(uargs) == 1:
            raise Exception('Invalid Authorization URL')
        for pair in uargs[1].split('&'):
            key, value = pair.split('=', 1)
            vals[key] = value
        return vals

    @staticmethod
    def get_keys(filepath):
        f = open(filepath, 'r')
        keys= {}
        for line in f:
            print line
            k, v = line.strip().split('^')
            keys[k.strip()] = v.strip()
        f.close()
        return keys
    

if __name__ == '__main__':

    keys_filepath = "keys.txt"
    old_title_charcount = 38
    is_sandbox = True
    notebook_name = "First Notebook"
    tag_name = None 
    offset = 0
    limit = 10

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
        

   # ipython crap
   # n0 = rn.get_note(noteslist[0], notestore)
   # n0s = BS(n0.content)
   # n0f = n0s.findAll('en-note')[0]
   # n1 = rn.get_note(noteslist[1], notestore)
   # n1s = BS(n1.content)
   # n1f = n1s.findAll('en-note')[0]
   # n2 = rn.get_note(noteslist[2], notestore)
   # n2s = BS(n0.content)
   # n2f = n2s.findAll('en-note')[0]
   # retrieved_notes = [n0, n1, n2]
    
    
    
    
        

