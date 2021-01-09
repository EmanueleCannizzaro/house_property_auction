from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools

class auctions():

    def __init__(self):
        self.webcrawlers = list()
        self.scrapeddata = list()

    def addwebcrawler(self, webcrawler, *args, **kwargs):
        '''
        Adds a ``webcrawler`` class to the mix for a single pass run.
        Instantiation will happen during ``run`` time.

        args and kwargs will be passed to the webcrawler as they are during
        instantiation.

        '''
        self.webcrawlers.append([(webcrawler, args, kwargs)])
        return len(self.webcrawlers) - 1

    def scrape(self):
        # Instantiate and execute
        iterwebcrawlers = itertools.product(*self.webcrawlers)
        for iterwebcrawler in iterwebcrawlers:
            for scls, sargs, skwargs in iterwebcrawler:
                webcrawler = scls(*sargs, **skwargs)
                self.scrapeddata.append(webcrawler.scrape())

    def cleandata(self):
        return

    def analyze(self):
        return

