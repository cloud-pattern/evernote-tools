#entls.py | Robert Florance | 090215

import sys
import evernote
from evernote.api.client import EvernoteClient
import evernote.edam.notestore.NoteStore as NoteStore
from evernote.edam.type.ttypes import NoteSortOrder
from BeautifulSoup import NavigableString
from BeautifulSoup import BeautifulSoup as BS

class Entls:

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
        print request_token

        request_url = client.get_authorize_url(request_token)

        print request_url
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

        try:
            meta = notestore.findNotesMetadata(self.token, filter, offset, limit, spec)
            return meta.notes
        except Errors.EDAMSystemException, e:
            if e.errorCode == Errors.EDAMErrorCode.RATE_LIMIT_REACHED:
                print "Rate limit reached"
                print "Retry your request in %d seconds" % e.rateLimitDuration
                print "(at offset: %S)" % offset
                return None

    def get_note(self, note, notestore):
        return notestore.getNote(self.token, note.guid, True, False, False, False)

    def get_note_title(self, note):
        return note.title

    def get_title_length(self, note):
        return len(note.title)

    def get_note_firstline(self, note):
        notesoup = BS(note.content)
        first = notesoup.findAll('en-note')[0]
        line = first.contents[0]
        return unicode(line)

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
    
