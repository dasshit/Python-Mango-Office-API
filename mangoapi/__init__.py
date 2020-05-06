#!/usr/bin/env python
import requests, hashlib, json, random, time, os
from datetime import datetime


def hash(data, self):            
    return hashlib.sha256(self.key.encode('utf-8') +
                                data.encode('utf-8') +
                                self.salt.encode('utf-8')).hexdigest()

def stringify(data):
    return json.dumps(data, separators=(',', ':'))

class MangoAPI:
    
    def __init__(self, api_url, key, salt):
        self.url = api_url
        self.key = key
        self.salt = salt
         

    def request(self, data=None, api_command=None):
        if self.url == None:
            self.url = 'https://app.mango-office.ru/vpbx/'
        else:
            self.url = self.url
        if data == None:
            data = {}
        else:
            data = data
        if api_command == None:
            return 'Undefined method'
        else:
            stringified = stringify(data)
            params = {'vpbx_api_key': self.key,
                        'sign': hash(stringified, self),
                        'json': stringified}
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            return requests.post((self.url + api_command),
                                    data=params,
                                    headers=headers).text
    def sms(self, command_id=None, from_ext=None, text='Test', number=None, sender=None):
        if number == None:
            return 'Please, specify number'
        elif from_ext == None:
            return 'Please, specify user extension'
        else:
            data = {"text":text,
                     "from_extension":from_ext,
                     "to_number":number}
            if command_id != None:
                tier = {"command_id":command_id}
                data.update(tier)
            else:
                tier = {"command_id":"base"}
                data.update(tier)
            if sender != None:
                tier = {"sms_sender":sender}
                data.update(tier)
            return self.request(data, '/commands/sms')
    
    def callback(self, command_id=None, from_ext=None, from_num=None, to_num=None, line=None, sip_head=None):
        if from_ext == None:
            return "Please, specify user extension"
        elif to_num == None:
            return "Please, specify calling number"
        else:
            data = {}
            if command_id!=None:
                tier = {"command_id":command_id}
                data.update(tier)
            else:
                tier = {"command_id":'base'}
                data.update(tier)
            if from_ext!=None and from_num!=None:
                tier = {'from':{'extension':from_ext, 'number':from_num}, "to_number" : to_num}
                data.update(tier)
            else:
                tier = {'from':{'extension':from_ext}, "to_number" : to_num}
                data.update(tier)
        if line != None:
            tier = {"line_number" : line}
            data.update(tier)
        if sip_head != None:
            tier = {"sip_headers": sip_head}
            data.update(tier)
        return self.request(data, '/commands/callback')
            
                
    def group_callback(self, command_id=None, from_ext=None, to_num=None, line=None):
        if from_ext == None:
            return "Please, specify user extension"
        elif to_num == None:
            return "Please, specify calling number"
        else:
            data = {}
            if command_id!=None:
                tier = {"command_id":command_id}
                data.update(tier)
            else:
                tier = {"command_id":'base'}
                data.update(tier)
                tier = {'from':from_ext, "to" : to_num}
                data.update(tier)
        if line != None:
            tier = {"line_number" : line}
            data.update(tier)
        return self.request(data, '/commands/callback_group')
    
    def hangup(self, command_id=None, call_id=None):
        if command_id == None:
            command_id = 'base'
        if call_id == None:
            return 'Please specify call_id'
        else:
            data = {'command_id':command_id, 'call_id':call_id}
            return self.request(data, '/commands/call/hangup')
        
    def start_record(self, command_id=None, call_id=None, call_party_number=None):
        if command_id == None:
            command_id = 'base'
        if call_id == None:
            return 'Please specify call_id'
        else:
            data = {'command_id':command_id, 'call_id':call_id}
            if call_party_number != None:
                tier = {'call_party_number':call_party_number}
                data.update(tier)
            else:
                return 'Please specify call_party_number'
            return self.request(data, '/commands/recording/start')
    
    def start_play(self, command_id=None, call_id=None, after_play_time=None, internal_id=None):
        if command_id == None:
            command_id = 'base'
        if call_id == None:
            return 'Please specify call_id'
        else:
            data = {'command_id':command_id, 'call_id':call_id}
            if after_play_time != None:
                tier = {'after_play_time':after_play_time}
                data.update(tier)
            if internal_id != None:
                tier = {'internal_id':internal_id}
                data.update(tier)
            return self.request(data, '/commands/play/start')
        
    def route(self, command_id=None, call_id=None, to_number=None, sip_headers=None):
        if command_id == None:
            command_id = 'base'
        if call_id == None:
            return 'Please specify call_id'
        if to_number == None:
            return 'Please specify number transfer to'
        else:
            data = {'command_id':command_id, 'call_id':call_id}
            if to_number == None:
                return 'Please specify number to route'
            else:
                tier = {'to_number':to_number}
                data.update(tier)
                if sip_headers!=None:
                    tier = {'sip_headers':sip_headers}
                    data.update(tier)
                return self.request(data, '/commands/route')
            
    def transfer(self, command_id=None, call_id=None, to_number=None, initiator=None, method=None):
        if command_id == None:
            command_id = 'base'
        if call_id == None:
            return 'Please specify call_id'
        if method == None:
            return 'Please specify transfer method'
        if to_number == None:
            return 'Please specify number transfer to'
        if initiator  == None:
            return 'Please specify initiator'
        else:
            data = {'command_id':command_id, 'call_id':call_id, 'method':method, 'to_number':to_number, 'initiator':initiator}
            if initiator!=None:
                tier = {'initiator':initiator}
                data.update(tier)
            return self.request(data, '/commands/transfer')
        
    def get_stats_from(self, request_id=None, from_ext=None, from_num=None, date_from=None, date_to=None, fields=None):
        if date_from != None and date_to!=None and (from_ext!=None or from_num!=None):
            data = {'date_from':str(date_from),
                   'date_to':str(date_from)}
            if from_ext != None:
                tier = {'from':{'extenstion':from_ext}}
                data.update(tier)
            else:
                tier = {'from':{'number':from_num}}
                data.update(tier)
            if fields!=None:
                tier = {'fields':fields}
                data.update(tier)
            if request_id!=None:
                tier = {'request_id':request_id}
                data.update(tier)
            result = json.loads(self.request(data, '/stats/request'))
            data = {}
            if request_id!=None:
                tier = {'request_id':request_id}
                data.update(tier)
            try:
                if result['key']!=None:
                    tier = {'key':result['key']}
                    data.update(tier)
            except KeyError:
                return 'Error'
            finally:
                return self.request(data, '/stats/result')
        else:
            return 'Please specify params'
            
    def get_stats_to(self, request_id=None, to_ext=None, to_num=None, date_from=None, date_to=None, fields=None):
        if date_from != None and date_to!=None and (to_ext!=None or to_num!=None):
            data = {'date_from':str(date_from),
                   'date_to':str(date_from)}
            if to_ext != None:
                tier = {'to':{'extenstion':to_ext}}
                data.update(tier)
            else:
                tier = {'to':{'number':to_num}}
                data.update(tier)
            if fields!=None:
                tier = {'fields':fields}
                data.update(tier)
            if request_id!=None:
                tier = {'request_id':request_id}
                data.update(tier)
            result = json.loads(self.request(data, '/stats/request'))
            data = {}
            if request_id!=None:
                tier = {'request_id':request_id}
                data.update(tier)
            try:
                if result['key']!=None:
                    tier = {'key':result['key']}
                    data.update(tier)
            except KeyError:
                return 'Error'
            finally:
                return self.request(data, '/stats/result')
        else:
            return 'Please specify params'
        
    def get_stats_call_party(self, request_id=None, call_party_ext=None, call_party_num=None, date_from=None, date_to=None, fields=None):
        if date_from != None and date_to!=None and (call_party_ext!=None or call_party_num!=None):
            data = {'date_from':str(date_from),
                   'date_to':str(date_from)}
            if call_party_ext != None:
                tier = {'call_party':{'extenstion':call_party_ext}}
                data.update(tier)
            else:
                tier = {'call_party':{'number':call_party_num}}
                data.update(tier)
            if fields!=None:
                tier = {'fields':fields}
                data.update(tier)
            if request_id!=None:
                tier = {'request_id':request_id}
                data.update(tier)
            print(data)
            result = json.loads(self.request(data, '/stats/request'))
            data = {}
            if request_id!=None:
                tier = {'request_id':request_id}
                data.update(tier)
            try:
                if result['key']!=None:
                    tier = {'key':result['key']}
                    data.update(tier)
            except KeyError:
                return 'Error'
            finally:
                print(data)
                return self.request(data, '/stats/result')
        else:
            return 'Please specify params'
