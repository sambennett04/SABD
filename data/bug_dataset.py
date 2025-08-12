"""
Each dataset has bug report ids and the ids of duplicate bug reports.
"""
class BugDataset(object):

    def __init__(self, file):
        f = open(file, 'r')
        self.info = f.readline().strip()

        self.bugIds = [id for id in f.readline().strip().split()]
        #reads all ids in test file, these are all duplicates
        self.duplicateIds = [id for id in f.readline().strip().split()]
