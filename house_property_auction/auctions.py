import itertools

class Auction():    
    # available websites
    URLS = {
        'astegiudiziarie': 'https://www.astegiudiziarie.it',
        'astalegale': 'https://www.astalegale.net/',
        'REdiscount': 'https://www.realestatediscount.com/',
        'asteRE': 'https://www.asterealestate.it/index_A.jsp',
        'giustizia': 'https://pvp.giustizia.it/pvp/it/homepage.page'
    }
    
    def __init__(self):
        self.webcrawlers = []
        self.scrapeddata = []

    def add_webcrawler(self, webcrawler, *args, **kwargs):
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
