
from datetime import datetime
from lxml import html
import matplotlib as mpl
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns


class RightmoveData:
    """The `RightmoveData` webscraper collects structured data on properties
    returned by a search performed on www.rightmove.co.uk

    An instance of the class provides attributes to access data from the search
    results, the most useful being `get_results`, which returns all results as a
    Pandas DataFrame object.

    The query to rightmove can be renewed by calling the `refresh_data` method.
    """
    def __init__(self, url: str, get_floorplans: bool = False):
        """Initialize the scraper with a URL from the results of a property
        search performed on www.rightmove.co.uk.

        Args:
            url (str): full HTML link to a page of rightmove search results.
            get_floorplans (bool): optionally scrape links to the individual
                floor plan images for each listing (be warned this drastically
                increases runtime so is False by default).
        """
        self._status_code, self._first_page = self._request(url)
        self._url = url
        self._validate_url()
        self._results = self._get_results(get_floorplans=get_floorplans)

    @staticmethod
    def _request(url: str):
        r = requests.get(url)
        return r.status_code, r.content

    def refresh_data(self, url: str = None, get_floorplans: bool = False):
        """Make a fresh GET request for the rightmove data.

        Args:
            url (str): optionally pass a new HTML link to a page of rightmove
                search results (else defaults to the current `url` attribute).
            get_floorplans (bool): optionally scrape links to the individual
                flooplan images for each listing (this drastically increases
                runtime so is False by default).
        """
        url = self.url if not url else url
        self._status_code, self._first_page = self._request(url)
        self._url = url
        self._validate_url()
        self._results = self._get_results(get_floorplans=get_floorplans)

    def _validate_url(self):
        """Basic validation that the URL at least starts in the right format and
        returns status code 200."""
        real_url = "{}://www.rightmove.co.uk/{}/find.html?"
        protocols = ["http", "https"]
        types = ["property-to-rent", "property-for-sale", "new-homes-for-sale"]
        urls = [real_url.format(p, t) for p in protocols for t in types]
        conditions = [self.url.startswith(u) for u in urls]
        conditions.append(self._status_code == 200)
        if not any(conditions):
            raise ValueError(f"Invalid rightmove search URL:\n\n\t{self.url}")

    @property
    def url(self):
        return self._url

    @property
    def get_results(self):
        """Pandas DataFrame of all results returned by the search."""
        return self._results

    @property
    def results_count(self):
        """Total number of results returned by `get_results`. Note that the
        rightmove website may state a much higher number of results; this is
        because they artificially restrict the number of results pages that can
        be accessed to 42."""
        return len(self.get_results)

    @property
    def average_price(self):
        """Average price of all results returned by `get_results` (ignoring
        results which don't list a price)."""
        total = self.get_results["price"].dropna().sum()
        return total / self.results_count

    def summary(self, by: str = None):
        """DataFrame summarising results by mean price and count. Defaults to
        grouping by `number_bedrooms` (residential) or `type` (commercial), but
        accepts any column name from `get_results` as a grouper.

        Args:
            by (str): valid column name from `get_results` DataFrame attribute.
        """
        if not by:
            by = "type" if "commercial" in self.rent_or_sale else "number_bedrooms"
        assert by in self.get_results.columns, f"Column not found in `get_results`: {by}"
        df = self.get_results.dropna(axis=0, subset=["price"])
        groupers = {"price": ["count", "mean"]}
        df = df.groupby(df[by]).agg(groupers)
        df.columns = df.columns.get_level_values(1)
        df.reset_index(inplace=True)
        if "number_bedrooms" in df.columns:
            df["number_bedrooms"] = df["number_bedrooms"].astype(int)
            df.sort_values(by=["number_bedrooms"], inplace=True)
        else:
            df.sort_values(by=["count"], inplace=True, ascending=False)
        return df.reset_index(drop=True)

    @property
    def rent_or_sale(self):
        """String specifying if the search is for properties for rent or sale.
        Required because Xpaths are different for the target elements."""
        if "/property-for-sale/" in self.url or "/new-homes-for-sale/" in self.url:
            return "sale"
        elif "/property-to-rent/" in self.url:
            return "rent"
        elif "/commercial-property-for-sale/" in self.url:
            return "sale-commercial"
        elif "/commercial-property-to-let/" in self.url:
            return "rent-commercial"
        else:
            raise ValueError(f"Invalid rightmove URL:\n\n\t{self.url}")

    @property
    def results_count_display(self):
        """Returns an integer of the total number of listings as displayed on
        the first page of results. Note that not all listings are available to
        scrape because rightmove limits the number of accessible pages."""
        tree = html.fromstring(self._first_page)
        xpath = """//span[@class="searchHeader-resultCount"]/text()"""
        return int(tree.xpath(xpath)[0].replace(",", ""))

    @property
    def page_count(self):
        """Returns the number of result pages returned by the search URL. There
        are 24 results per page. Note that the website limits results to a
        maximum of 42 accessible pages."""
        page_count = self.results_count_display // 24
        if self.results_count_display % 24 > 0:
            page_count += 1
        # Rightmove will return a maximum of 42 results pages, hence:
        if page_count > 42:
            page_count = 42
        return page_count

    def _get_page(self, request_content: str, get_floorplans: bool = False):
        """Method to scrape data from a single page of search results. Used
        iteratively by the `get_results` method to scrape data from every page
        returned by the search."""
        # Process the html:
        tree = html.fromstring(request_content)

        # Set xpath for price:
        if "rent" in self.rent_or_sale:
            xp_prices = """//span[@class="propertyCard-priceValue"]/text()"""
        elif "sale" in self.rent_or_sale:
            xp_prices = """//div[@class="propertyCard-priceValue"]/text()"""
        else:
            raise ValueError("Invalid URL format.")

        # Set xpaths for listing title, property address, URL, and agent URL:
        xp_titles = """//div[@class="propertyCard-details"]\
        //a[@class="propertyCard-link"]\
        //h2[@class="propertyCard-title"]/text()"""
        xp_addresses = """//address[@class="propertyCard-address"]//span/text()"""
        xp_weblinks = """//div[@class="propertyCard-details"]//a[@class="propertyCard-link"]/@href"""
        xp_agent_urls = """//div[@class="propertyCard-contactsItem"]\
        //div[@class="propertyCard-branchLogo"]\
        //a[@class="propertyCard-branchLogo-link"]/@href"""

        # Create data lists from xpaths:
        price_pcm = tree.xpath(xp_prices)
        titles = tree.xpath(xp_titles)
        addresses = tree.xpath(xp_addresses)
        base = "http://www.rightmove.co.uk"
        weblinks = [f"{base}{tree.xpath(xp_weblinks)[w]}" for w in range(len(tree.xpath(xp_weblinks)))]
        agent_urls = [f"{base}{tree.xpath(xp_agent_urls)[a]}" for a in range(len(tree.xpath(xp_agent_urls)))]

        # Optionally get floorplan links from property urls (longer runtime):
        floorplan_urls = list() if get_floorplans else np.nan
        if get_floorplans:
            for weblink in weblinks:
                status_code, content = self._request(weblink)
                if status_code != 200:
                    continue
                tree = html.fromstring(content)
                xp_floorplan_url = """//*[@id="floorplanTabs"]/div[2]/div[2]/img/@src"""
                floorplan_url = tree.xpath(xp_floorplan_url)
                if floorplan_url:
                    floorplan_urls.append(floorplan_url[0])
                else:
                    floorplan_urls.append(np.nan)

        # Store the data in a Pandas DataFrame:
        data = [price_pcm, titles, addresses, weblinks, agent_urls]
        data = data + [floorplan_urls] if get_floorplans else data
        temp_df = pd.DataFrame(data)
        temp_df = temp_df.transpose()
        columns = ["price", "type", "address", "url", "agent_url"]
        columns = columns + ["floorplan_url"] if get_floorplans else columns
        temp_df.columns = columns

        # Drop empty rows which come from placeholders in the html:
        temp_df = temp_df[temp_df["address"].notnull()]

        return temp_df

    def _get_results(self, get_floorplans: bool = False):
        """Build a Pandas DataFrame with all results returned by the search."""
        results = self._get_page(self._first_page, get_floorplans=get_floorplans)

        # Iterate through all pages scraping results:
        for p in range(1, self.page_count + 1, 1):

            # Create the URL of the specific results page:
            p_url = f"{str(self.url)}&index={p * 24}"

            # Make the request:
            status_code, content = self._request(p_url)

            # Requests to scrape lots of pages eventually get status 400, so:
            if status_code != 200:
                break

            # Create a temporary DataFrame of page results:
            temp_df = self._get_page(content, get_floorplans=get_floorplans)

            # Concatenate the temporary DataFrame with the full DataFrame:
            frames = [results, temp_df]
            results = pd.concat(frames)

        return self._clean_results(results)

    @staticmethod
    def _clean_results(results: pd.DataFrame):
        # Reset the index:
        results.reset_index(inplace=True, drop=True)

        # Convert price column to numeric type:
        results["price"].replace(regex=True, inplace=True, to_replace=r"\D", value=r"")
        results["price"] = pd.to_numeric(results["price"])

        # Extract short postcode area to a separate column:
        pat = r"\b([A-Za-z][A-Za-z]?[0-9][0-9]?[A-Za-z]?)\b"
        results["postcode"] = results["address"].astype(str).str.extract(pat, expand=True)[0]

        # Extract full postcode to a separate column:
        pat = r"([A-Za-z][A-Za-z]?[0-9][0-9]?[A-Za-z]?[0-9]?\s[0-9]?[A-Za-z][A-Za-z])"
        results["full_postcode"] = results["address"].astype(str).str.extract(pat, expand=True)[0]

        # Extract number of bedrooms from `type` to a separate column:
        pat = r"\b([\d][\d]?)\b"
        results["number_bedrooms"] = results["type"].astype(str).str.extract(pat, expand=True)[0]
        results.loc[results["type"].str.contains("studio", case=False), "number_bedrooms"] = 0
        results["number_bedrooms"] = pd.to_numeric(results["number_bedrooms"])

        # Clean up annoying white spaces and newlines in `type` column:
        results["type"] = results["type"].str.strip("\n").str.strip()

        # Add column with datetime when the search was run (i.e. now):
        now = datetime.now()
        results["search_date"] = now

        return results
    
    def rightmove_webscrape(self, rightmove_url):
        '''
        The purpose of the function is to extract data from the listings on the http://www.rightmove.co.uk/ 
        property website. 
        After passing the function the long url from the first results page of a search, 
        the function will extract the price, property type, address details, and 
        url for the specific property listing. 
        It will also extract the postcode stems from the address details (e.g. 'N1') and 
        store this in a separate column; and extract the number of bedrooms 
        from the property type as a separate column. 
        If more than one page of results are returned by the search then 
        the function will automatically cycle through all pages collecting the data 
        (which means it can take a while to return the results 
        if the search criteria returns thousands of results).
        '''
        
        # Get the start & end of the web url around the index value
        start,end = rightmove_url.split('&index=')
        url_start = start+'&index='
        url_end = end[1:]
        
        # Initialise variables
        price_pcm=[]
        titles=[]
        addresses=[]
        weblinks=[]
        page_counts=[]
        
        # Initialise pandas DataFrame for results.
        df = pd.DataFrame(columns=['price','type','address','url'])

        # Get the total number of results from the search
        page = requests.get(rightmove_url)
        tree = html.fromstring(page.content)
        xp_result_count = '//span[@class="searchHeader-resultCount"]/text()'
        result_count = int(tree.xpath(xp_result_count)[0].replace(",", ""))
        
        # Turn the total number of search results into number of iterations for the loop
        loop_count = result_count / 24
        if result_count % 24 > 0:
            loop_count = loop_count + 1
        loop_count = int(loop_count)
            
        # Set the Xpath variables for the loop
        xp_prices = '//span[@class="propertyCard-priceValue"]/text()'
        xp_titles = '//div[@class="propertyCard-details"]//a[@class="propertyCard-link"]//h2[@class="propertyCard-title"]/text()'
        xp_addresses = '//address[@class="propertyCard-address"]/text()'
        xp_weblinks = '//div[@class="propertyCard-details"]//a[@class="propertyCard-link"]/@href'

        # Start the loop through the search result web pages
        for pages in range(0, loop_count, 1):
            rightmove_url = url_start+str(pages*24)+url_end
            page = requests.get(rightmove_url)
            tree = html.fromstring(page.content)
            
            # Reset variables
            price_pcm=[]
            titles=[]
            addresses=[]
            weblinks=[]

            # Create data lists from Xpaths
            for val in tree.xpath(xp_prices):
                price_pcm.append(val)
            for val in tree.xpath(xp_titles):
                titles.append(val)
            for val in tree.xpath(xp_addresses):
                addresses.append(val)
            for val in tree.xpath(xp_weblinks):
                weblinks.append(val)

        # Convert data to temporary DataFrame
            data = [price_pcm, titles, addresses, weblinks]
            temp_df= pd.DataFrame(data)
            temp_df = temp_df.transpose()
            temp_df.columns=['price','type','address','url']
            
        # Drop empty rows from DataFrame which come from placeoholders in html file.
            temp_df = temp_df[temp_df.url != '/property-for-sale/property-0.html']
        
        # Join temporary DataFrame to main results DataFrame.
            frames = [df,temp_df]
            df = pd.concat(frames)

        # Renumber results DataFrame index to remove duplicate index values.
        df = df.reset_index(drop=True)

        # Convert price column to numeric values for analysis.
        df.price = df.price.replace(regex=True, to_replace=r'\D', value=r'')
        df.price = pd.to_numeric(df.price)

        # Extract postcode areas to separate column.
        df['postcode'] = df['address'].str.extract(r'\b([A-Za-z][A-Za-z]?[0-9][0-9]?[A-Za-z]?)\b',expand=True)
        
        # Extract number of bedrooms from 'type' column.
        df['number_bedrooms'] = df.type.str.extract(r'\b([\d][\d]?)\b',expand=True)
        df['type'] = df['type'].fillna('')
        df.loc[df['type'].str.contains('studio', case=False), 'number_bedrooms'] = 0

        # Add in search_date column with date website was queried (i.e. today's date).
        now = datetime.today().strftime("%d/%m/%Y")
        df['search_date'] = now

        # Optional line to export the results to CSV if you wish to inspect them in an alternative program.
        #     df.to_csv('rightmove_df.csv',encoding='utf-8')

        print(f"The search returned a total of {len(df)} results.")
        return df
    
    @staticmethod
    def plot_by_bedroom(df_by_bedroom):
        plt.figure(num=1,figsize=(10,8))
        plt.bar(df_by_bedroom['number_bedrooms'],df_by_bedroom['count'],align='center')
        plt.xlabel('number bedrooms')
        plt.ylabel('count')
        plt.title('count by number of bedrooms')
        plt.ticklabel_format(style='plain')

        plt.figure(num=2,figsize=(10,8))
        plt.bar(df_by_bedroom['number_bedrooms'],df_by_bedroom['average_price'],align='center')
        plt.xlabel('number bedrooms')
        plt.ylabel('average price')
        plt.title('average price by number of bedrooms')
        plt.ticklabel_format(style='plain')
        plt.show()
        
    def plot_by_type(self):
        # The .summary() method summarises the results by number of bedrooms:
        df = self.summary()
        
        labels = [f"{i}-bed" if i != 0 else "Studio" for i in df["number_bedrooms"]]
        x = df.index
        y = df["count"]
        sns.set_style("dark")
        sns.set_palette(sns.color_palette("pastel"))
        fig, ax = plt.subplots(figsize=(12, 8))
        plt.title("London Rentals: Number of Listings by Apartment Type", size = 18)
        plt.xlabel("Apartment Type", size = 14)
        plt.ylabel("Number of Listings", size = 14)
        plt.xticks(size = 14)
        plt.yticks(size = 12)
        plt.bar(x, y, tick_label=labels)
        plt.show()

    def plot_by_postcode(self, number_to_plot:int=25):    
        # The .summary() method summarises the results by number of bedrooms:
        df = self.summary("postcode")\
        .sort_values(by = "count", ascending = False)\
        .reset_index(drop = True)[:number_to_plot]

        x = df["postcode"]
        y = df["count"]
        ymax = ((df["count"].max() // 5) + 1) * 5
        
        sns.set_palette(sns.color_palette("pastel"))
        fig, ax = plt.subplots(figsize=(15, 7))
        plt.title("London Rentals: {} Most Active Postcode Areas".format(number_to_plot), size = 18)
        plt.xlabel("Postcode Area", size = 14)
        plt.ylabel("Number of Listings", size = 14)
        plt.xticks(rotation = 45, size = 14)
        plt.yticks(range(0, ymax, 5), size = 14)
        plt.bar(x, y)
        plt.show()

    @staticmethod
    def add_borough(df, postcodes_df):
        """Add the borough column based on lookup table using data 
        from https://www.doogal.co.uk/PostcodeDownloads.php."""

        # Useful columns are Postcode and District, so drop the rest:
        cols_to_drop = postcodes_df.columns.drop(["Postcode", "District"])
        postcodes_df = postcodes_df.drop(labels=cols_to_drop, axis=1)

        # Only need the stem of the postcode (e.g. from "N1 6RQ": "N1"):
        postcodes_df["stem"] = postcodes_df["Postcode"].str.split(" ").str.get(0)

        # Drop duplicate rows and reset index:
        postcodes_df = postcodes_df.drop_duplicates()
        postcodes_df = postcodes_df.reset_index(drop=True)

        # Some postcodes cross multiple districts, e.g. N1 is in Hackney 
        # and Islington. To deal with this take a pivot table of postcode
        # by District, and keep the District with the maximum count.

        # Create pivot table of postcode stem by how many postcodes in each District:
        pivot = pd.DataFrame(pd.pivot_table(postcodes_df, values = "Postcode",index = "stem",
                                            columns = "District", aggfunc = "count"))

        # Keep max District count for each postcode_stem:
        lookup = pd.DataFrame(pivot.idxmax(axis = 1))
        lookup = lookup.reset_index()

        # Rename columns:
        lookup = lookup.rename(columns={"stem":"postcode", 0:"borough"})
        lookup['postcode'] = lookup['postcode'].astype(str)
        
        df['postcode'] = df['postcode'].astype(str)
        
        # Merge the borough column into main DataFrame:
        df = pd.merge(df, lookup, how="left", on="postcode")
        return df

    @staticmethod
    def add_inner_outer(df:pd.DataFrame, filename:str):
        """Adds a classification column of inner/outer London based on borough."""
        io_london = pd.read_csv(filename, header = None)
        io_london = io_london.rename(columns = {0:"borough", 1:"inner_outer"})
        out_df = pd.merge(df, io_london, how="left", left_on="borough", right_on="borough")
        return out_df

    @staticmethod
    def remove_null_rows(df:pd.DataFrame, col):
        out_df = df[df[col].notnull()]
        out_df = out_df.reset_index(drop=True)
        return out_df

    def summary_df(self, df, col_to_group, col_to_summarise, filename):
        """Create a summary of the df by col."""
        
        groupers = {col_to_summarise:["count", "mean"]}
        out_df = df.groupby(df[col_to_group]).agg(groupers).astype(int)
        out_df.columns = out_df.columns.get_level_values(1)
        out_df = out_df.reset_index()
        out_df = self.add_inner_outer(out_df, filename)
        # Drop any non-London postcodes that have snuck in there:
        out_df = out_df.dropna(subset=["inner_outer"])
        out_df = out_df.reset_index(drop=True)
        return out_df

    @staticmethod
    def good_axis_max(axis_max):
        """Helper function for charts to provide aesthtically pleasing axis."""
        magnitude = 10**(len(str(axis_max))-1)
        max_axis = ((axis_max // magnitude) + 1) * magnitude
        return max_axis

    @staticmethod
    def good_axis_min(axis_min):
        """Helper function for charts to provide aesthtically pleasing axis."""
        magnitude = 10**(len(str(axis_min))-1)
        min_axis = (((axis_min) // magnitude)) * magnitude
        if axis_min == min_axis and axis_min > 0:
            min_axis -= magnitude
        return min_axis

    def borough_scatterplot(self, df, x, y, labels, title, xlabel, ylabel, hue, size=7, aspect=1.2):
        """Create a scatter plot of price & number of listings by borough."""
        
        df.sort_values(by = ["mean", "count"])
        df = df.reset_index(drop=True)
        
        sns.set_style("white")
        scatter = sns.lmplot(x = x, y = y, data = df, fit_reg = False, hue = hue,
                            palette = sns.color_palette("bright"),
                            legend=False, aspect=aspect)
                            #legend=False, size=size, aspect=aspect)

        scatter.set(xlim = (self.good_axis_min(df[x].min()), self.good_axis_max(df[x].max()) + 0.1), 
                            ylim = (self.good_axis_min(df[y].min()), self.good_axis_max(df[y].max())))
            
        # Add data labels:
        style = dict(size=10, color='gray')
        for r in range(len(df)):
            x = df.loc[r, "count"]
            y = df.loc[r, "mean"]
            label = df.loc[r, "borough"]
            scatter.ax.text(x, y, label, **style)

        plt.title(title, size=14)
        plt.legend(loc = "upper right", bbox_to_anchor=(1.2, 1), fontsize = "xx-large", )
        plt.xlabel(xlabel, size=14)
        plt.ylabel(ylabel, size=14)
        plt.xticks(size = 14)
        plt.yticks(size = 14)
        plt.show()

    def cheap_listings(self, postcodes_df, boroughs = [], number=10):
        df = self.get_results
        df = self.add_borough(df, postcodes_df)
        df = df[df["borough"].isin(boroughs)]
        df = df.sort_values(by="price", ascending=True)
        df = df.reset_index(drop=True)
        for l in range(number):
            print("£{} - {} - {}" .format(df.loc[l, "price"], df.loc[l, "borough"], df.loc[l, "url"]))

    @staticmethod
    def fix_characters_in_column_names(df:pd.DataFrame):
        to_replace = (" ",")","(",":","/","%","-")
        for i in to_replace:
            df.columns = df.columns.str.replace(i, "_")
        
    def to_dataframe(self):
        _dfs = []
        #df = pd.DataFrame()
        pbar = tqdm(self.urls)
        for url in pbar:
            self.url = url
            _dfs.append(pd.DataFrame.from_dict(self.info, orient='index').T)
        df = pd.concat(_dfs)
        df = df.reset_index(drop=True)
        return df
