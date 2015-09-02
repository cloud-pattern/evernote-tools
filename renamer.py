#Changes the titles of every note in a given note book
#   to the content of the first div in the note content.
import evernote as evernote
from evernote.api.client import EvernoteClient
import evernote.edam.notestore.NoteStore as NoteStore
from BeautifulSoup import BeautifulSoup


keys_filepath = "keys.txt"

f = open(keys_filepath, 'r')
keys= {}
for line in f:
    print line
    k, v = line.strip().split('^')
    keys[k.strip()] = v.strip()
f.close()

token = keys["token"]
#token = keys["sandbox_token"]

def get_client_oauth():
    client = EvernoteClient(consumer_key=keys["ckey"], 
                            consumer_secret=keys["csecret"],
                            sandbox=False)
    request_token = client.get_request_token(keys["prod_notestore_url"])
    print client.get_authorize_url(request_token)

    #now the user should paste that into the browser,
    #   ...accept the access, then paste the resulting url back in
    #   ...and hit enter
    auth_url = raw_input()
    vals = parse_query_string(auth_url)
    auth_token = client.get_access_token(
        request_token['oauth_token'],
        request_token['oauth_token_secret'],
        vals['oauth_verifier']
    )
    print "auth token:\n"
    print auth_token

    return client

def get_client_dev():
    client = EvernoteClient(token=token, sandbox=False)
    return client

def get_note_list(notestore,notebook, offset, limit):
    filter = evernote.edam.notestore.ttypes.NoteFilter()
    filter.notebookGuid = notebook.guid

    spec = NoteStore.NotesMetadataResultSpec()
    spec.includeNotebookGuid = True
    spec.includeCreated = True

    meta = notestore.findNotesMetadata(token, filter, offset, limit, spec)
    return meta.notes

def replace_titles(notes, notestore):
    for note in notes:
        noteguid = note.guid

        note = notestore.getNote(token, noteguid, True, False, False, False)
        notecontent = note.content

        notesoup = BeautifulSoup(notecontent)
        firstdiv = notesoup.findAll('div')[0]
        newtitle = firstdiv.contents[0]

        note.title = newtitle
        note = notestore.updateNote(note)

def list_titles(notes, notestore):
    for note in notes:
        noteguid = note.guid

        note = notestore.getNote(token, noteguid, True, False, False, False)
        notecontent = note.content

        notesoup = BeautifulSoup(notecontent)
        firstdiv = notesoup.findAll('div')[0]
        print firstdiv.contents[0]

def check_title(note):
    if len(note.title) == 33:
        print title

def parse_query_string(authorize_url):
    uargs = authorize_url.split('?')
    vals = {}
    if len(uargs) == 1:
        raise Exception('Invalid Authorization URL')
    for pair in uargs[1].split('&'):
        key, value = pair.split('=', 1)
        vals[key] = value
    return vals

client = get_client_dev()
ns = client.get_note_store()
nb = ns.listNotebooks()[11]
notes = get_note_list(ns, nb)
