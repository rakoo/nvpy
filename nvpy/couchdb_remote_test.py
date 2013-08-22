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
        content = 'Some utf8 ćontent'
        newdoc, ok = self.couchBackend.add_note(content)
        self.assertEqual(ok, 0)
        self.assertTrue("key" in newdoc)

        self.assertTrue("content" in newdoc)
        self.assertEquals(newdoc["content"], content)

        self.assertFalse("tags" in newdoc)

    def test_AddContentNote(self):
        note = {
            "content": "Some oẗher utf-8 cöntent",
            "tags":["tag1","tag2"]
        }

        newdoc, ok = self.couchBackend.add_note(note)
        self.assertEqual(ok, 0)
        self.assertTrue("key" in newdoc)

        self.assertTrue("content" in newdoc)
        self.assertEquals(newdoc["content"], note["content"])

        self.assertTrue("tags" in newdoc)
        self.assertEquals(newdoc["tags"], note["tags"])

suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
unittest.TextTestRunner(verbosity=2).run(suite)
