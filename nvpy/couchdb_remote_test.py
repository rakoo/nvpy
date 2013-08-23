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
        self.assertEquals(newdoc["content"], note["content"])

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

        notes = self.couchBackend.get_note_list()
        # 5 because of the notes of other tests
        self.assertEquals(5, len(notes))

        # Only test note1 and note2
        for n in notes:
            if n["key"] not in ("key1", "key2"): # skip other tests' notes
                continue
            key = n["key"]
            if "tags" in n:
                self.assertEquals(n["tags"], notes[key]["tags"])

    def test_LimitedListNote(self):
        notes = self.couchBackend.get_note_list(1)
        self.assertEquals(1, len(notes))

suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
unittest.TextTestRunner(verbosity=2).run(suite)
