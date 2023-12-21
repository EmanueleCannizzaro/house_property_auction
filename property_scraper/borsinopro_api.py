#!python

import json
import os
import requests


class BorsinoProAPI():
    
    def __init__(self, name:str=None):
        self.name = name
        
    @staticmethod
    def read_configuration(filename:str):
        with open(filename, 'r') as f:
            configuration = json.load(f)
            print(configuration['api.borsinopro.it'].keys())
            return configuration

    @staticmethod
    def get_property_type(configuration):
        url = configuration['api.borsinopro.it']['property_type']['url']
        assert(url == "https://api.borsinopro.it/rest/standard-v1/getImmobiliType/")
        method = configuration['api.borsinopro.it']['property_type']['method']
        headers = configuration['api.borsinopro.it']['property_type']['headers']
        payload = configuration['api.borsinopro.it']['property_type']['payload']
        response = requests.request(method, url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=4))
            assert(int(data['response']['options'][0]['id']) == 20)
        return data

    @staticmethod
    def get_contract_type(configuration):
        url = configuration['api.borsinopro.it']['contract_type']['url']
        assert(url == "https://api.borsinopro.it/rest/standard-v1/getContractType/")
        method = configuration['api.borsinopro.it']['contract_type']['method']
        headers = configuration['api.borsinopro.it']['contract_type']['headers']
        payload = configuration['api.borsinopro.it']['contract_type']['payload']
        response = requests.request(method, url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=4))
            assert(data['response']['options']['sale']['id'] == 'sale')
            
    @staticmethod
    def get_quotations(configuration, first_only:bool=False):
        url = configuration['api.borsinopro.it']['quotation']['url']
        assert(url == "https://api.borsinopro.it/rest/standard-v1/getQuotazione/")
        method = configuration['api.borsinopro.it']['quotation']['method']
        headers = configuration['api.borsinopro.it']['quotation']['headers']
        _payload = configuration['api.borsinopro.it']['quotation']['payload']
        _indices = configuration['api.borsinopro.it']['quotation'][_payload]
        print(_indices)
        if len(_indices) > 1:
            _data = []
        for ix in _indices:
            payload = configuration['api.borsinopro.it'][_payload][ix]
            print(payload)
            response = requests.request(method, url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=4))
                #assert(data['response']['options']['sale']['id'] == 'sale')
                if first_only:
                    return data
                else:
                    _data.append(data)
            else:
                raise ValueError(f'Status code is {response.status_code}!' )
        data = {
            'addresses': _data
        }
        return data
    
    @staticmethod
    def get_trends(configuration, first_only:bool=False):
        url = configuration['api.borsinopro.it']['trends']['url']
        assert(url == "https://api.borsinopro.it/rest/professional-v2/getTrends/")
        method = configuration['api.borsinopro.it']['trends']['method']
        headers = configuration['api.borsinopro.it']['trends']['headers']
        #files = configuration['api.borsinopro.it']['trends']['files']
        _payload = configuration['api.borsinopro.it']['trends']['payload']
        _indices = configuration['api.borsinopro.it']['trends'][_payload]
        print(_indices)
        if len(_indices) > 1:
            _data = []
        for ix in _indices:
            payload = configuration['api.borsinopro.it'][_payload][ix]
            print(payload)
            response = requests.request(method, url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=4))
                #assert(data['response']['options']['sale']['id'] == 'sale')
                if first_only:
                    return data
                else:
                    _data.append(data)
            else:
                raise ValueError(f'Status code is {response.status_code}!' )
        data = {
            'addresses': _data
        }
        return data

    @staticmethod
    def get_demographies(configuration, first_only:bool=False):
        url = configuration['api.borsinopro.it']['demography']['url']
        assert(url == "https://api.borsinopro.it/rest/professional-v2/getDemographic/")
        method = configuration['api.borsinopro.it']['demography']['method']
        headers = configuration['api.borsinopro.it']['demography']['headers']
        files = configuration['api.borsinopro.it']['demography']['files']
        _payload = configuration['api.borsinopro.it']['demography']['payload']
        _indices = configuration['api.borsinopro.it']['demography'][_payload]
        print(_indices)
        if len(_indices) > 1:
            _data = []
        for ix in _indices:
            payload = configuration['api.borsinopro.it'][_payload][ix]
            print(payload)
            response = requests.request(method, url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=4))
                #assert(data['response']['options']['sale']['id'] == 'sale')
                if first_only:
                    return data
                else:
                    _data.append(data)
            else:
                raise ValueError(f'Status code is {response.status_code}!' )
        data = {
            'addresses': _data
        }
        return data

    @staticmethod
    def get_timelines(configuration, first_only:bool=False):
        url = configuration['api.borsinopro.it']['timeline']['url']
        assert(url == "https://api.borsinopro.it/rest/professional-v2/getTempistiche/")
        method = configuration['api.borsinopro.it']['timeline']['method']
        headers = configuration['api.borsinopro.it']['timeline']['headers']
        files = configuration['api.borsinopro.it']['timeline']['files']
        _payload = configuration['api.borsinopro.it']['timeline']['payload']
        _indices = configuration['api.borsinopro.it']['timeline'][_payload]
        print(_indices)
        if len(_indices) > 1:
            _data = []
        for ix in _indices:
            payload = configuration['api.borsinopro.it'][_payload][ix]
            print(payload)
            response = requests.request(method, url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=4))
                #assert(data['response']['options']['sale']['id'] == 'sale')
                if first_only:
                    return data
                else:
                    _data.append(data)
            else:
                raise ValueError(f'Status code is {response.status_code}!' )
        data = {
            'addresses': _data
        }
        return data

    @staticmethod
    def get_addresses(configuration, first_only:bool=False):
        url = configuration['api.borsinopro.it']['address']['url']
        assert(url == "https://api.borsinopro.it/rest/standard-v1/getAddress/")
        method = configuration['api.borsinopro.it']['address']['method']
        headers = configuration['api.borsinopro.it']['address']['headers']
        #files = configuration['api.borsinopro.it']['address']['files']
        _payload = configuration['api.borsinopro.it']['address']['payload']
        _indices = configuration['api.borsinopro.it']['address'][_payload]
        print(_indices)
        if len(_indices) > 1:
            _data = []
        for ix in _indices:
            payload = configuration['api.borsinopro.it'][_payload][ix]
            print(payload)
            response = requests.request(method, url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=4))
                #assert(data['response']['options']['sale']['id'] == 'sale')
                if first_only:
                    return data
                else:
                    _data.append(data)
            else:
                raise ValueError(f'Status code is {response.status_code}!' )
        data = {
            'addresses': _data
        }
        return data

    @staticmethod
    def get_valuations(configuration, first_only:bool=False):
        url = configuration['api.borsinopro.it']['valuation']['url']
        assert(url == "https://api.borsinopro.it/rest/standard-v1/getValutazione/")
        method = configuration['api.borsinopro.it']['valuation']['method']
        headers = configuration['api.borsinopro.it']['valuation']['headers']
        files = configuration['api.borsinopro.it']['valuation']['files']
        _payload = configuration['api.borsinopro.it']['valuation']['payload']
        _indices = configuration['api.borsinopro.it']['valuation'][_payload]
        print(_indices)
        if len(_indices) > 1:
            _data = []
        for ix in _indices:
            payload = configuration['api.borsinopro.it'][_payload][ix]
            print(payload)
            response = requests.request(method, url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=4))
                #assert(data['response']['options']['sale']['id'] == 'sale')
                if first_only:
                    return data
                else:
                    _data.append(data)
            else:
                raise ValueError(f'Status code is {response.status_code}!' )
        data = {
            'addresses': _data
        }
        return data
