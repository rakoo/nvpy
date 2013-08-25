# -*- coding: utf-8 -*-

import random
import unittest

from couchdb_remote import Couchdb

class TestSequenceFunctions(unittest.TestCase):
    """
    Tests the behaviour of the couchdb backend.

    To run the test, you need a running couchdb-talking instance
    (couchdb, pouchdb, anything else) running on localhost:5984. You
    also need to create a db called "nvpy-test", which you must delete
    after the test.

    """

    def setUp(self):
        self.couchBackend = Couchdb(db="nvpy-test")

    def test_AddStringNote(self):
        content = u'Some utf8 ćontent'
        newdoc, ok = self.couchBackend.add_note(content)
        self.assertEqual(ok, 0)
        self.assertTrue("key" in newdoc)

        self.assertTrue("content" in newdoc)
        self.assertEquals(newdoc["content"], content)

        self.assertFalse("tags" in newdoc)

    def test_AddContentNote(self):
        note = {
            "content": u"Some oẗher utf-8 cöntent",
            "tags":["tag1","tag2"]
        }

        newdoc, ok = self.couchBackend.add_note(note)
        self.assertEqual(ok, 0)
        self.assertTrue("key" in newdoc)

        self.assertTrue("content" in newdoc)
        self.assertEquals(newdoc["content"], note["content"])

        self.assertTrue("tags" in newdoc)
        self.assertEquals(newdoc["tags"], note["tags"])

    def test_GetNote(self):
        # This note has utf-8 content but it's not a unicode object,
        # it's a str, so we also test it doesn't break
        note = {
            "content": "Some oẗher utf-8 cöntent",
            "tags":["tag1","tag2"]
        }
        newnote, ok = self.couchBackend.add_note(note)
        self.assertEqual(ok, 0)

        newdoc, ok = self.couchBackend.get_note(newnote["key"])
        self.assertEqual(ok, 0)

        # Same checks as previous function
        self.assertTrue("content" in newdoc)
        self.assertEquals(newdoc["content"], unicode(note["content"],
                                                     "utf-8"))

        self.assertTrue("tags" in newdoc)
        self.assertEquals(newdoc["tags"], note["tags"])

    def test_ListNote(self):
        note1 = {
            "key": "key1",
            "content": "content1"
        }
        note2 = {
            "key": "key2",
            "content": "content2"
        }
        self.couchBackend.add_note(note1)
        self.couchBackend.add_note(note2)
        notes = {"key1": note1, "key2": note2}

        notes, status = self.couchBackend.get_note_list()
        self.assertEquals(0, status)
        # 6 because of the notes of other tests
        self.assertEquals(6, len(notes))

        # Only test note1 and note2
        for n in notes:
            if n["key"] not in ("key1", "key2"): # skip other tests' notes
                continue
            key = n["key"]
            if "tags" in n:
                self.assertEquals(n["tags"], notes[key]["tags"])

    def test_LimitedListNote(self):
        notes, status = self.couchBackend.get_note_list(1)
        self.assertEquals(0, status)
        self.assertEquals(1, len(notes))

    def test_DeleteNote(self):
        note = {
            "key": "note",
            "content": "some content",
        }
        self.couchBackend.add_note(note)
        self.couchBackend.delete_note("note")
        actual_note, ok = self.couchBackend.get_note("note")
        self.assertEquals(None, actual_note)
        self.assertEquals(-1, ok)

    def test_UpdateNote(self):
        note = {
            "key": "keyx",
            "content": "before"
        }
        new_note, ok = self.couchBackend.add_note(note)
        self.assertEquals(ok, 0)
        self.assertEquals(new_note["syncnum"], 1)

        createdate = new_note["createdate"]
        syncdate = new_note["syncdate"]
        self.assertIsNotNone(createdate)
        self.assertIsNotNone(syncdate)

        new_note["content"] = "after"
        new_new_note, ok = self.couchBackend.update_note(new_note)
        self.assertEquals(ok, 0)
        self.assertEquals(new_new_note["syncnum"], 2)

        modifydate = new_new_note["modifydate"]
        self.assertTrue(modifydate > createdate)
        self.assertTrue(modifydate > syncdate)
        newsyncdate = new_new_note["syncdate"]
        self.assertTrue(newsyncdate > syncdate)

    def test_DontReturnContentIfUnchanged(self):
        note = {
            "key": "keyy",
            "content": "some content"
        }
        new_note, ok = self.couchBackend.add_note(note)
        self.assertEquals(ok, 0)

        new_new_note, ok = self.couchBackend.update_note(note)
        self.assertEquals(ok, 0)
        self.assertFalse("content" in new_new_note)


suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
unittest.TextTestRunner(verbosity=2).run(suite)
