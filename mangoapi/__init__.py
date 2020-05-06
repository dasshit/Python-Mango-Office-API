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
            if api_command == 'stats/result':
                return requests.post((self.url + api_command),
                                        data=params,
                                        headers=headers).text
            elif api_command == 'queries/recording/post/':
                return requests.post((self.url + api_command),
                                        data=params,
                                        headers=headers)
            else:
                print(self.url + api_command)
                return json.loads(requests.post((self.url + api_command),
                                        data=params,
                                        headers=headers).text)
            
            
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
            return self.request(data, 'commands/sms')
    
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
        return self.request(data, 'commands/callback')
            
                
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
        return self.request(data, 'commands/callback_group')
    
    def hangup(self, command_id=None, call_id=None):
        if command_id == None:
            command_id = 'base'
        if call_id == None:
            return 'Please specify call_id'
        else:
            data = {'command_id':command_id, 'call_id':call_id}
            return self.request(data, 'commands/call/hangup')
        
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
            return self.request(data, 'commands/recording/start')
    
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
            return self.request(data, 'commands/play/start')
        
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
                return self.request(data, 'commands/route')
            
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
            return self.request(data, 'commands/transfer')
        
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
            result = json.loads(self.request(data, 'stats/request'))
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
                return self.request(data, 'stats/result')
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
            result = self.request(data, 'stats/request')
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
                return self.request(data, 'stats/result')
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
            result = json.loads(self.request(data, 'stats/request'))
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
                return self.request(data, 'stats/result')
        else:
            return 'Please specify params'
        
    def dct_user_info(self, number=None):
        if number!=None:
            if type(number) == type('str'):
                data = {"number": number}
            else:
                return 'Wrong info type'
            return self.request(data, 'queries/user_info_by_dct_number/')
        else:
            return 'Please specify number'
        
    def dct_user_history(self, number=None):
        if number!=None:
            if type(number) == type('str'):
                data = {"number": number}
            else:
                return 'Wrong info type'
            return self.request(data, 'queries/user_history_by_dct_number/')
        else:
            return 'Please specify number'
    
    def user_list(self, ext_fields=None, extension=None):
        data = {}
        if ext_fields != None:
            tier = {'ext_fields':ext_fields}
            data.update(tier)
        if extension!=None:
            tier = {'extension':extension}
            data.update(tier)
        return self.request(data, 'config/users/request')
    
    def user_add(self, name=None, email=None, mobile=None, department=None, position=None, login=None, password=None, use_status=None, use_cc_numbers=None,
                access_role_id=None, extension=None, line_id=None, trunk_number_id=None, dial_alg=None, numbers=None):
        data = {'name':name, 'email':email, 'mobile':mobile, 'department':department, 'position':position, 'login':login, 'password':password,
               'use_status':use_status, 'use_cc_numbers':use_cc_numbers, 'access_role_id':access_role_id, 'extension':extension,
               'line_id':line_id, 'trunk_number_id':trunk_number_id, 'dial_alg':dial_alg, 'numbers':numbers}
        return self.request(data, 'member/create')
    
    def user_upd(self, user_id=None, name=None, email=None, mobile=None, department=None, position=None, login=None, password=None, use_status=None, use_cc_numbers=None,
                access_role_id=None, extension=None, line_id=None, trunk_number_id=None, dial_alg=None, numbers=None):
        data = {'user_id':user_id, 'name':name, 'email':email, 'mobile':mobile, 'department':department, 'position':position, 'login':login, 'password':password,
               'use_status':use_status, 'use_cc_numbers':use_cc_numbers, 'access_role_id':access_role_id, 'extension':extension,
               'line_id':line_id, 'trunk_number_id':trunk_number_id, 'dial_alg':dial_alg, 'numbers':numbers}
        return self.request(data, 'member/update')
    
    
    def user_del(self, user_id):
        data = {'user_id':user_id}
        return self.request(data, 'member/delete')
        
    def group_list(self, group_id=None, operator_id=None, operator_extension=None, show_users=1):
        data = {'show_users':show_users}
        if group_id==None and operator_id==None and operator_extension==None:
            return self.request(data, 'groups')
        else:
            if group_id!=None:
                tier = {'group_id':group_id}
                data.update(tier)
            else:
                if operator_id!=None:
                    tier = {'operator_id':operator_id}
                    data.update(tier)
                else:
                    if operator_extension!=None:
                        tier = {'operator_extension':operator_extension}
                        data.update(tier)
        return self.request(data, 'groups')
    
    def group_add(self, name=None, description=None, extension=None, dial_alg_group=None, dial_alg_users=None, auto_redirect=None, auto_dial=None,
                 line_id=None, use_dynamic_ivr=None, use_dynamic_seq_num=None, melody_id=None, operators=None):
        data = {'name':name, 'description':description, 'extension':extension, 'dial_alg_group':dial_alg_group, 'dial_alg_users':dial_alg_users, 'auto_redirect':auto_redirect, 
               'auto_dial':auto_dial, 'line_id':line_id, 'use_dynamic_ivr':use_dynamic_ivr, 'use_dynamic_seq_num':use_dynamic_seq_num,'melody_id':melody_id, 'operators':operators}
        return self.request(data, 'group/create')
    
    def group_upd(self, group_id=None, name=None, description=None, extension=None, dial_alg_group=None, dial_alg_users=None, auto_redirect=None, auto_dial=None,
                 line_id=None, use_dynamic_ivr=None, use_dynamic_seq_num=None, melody_id=None, operators=None):
        data = {'name':name, 'description':description, 'extension':extension, 'dial_alg_group':dial_alg_group, 'dial_alg_users':dial_alg_users, 'auto_redirect':auto_redirect, 
               'auto_dial':auto_dial, 'line_id':line_id, 'use_dynamic_ivr':use_dynamic_ivr, 'use_dynamic_seq_num':use_dynamic_seq_num,'melody_id':melody_id, 'operators':operators}
        return self.request(data, 'group/update')
    
    def group_del(self, group_id):
        data = {'group_id':group_id}
        return self.request(data, 'group/delete')
    
    def balance(self):
        data = {}
        return self.request(data, 'account/balance')
    
    def lines(self):
        data = {}
        return self.request(data, 'incominglines')
    
    
    def audio(self):
        data = {}
        return self.request(data, 'audiofiles')
    
    def schemas(self, ext_fields=0):
        if ext_fields!=0:
            data = {'ext_fields':['trunks_numbers']}
        else:
            data = {}
        return self.request(data, 'schemas/')
    
    def set_schema(self, line=None, trunk=None, schema=None):
        if schema !=None and (line != None or schema != None):
            data = {'schema_id':schema}
            if line != None:
                tier = {'line_id':line}
                data.update(tier)
            elif trunk != None:
                tier = {'trunk_number_id':trunk}
                data.update(tier)
        else:
            return 'Specify params'
        return self.request(data, 'schema/set/')
            
        
    def roles(self):
        data = {}
        return self.request(data, 'roles')
    
    def sips_list(self):
        data = {}
        return self.request(data, 'sips')
    
    def sip_add(self, user_id=None, password=None, login=None, domain=None, description=None):
        if user_id!=None and password!=None:
            data = {'user_id':user_id, 'password':password}
            if login!=None and domain!=None:
                tier = {'login':login, 'domain':domain}
                data.update(tier)
            if description!=None:
                tier = {'description':description}
                data.update(tier)
            return self.request(data, 'sip/create')
        else:
            return 'Specify params'
    
    def sip_edit(self, sip_id=None, user_id=None, password=None, login=None, domain=None, description=None):
        if sip_id!=None:
            if user_id!=None and password!=None:
                data = {'sip_id':sip_id,'user_id':user_id, 'password':password}
                if login!=None and domain!=None:
                    tier = {'login':login, 'domain':domain}
                    data.update(tier)
                if description!=None:
                    tier = {'description':description}
                    data.update(tier)
                return self.request(data, 'sip/update')
        else:
            return 'Specify params'
    
    def domains_list(self):
        data = {}
        return self.request(data, 'domains')
    
    def trunk_num_list(self):
        data = {}
        return self.request(data, 'trunks/numbers')
    
    def bwlist_state(self):
        data = {}
        return self.request(data, 'bwlists/state/')
    
    def bwlist_nums(self):
        data = {}
        return self.request(data, 'bwlists/numbers/')
    def bwlist_add(self, number=None, list_type='black', num_type='tel', comment='API'):
        if number != None:
            data = {'number':number,'list_type':list_type, 'number_type':num_type, 'comment':comment}
            return self.request(data, 'bwlists/number/add/')
        else:
            return 'Specify number'

    def bwlist_del(self, num_id=None):
        if num_id != None:
            data = {'number_id':num_id}
            return self.request(data, 'bwlists/number/delete/')
        else:
            return 'Specify number'
    
    def campaign_info(self, campaign_id=None):
        if campaign_id!=None:
            data = {'campaign_id':campaign_id}
            return self.request(data, 'campaign')
        else:
            return 'Specify campaign id'
        
        
    def camp_task_info(self, task_id=None):
        data = {'task_id':task_id}
        return self.request(data, 'task')
    
    def camp_task_add(self, campaign_id=None, tasks=None):
        data = {'tasks':tasks}
        return self.request(data, 'tasks/push')
    
    def campaign_start(self, campaign_id=None):
        if campaign_id!=None:
            data = {'campaign_id':campaign_id}
            return self.request(data, 'campaign/start')
        else:
            return 'Specify campaign id'
        
    def campaign_stop(self, campaign_id=None):
        if campaign_id!=None:
            data = {'campaign_id':campaign_id}
            return self.request(data, 'campaign/stop')
        else:
            return 'Specify campaign id'
        
    def campaign_del(self, campaign_id=None):
        if campaign_id!=None:
            data = {'campaign_id':campaign_id}
            return self.request(data, 'campaign/delete')
        else:
            return 'Specify campaign id'
    
    def record_meth_get(self, record_id):
        timestamp = str(int(time.time()) + 10800)
        sign = hash2(record_id, timestamp, self.key, self.salt)
        url = self.url + 'queries/recording/link/' + record_id + '/download/' + self.key + '/' + str(timestamp) + '/' + hashlib.sha256(self.key.encode('utf-8') +
                            timestamp.encode('utf-8') +
                            record_id.encode('utf-8') +
                            self.salt.encode('utf-8')).hexdigest()
        result = requests.get(url)
        return result.url
    
    def record_meth_post(self, record_id):
        data = {'recording_id':record_id, 'action':'download'}
        return self.request(data, 'queries/recording/post/').url
    
    def speech2text(self, record_id=None, with_terms=None, with_names=None):
        if record_id != None:
            result = '[\"' + record_id + '\"]'
            data = {"recording_id":result}
            if with_terms!=None:
                tier = {'with_terms':True}
                data.update(tier)
            if with_names!=None:
                tier = {'with_names':True}
                data.update(tier)       
            print(data)
            return self.request(data, 'queries/recording_categories/')
        else:
            return 'Specify params'
