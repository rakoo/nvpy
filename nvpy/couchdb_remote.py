# -*- coding: utf-8 -*-
import couchdb

from remote import AbstractRemote

"""
    Couchdb.py

    Python library to synchronize nvpy with a couchdb instance
"""

class Couchdb(AbstractRemote):

    def __init__(self, url="http://localhost:5984", db="nvpy"):
        # The couchdb instance
        self.couch = couchdb.Server(url)

        # The db used
        # Note that it needs to be already existing, and I don't want to
        # manage credentials here so it has to be done outside.
        self.db = self.couch[db]

        # UUIDs to be used for new docs
        self.uuids = []

    def get_note_list(self, qty=float("inf")):
        # TODO: use a "type":"note" in each note to list only real notes
        # TODO: separate the content (maybe in an attachment?) to
        # retrieve only the metadata, not the content. For the moment we
        # filter out the "content"
        opts = {
            "include_docs": True,
        }
        if qty != float("inf"):
            opts["limit"] = qty

        vr = self.db.view("_all_docs", self._row_without_content, **opts)

        return vr.rows

    def _row_without_content(self, row):
        """
        Transform the row of a view results to a doc without content.
        This function is called by the view function in the
        couchdb-python code
        """

        nocontent = self._couchdb_to_nvpy(row["doc"])
        del nocontent["content"]
        return nocontent

    def get_note(self, noteid):
        doc = self.db.get(noteid)
        if doc is not None:
            return self._couchdb_to_nvpy(doc), 0
        else:
            return None, -1


    def add_note(self, note):
        if type(note) == str:
            return self._update_note({"content": note})
        elif (type(note) == dict) and note.has_key("content"):
            return self._update_note(note)
        else:
            return "No string or valid note.", -1

    def _update_note(self, note):
        doc = self._nvpy_to_couchdb(note)
        ok, id, rev_or_exc = self.db.update([doc])[0]
        # TODO: treat !ok and rev_or_exc
        note = self._couchdb_to_nvpy(doc)

        if rev_or_exc is not None and id == note["key"]:
            return note, 0
        else:
            return note, 1

    def _nvpy_to_couchdb(self, note):
        """
        Transform a nvpy note (with "key" for id) to a couchdb doc (with
        "_id").

        Also transform everything into utf-8
        """

        # Encode to utf-8
        if isinstance(note["content"], str):
            note["content"] = unicode(note["content"], "utf-8")
        if "tags" in note:
            note["tags"] = [unicode(t, "utf-8") if isinstance(t,str) else t for t in note["tags"]]

        if "key" in note:
            note["_id"] = note["key"]
            del note["key"]
        else:
            note["_id"] = self._next_uuid()

        return note

    def _couchdb_to_nvpy(self, doc):
        """
        Transform a couchdb doc (with "_id") to a nvpy doc (with
        "_key") and remove the "_rev" key.

        Also transform everything into utf-8
        """

        doc["key"] = doc["_id"]
        del doc["_id"]

        del doc["_rev"]

        # Encode to utf-8
        doc["content"] = unicode(doc["content"])
        if "tags" in doc:
            doc["tags"] = [t.encode('utf-8') if isinstance(t,str) else t for t in doc["tags"]]

        return doc

    def _next_uuid(self):
        if len(self.uuids) == 0:
            self.uuids = self.couch.uuids()

        return self.uuids.pop()

