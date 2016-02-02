"""
This module contains the Optimal BPM Repositories API
"""

import os
from bson.objectid import ObjectId


__author__ = 'nibo'

from dulwich.repo import Repo

class Repositories():
    """
        Repositories
    """

    def __init__(self, _db_access, _node):

        self.node = _node

    def refresh_cache(self):
        """

        :return:
        """
        pass



    def get_hash(self, _id, _user):
        """
        Returns the hashes
        :param _id: The _id of the repository
        :return: The hash of the repository
        """
        _result = self.node.find({"_id": ObjectId(_id)}, _user, _error_prefix_if_not_allowed = "This user doesn't have permissions for this repository.")
        _repo = Repo(os.path.join(_result["folder"], str(_id)))
        return _repo.head()


    def init_repository(self, _id, _folder=None):
        """
        Initialize a repository
        :param _id: repository_id
        :param _folder:
        :return:
        """
        if _folder is None:
            _repo_folder = os.path.join(os.path.expanduser(self.default_folder), str(_id))
        else:
            _repo_folder = os.path.join(os.path.expanduser(_folder), str(_id))

        from os import mkdir
        mkdir(_repo_folder)
        # TODO: Implement repositories (PROD-11)
        #_repo = Repo.init(_repo_folder)

        # return _repo.head()