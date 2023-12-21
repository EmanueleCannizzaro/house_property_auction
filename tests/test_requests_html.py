
import json
from requests_html import HTML, HTMLSession
#from requests_html import AsyncHTMLSession


def test_requests_html_sync():
    session = HTMLSession()
    r = session.get('https://python.org/')
    

    print(r.html.links)
    print(r.html.absolute_links)
    about = r.html.find('#about', first=True)
    print(about.text)

    print(about.attrs)
    print(about.html)
    print(about.tag)

    print(about.lineno)
    print(about.find('a'))
    print(about.absolute_links)

    r.html.search('Python is a {} language')[0]

    r = session.get('https://github.com/')
    sel = 'body > div.application-main > div.jumbotron.jumbotron-codelines > div > div > div.col-md-7.text-center.text-md-left > p'

    print(r.html.find(sel, first=True))
    print(r.html.xpath('a'))

    r = session.get('https://python.org/')
    print(r.html.find('a', containing='kenneth'))
    
    
'''
async def test_requests_html_async():
    asession = AsyncHTMLSession()
    r = await asession.get('https://python.org/')

    async def get_pythonorg():
        r = await asession.get('https://python.org/')

    async def get_reddit():
        r = await asession.get('https://reddit.com/')

    async def get_google():
        r = await asession.get('https://google.com/')

    asession.run(get_pythonorg, get_reddit, get_google)
'''

'''
def test_requests_javascript_sync():
    """Return the output of the javascript function.

    >>> test_requests_javascript_sync
    '<time>25</time>'
    """
    
    session = HTMLSession()
    r = session.get('https://quotes.toscrape.com/js/')
    r.html.render()

    return r.html.search('Python 2 will retire in only {months} months!')['months']
'''

'''
def test_requests_javascript_async():
    r = asession.get('http://python-requests.org/')
    await r.html.arender()
    r.html.search('Python 2 will retire in only {months} months!')['months']
'''

'''
def test_requests_pagination_sync():
    session = HTMLSession()
    r = session.get('https://reddit.com')
    for html in r.html:
        print(html)
'''
        
'''
def test_requests_pagination_async():
    r = await asession.get('https://reddit.com')
    async for html in r.html:
        print(html)
'''

'''
def test_requests_next_sync():
    """Return the output of the javascript function.

    >>> test_requests_next_sync()
    'https://www.reddit.com/?count=25&after=t3_81pm82'
    """
    
    session = HTMLSession()
    r = session.get('https://reddit.com')
    r.html.next()
'''
   
'''
def test_requests_norequests_sync():
    doc = """<a href='https://httpbin.org'>"""

    html = HTML(html=doc)
    print(html.links)
    script = """
        () => {
            return {
                width: document.documentElement.clientWidth,
                height: document.documentElement.clientHeight,
                deviceScaleFactor: window.devicePixelRatio,
            }
        }
    """
    val = html.render(script=script, reload=False)

    print(val)
    print(html.html)
    
    #For using arender just pass async_=True to HTML.

    #html = HTML(html=doc, async_=True)
    #val = await html.arender(script=script, reload=False)
    #print(val)
'''

def test_requests_youtube_sync():
    #https://github.com/jhnwr/requests-html-render-yt/blob/master/requests-render.py
    
    #create the session
    session = HTMLSession()

    #define our URL
    url = 'https://www.youtube.com/channel/UC8tgRQ7DOzAbn9L7zDL8mLg/videos'

    #use the session to get the data
    r = session.get(url)

    #Render the page, up the number on scrolldown to page down multiple times on a page
    r.html.render(sleep=1, keep_page=True, scrolldown=25)
    #r.html.render(sleep=1, keep_page=True, scrolldown=1)

    #take the rendered html and find the element that we are interested in
    elements = r.html.find('#video-title-link')
    
    videos = {}
    videos['videos'] = []
    
    #loop through those elements extracting the text and link
    for item in elements:
        links = list(item.absolute_links)
        video = {}
        video ['title'] = item.text        
        video['links'] = [x.replace('://consent.', '://www.') for x in links]
        #print(video)
        videos['videos'].append(video)
        #break
    
    filename = 'UC8tgRQ7DOzAbn9L7zDL8mLg.json'
    with open(filename, 'w') as f:
        json.dump(videos, f, indent=4)
        
if __name__ == "__main__":
    test_requests_html_sync()
    test_requests_youtube_sync()
