'''
Original version by xthepoet (https://github.com/xthepoet/pyBingSearchAPI)

This is designed for the new Azure Marketplace Bing Search API (released Aug 2012)

Inspired by https://github.com/mlagace/Python-SimpleBing and 
http://social.msdn.microsoft.com/Forums/pl-PL/windowsazuretroubleshooting/thread/450293bb-fa86-46ef-be7e-9c18dfb991ad
'''

import requests
import string

class BingSearchAPI(object):
    """ interface with the Bing search API """
    bing_api = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Composite?"
    bing_web_api = "https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web?"

    def __init__(self, key):
        self.key = key

    def replace_symbols(self, request):
        """ Custom urlencoder """
        # They specifically want %27 as the quotation which is a single quote '
        # We're going to map both ' and " to %27 to make it more python-esque
        request = string.replace(request, "'", '%27')
        request = string.replace(request, '"', '%27')
        request = string.replace(request, '+', '%2b')
        request = string.replace(request, ' ', '%20')
        request = string.replace(request, ':', '%3a')
        return request

    def search(self, sources, query, params):
        ''' This function expects a dictionary of query parameters and values.
            Sources and Query are mandatory fields.
            Sources is required to be the first parameter.
            Both Sources and Query requires single quotes surrounding it.
            All parameters are case sensitive. Go figure.

            For the Bing Search API schema, go to http://www.bing.com/developers/
            Click on Bing Search API. Then download the Bing API Schema Guide
            (which is oddly a word document file...pretty lame for a web api doc)
        '''
        request = 'Sources="' + sources + '"'
        request += '&Query="' + str(query) + '"'
        for key, value in params.iteritems():
            request += '&' + key + '=' + str(value)
        request = self.bing_api + self.replace_symbols(request)
        return requests.get(request, auth=(self.key, self.key))

    def search_web(self, query, params):
        """ search using the Bing web API """
        request = 'Query="' + str(query) + '"'
        for key, value in params.iteritems():
            request += '&' + key + '=' + str(value)
        request = self.bing_web_api + self.replace_symbols(request)
        return requests.get(request, auth=(self.key, self.key))

    def search_web_json(self, query, params):
        """ search using the Bing web API, results in JSON """
        request = 'Query="' + str(query) + '"'
        request += '&$format=json'
        for key, value in params.iteritems():
            request += '&' + key + '=' + str(value)
        request = self.bing_web_api + self.replace_symbols(request)
        return requests.get(request, auth=(self.key, self.key)).json()
        # return requests.get(request, auth=(self.key, self.key))


if __name__ == "__main__":
    my_key = "[your key]"
    query_string = "Brad Pitt"
    bing = BingSearchAPI(my_key)
    search_params = {
        'ImageFilters': '"Face:Face"',
        '$format': 'json',
        '$top': 10,
        '$skip': 0
    }
    print bing.search('image+web', query_string, search_params).json()
