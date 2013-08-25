# -*- coding: utf-8 -*-
import couchdb
import time

from remote import AbstractRemote

"""
    Couchdb.py

    Python library to synchronize nvpy with a couchdb instance
"""

class CouchdbInitError(RuntimeError):
    pass

class Couchdb(AbstractRemote):

    def __init__(self, url="http://localhost:5984/", db="nvpy"):
        # The couchdb instance
        self.couch = couchdb.Server(url)

        # The db used
        # Note that it needs to be already existing, and I don't want to
        # manage credentials here so it has to be done outside.
        if db not in self.couch:
            raise CouchdbInitError(db + " db is not present on the couchdb instance. Please create it.")
        self.db = self.couch[db]

        # UUIDs to be used for new docs
        self.uuids = []

        # Keep a nvpy-side index of couchdb revs, to see if anything
        # changed on couchdb
        # Keys are note keys, values are _rev as returned by couchdb
        self.revs = {}

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

        return vr.rows, 0

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
        if isinstance(note, basestring):
            return self.update_note({"content": note})
        elif (isinstance(note, dict)) and "content" in note:
            return self.update_note(note)
        else:
            return "No string or valid note.", -1

    def delete_note(self, noteid):
        doc = self.db.get(noteid)
        try:
            self.db.delete(doc)
        except couchdb.ResourceConflict:
            # restart until it works
            # TODO: do not restart indefinitely
            self.delete_note(noteid)

        return {}, 0

    def update_note(self, note):
        is_update = "key" in note
        has_changed = None

        doc = self._nvpy_to_couchdb(note)
        id = doc["_id"]

        try:
            id, rev = self.db.save(doc)
            has_changed = False
        except couchdb.ResourceConflict:
            has_changed = True
            latest_doc = self.db.get(id)
            doc["_rev"] = latest_doc["_rev"]
            id, rev = self.db.save(doc)


        note, ok = self.get_note(id)
        if is_update and not has_changed:
            del note["content"]

        return note, ok

    def _has_doc_changed(self, latest_remote_doc, local_doc):
        if "tags" in latest_remote_doc:
            if "tags" in local_doc:
                if local_doc["tags"] != latest_remote_doc["tags"]:
                    return True

        if latest_remote_doc["content"] != local_doc["content"]:
            return True

        return False

    def _nvpy_to_couchdb(self, note):
        """
        Transform a nvpy note (with "key" for id) to a couchdb doc (with
        "_id").

        Also transform everything into utf-8.

        MUST be called before saving to couchdb
        """

        doc = {}
        # Encode to utf-8
        if isinstance(note["content"], str):
            doc["content"] = unicode(note["content"], "utf-8")
        elif isinstance(note["content"], unicode):
            doc["content"] = note["content"]

        if "tags" in note:
            doc["tags"] = [unicode(t, "utf-8") if isinstance(t,str) else t for t in note["tags"]]

        now = time.time()

        # TODO do this on couchdb side with an update handler
        doc["syncdate"] = now

        if "key" in note:
            doc["_id"] = note["key"]
            doc["modifydate"] = now
        else:
            doc["createdate"] = now
            doc["_id"] = self._next_uuid()

        # Add _rev if known
        if doc["_id"] in self.revs:
            doc["_rev"] = self.revs[doc["_id"]]

        return doc

    def _couchdb_to_nvpy(self, doc):
        """
        Transform a couchdb doc (with "_id") to a nvpy doc (with
        "_key") and remove the "_rev" key.

        Also transform everything into utf-8

            MUST be called after retrieving from couchdb
        """

        createdate = doc.get("createdate") or time.time()
        modifydate = doc.get("modifydate") or createdate
        note = {
            "key": doc["_id"],
            "createdate": createdate,
            "modifydate": modifydate,
            "syncdate": doc["syncdate"],
        }
        if isinstance(doc["content"], str):
            note["content"] = unicode(doc["content"], "utf-8")
        elif isinstance(doc["content"], unicode):
            note["content"] = doc["content"]

        if "tags" in doc:
            note["tags"] = [t.encode('utf-8') if isinstance(t,str) else t for t in doc["tags"]]

        # Extract the syncnum from the _rev
        rev = doc["_rev"]
        note["syncnum"] = int(rev.partition("-")[0])
        self.revs[note["key"]] = rev

        return note

    def _next_uuid(self):
        if len(self.uuids) == 0:
            self.uuids = self.couch.uuids()

        return self.uuids.pop()

