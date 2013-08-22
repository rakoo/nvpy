# -*- coding: utf-8 -*-

"""
    Interface of remote storage that can work with nvpy. All remote
    backends have to subclass AbstractRemote.
"""

class AbstractRemote(object):

    def get_note(self, noteid):
        """ method to get a specific note

        Arguments:
            - noteid (string): ID of the note to get

        Returns:
            A tuple `(note, status)`

            - note (dict): note object
            - status (int): 0 on sucesss and -1 otherwise

        """
        raise NotImplementedError("Not implemented in AbstractRemote")

    def add_note(self, note):
        """wrapper function to add a note

        The function can be passed the note as a dict with the `content`
        property set, which is then directly send to the web service for
        creation. Alternatively, only the body as string can also be passed. In
        this case the parameter is used as `content` for the new note.

        Arguments:
            - note (dict or string): the note to add

        Returns:
            A tuple `(note, status)`

            - note (dict): the newly created note
            - status (int): 0 on sucesss and -1 otherwise

        """
        raise NotImplementedError("Not implemented in AbstractRemote")
