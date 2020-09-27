#!/usr/bin/env python
from requests import get, post
from hashlib import sha256
from json import dumps
import time


class MangoAPI:

    def __init__(self, key, salt, api_url='https://app.mango-office.ru/vpbx/'):
        self.url = api_url
        self.key = key
        self.salt = salt

    def hashing_func(self, data):
        return sha256(self.key.encode('utf-8') +
                      data.encode('utf-8') +
                      self.salt.encode('utf-8')).hexdigest()

    def request(self, data: dict, api_command: str):
        params = {
            'vpbx_api_key': self.key,
            'sign': self.hashing_func(dumps(data, separators=(',', ':'))),
            'json': dumps(data, separators=(',', ':'))
        }
        if api_command == 'stats/result':
            return post(
                (self.url + api_command),
                data=params,
                headers={'Content-type': 'application/x-www-form-urlencoded'}
            ).text
        elif api_command == 'queries/recording/post/':
            return post(
                (self.url + api_command),
                data=params,
                headers={'Content-type': 'application/x-www-form-urlencoded'}
            )
        else:
            return post(
                (self.url + api_command),
                data=params,
                headers={'Content-type': 'application/x-www-form-urlencoded'}
            ).json()

    def sms(self, from_ext: int, text: str, number: int, command_id="base", sender=None):
        return self.request({"command_id": command_id, "text": text,
                             "from_extension": from_ext, "to_number": number,
                             "sms_sender": sender}, 'commands/sms')

    def callback(self, command_id='base', from_ext=None, from_num=None, to_num=None, line=None, sip_head=None):
        return self.request({"command_id": command_id,
                             'from': {'extension': from_ext, 'number': from_num},
                             'to_number': to_num,
                             "line_number": line, "sip_headers": sip_head}, 'commands/callback')

    def group_callback(self, command_id=None, from_ext=None, to_num=None, line=None):
        return self.request({"command_id": command_id,
                             'from': from_ext, "to": to_num,
                             "line_number": line}, 'commands/callback_group')

    def hangup(self, command_id='base', call_id=None):
        return self.request({'command_id': command_id, 'call_id': call_id}, 'commands/call/hangup')

    def start_record(self, command_id='base', call_id=None, call_party_number=None):
        return self.request({'command_id': command_id,
                             'call_id': call_id, 'call_party_number': call_party_number}, 'commands/recording/start')

    def start_play(self, command_id='base', call_id=None, after_play_time=None, internal_id=None):
        return self.request({'command_id': command_id, 'call_id': call_id,
                             'after_play_time': after_play_time, 'internal_id': internal_id}, 'commands/play/start')

    def route(self, command_id='base', call_id=None, to_number=None, sip_headers=None):
        return self.request({'command_id': command_id, 'call_id': call_id, 'to_number': to_number,
                             'sip_headers': sip_headers}, 'commands/route')

    def transfer(self, command_id=None, call_id=None, to_number=None, initiator=None, method=None):
        return self.request({'command_id': command_id, 'call_id': call_id,
                             'method': method, 'to_number': to_number,
                             'initiator': initiator}, 'commands/transfer')

    def get_stats_from(self, request_id=None, from_ext=None, from_num=None, date_from=None, date_to=None, fields=None):
        if date_from and date_to and (from_ext or from_num):
            data = {
                'date_from': str(date_from),
                'date_to': str(date_from)
            }
            if from_ext:
                tier = {
                    'from':
                        {
                            'extenstion': from_ext
                        }
                }
                data.update(tier)
            else:
                tier = {
                    'from':
                        {
                            'number': from_num
                        }
                }
                data.update(tier)
            if fields:
                tier = {
                    'fields': fields
                }
                data.update(tier)
            if request_id:
                tier = {
                    'request_id': request_id
                }
                data.update(tier)
            result = self.request(data, 'stats/request').json()
            data = {}
            if request_id:
                tier = {
                    'request_id': request_id
                }
                data.update(tier)
            try:
                if result['key']:
                    tier = {
                        'key': result['key']
                    }
                    data.update(tier)
            except KeyError:
                return 'Error'
            finally:
                return self.request(data, 'stats/result')
        else:
            return 'Please specify params'

    def get_stats_to(self, request_id=None, to_ext=None, to_num=None, date_from=None, date_to=None, fields=None):
        if date_from and date_to and (to_ext or to_num):
            data = {
                'date_from': str(date_from),
                'date_to': str(date_from)
            }
            if to_ext:
                tier = {
                    'to':
                        {
                            'extenstion': to_ext
                        }
                }
                data.update(tier)
            else:
                tier = {
                    'to':
                        {
                            'number': to_num
                        }
                }
                data.update(tier)
            if fields:
                tier = {
                    'fields': fields
                }
                data.update(tier)
            if request_id:
                tier = {
                    'request_id': request_id
                }
                data.update(tier)
            result = self.request(data, 'stats/request')
            data = {}
            if request_id:
                tier = {
                    'request_id': request_id
                }
                data.update(tier)
            try:
                if result.get('key'):
                    tier = {
                        'key': result.get('key')
                    }
                    data.update(tier)
            except KeyError:
                return 'Error'
            finally:
                return self.request(data, 'stats/result')
        else:
            return 'Please specify params'

    def get_stats_call_party(self, request_id=None, call_party_ext=None, call_party_num=None, date_from=None,
                             date_to=None, fields=None):
        if date_from and date_to and (call_party_ext or call_party_num):
            data = {
                'date_from': str(date_from),
                'date_to': str(date_from)
            }
            if call_party_ext:
                tier = {
                    'call_party':
                        {
                            'extenstion': call_party_ext
                        }
                }
                data.update(tier)
            else:
                tier = {
                    'call_party':
                        {
                            'number': call_party_num
                        }
                }
                data.update(tier)
            if fields:
                tier = {
                    'fields': fields
                }
                data.update(tier)
            if request_id:
                tier = {
                    'request_id': request_id
                }
                data.update(tier)
            result = self.request(data, 'stats/request').json()
            data = {}
            if request_id:
                tier = {
                    'request_id': request_id
                }
                data.update(tier)
            try:
                if result['key']:
                    tier = {
                        'key': result['key']
                    }
                    data.update(tier)
            except KeyError:
                return 'Error'
            finally:
                return self.request(data, 'stats/result')
        else:
            return 'Please specify params'

    def dct_user_info(self, number=None):
        return self.request({"number": number}, 'queries/user_info_by_dct_number/')

    def dct_user_history(self, number=None):
        return self.request({"number": number}, 'queries/user_history_by_dct_number/')

    def user_list(self, extension=None, ext_fields=None):
        return self.request({'extension': extension, 'ext_fields': ext_fields}, 'config/users/request')

    def user_add(self, name=None, email=None, mobile=None, department=None, position=None, login=None, password=None,
                 use_status=None, use_cc_numbers=None, access_role_id=None, extension=None, line_id=None,
                 trunk_number_id=None, dial_alg=None, numbers=None):
        return self.request({
            'name': name,
            'email': email,
            'mobile': mobile,
            'department': department,
            'position': position,
            'login': login,
            'password': password,
            'use_status': use_status,
            'use_cc_numbers': use_cc_numbers,
            'access_role_id': access_role_id,
            'extension': extension,
            'line_id': line_id,
            'trunk_number_id': trunk_number_id,
            'dial_alg': dial_alg,
            'numbers': numbers
        },
            'member/create')

    def user_upd(self, user_id=None, name=None, email=None, mobile=None, department=None, position=None, login=None,
                 password=None, use_status=None, use_cc_numbers=None, access_role_id=None, extension=None, line_id=None,
                 trunk_number_id=None, dial_alg=None, numbers=None):
        return self.request({
            'user_id': user_id,
            'name': name,
            'email': email,
            'mobile': mobile,
            'department': department,
            'position': position,
            'login': login,
            'password': password,
            'use_status': use_status,
            'use_cc_numbers': use_cc_numbers,
            'access_role_id': access_role_id,
            'extension': extension,
            'line_id': line_id,
            'trunk_number_id': trunk_number_id,
            'dial_alg': dial_alg,
            'numbers': numbers
        },
            'member/update')

    def user_del(self, user_id):
        return self.request({'user_id': user_id}, 'member/delete')

    def group_list(self, group_id=None, operator_id=None, operator_extension=None, show_users=1):
        return self.request({
            'show_users': show_users,
            'group_id': group_id,
            'operator_id': operator_id,
            'operator_extension': operator_extension
        }, 'groups')

    def group_add(self, name=None, description=None, extension=None, dial_alg_group=None, dial_alg_users=None,
                  auto_redirect=None, auto_dial=None, line_id=None, use_dynamic_ivr=None, use_dynamic_seq_num=None,
                  melody_id=None, operators=None):
        return self.request({
            'name': name,
            'description': description,
            'extension': extension,
            'dial_alg_group': dial_alg_group,
            'dial_alg_users': dial_alg_users,
            'auto_redirect': auto_redirect,
            'auto_dial': auto_dial,
            'line_id': line_id,
            'use_dynamic_ivr': use_dynamic_ivr,
            'use_dynamic_seq_num': use_dynamic_seq_num,
            'melody_id': melody_id,
            'operators': operators},
            'group/create')

    def group_upd(self, group_id=None, name=None, description=None, extension=None, dial_alg_group=None,
                  dial_alg_users=None, auto_redirect=None, auto_dial=None,
                  line_id=None, use_dynamic_ivr=None, use_dynamic_seq_num=None, melody_id=None, operators=None):
        return self.request({
            'group_id': group_id,
            'group': {
                'name': name,
                'description': description,
                'extension': extension,
                'dial_alg_group': dial_alg_group,
                'dial_alg_users': dial_alg_users,
                'auto_redirect': auto_redirect,
                'auto_dial': auto_dial,
                'line_id': line_id,
                'use_dynamic_ivr': use_dynamic_ivr,
                'use_dynamic_seq_num': use_dynamic_seq_num,
                'melody_id': melody_id,
                'operators': operators
            }
        },
            'group/update')

    def group_del(self, group_id):
        return self.request({'group_id': group_id}, 'group/delete')

    def balance(self):
        return self.request({}, 'account/balance')

    def lines(self):
        return self.request({}, 'incominglines')

    def audio(self):
        return self.request({}, 'audiofiles')

    def schemas(self, ext_fields: bool):
        if ext_fields:
            return self.request({
                'ext_fields': [
                    'trunks_numbers'
                ]
            }, 'schemas/')
        else:
            return self.request({}, 'schemas/')

    def set_schema(self, line=None, trunk=None, schema=None):
        return self.request({
            'schema_id': schema,
            'line_id': line,
            'trunk_number_id': trunk
        }, 'schema/set/')

    def roles(self):
        return self.request({}, 'roles')

    def sips_list(self):
        return self.request({}, 'sips')

    def sip_add(self, user_id=None, password=None, login=None, domain=None, description=None):
        return self.request({'user_id': user_id, 'login': login, 'password': password,
                             'domain': domain, 'description': description}, 'sip/create')

    def sip_edit(self, sip_id=None, user_id=None, password=None, login=None, domain=None, description=None):
        return self.request({'sip_id': sip_id, 'user_id': user_id,
                             'login': login, 'domain': domain, 'password': password,
                             'description': description}, 'sip/update')

    def domains_list(self):
        return self.request({}, 'domains')

    def trunk_num_list(self):
        return self.request({}, 'trunks/numbers')

    def bwlist_state(self):
        return self.request({}, 'bwlists/state/')

    def bwlist_nums(self):
        return self.request({}, 'bwlists/numbers/')

    def bwlist_add(self, number=None, list_type='black', num_type='tel', comment='API'):
        return self.request({'number': number, 'number_type': num_type,
                             'list_type': list_type, 'comment': comment}, 'bwlists/number/add/')

    def bwlist_del(self, num_id=None):
        return self.request({'number_id': num_id}, 'bwlists/number/delete/')

    def campaign_info(self, campaign_id=None):
        return self.request({'campaign_id': campaign_id}, 'campaign')

    def camp_task_info(self, task_id=None):
        return self.request({'task_id': task_id}, 'task')

    def campaign_add(self, name=None, line_id=None, created_by=None,
                     priority=None, start_date=None, end_date=None,
                     schedule=None, operators=None, dial_mode=None,
                     voice_message_id=None, hold_message_id=None, max_redial_count_if_busy=None,
                     max_redial_count_if_no_answ=None, max_redial_count_if_number_not_avail=None,
                     max_wait_time=None, additional_calls_coefficient=None, wait_time_if_busy=None,
                     wait_time_if_no_answ=None, wait_time_if_number_not_avail=None,
                     after_call_processing=None):
        return self.request({
            'name': name,
            'line_id': line_id,
            'created_by': created_by,
            'priority': priority,
            'start_date': start_date,
            'end_date': end_date,
            'schedule': schedule,
            'operators': operators,
            'dial_mode': dial_mode,
            'voice_message_id': voice_message_id,
            'hold_message_id': hold_message_id,
            'max_redial_count_if_busy': max_redial_count_if_busy,
            'max_redial_count_if_no_answ': max_redial_count_if_no_answ,
            'max_redial_count_if_number_not_avail': max_redial_count_if_number_not_avail,
            'max_wait_time': max_wait_time,
            'additional_calls_coefficient': additional_calls_coefficient,
            'wait_time_if_busy': wait_time_if_busy,
            'wait_time_if_no_answ': wait_time_if_no_answ,
            'wait_time_if_number_not_avail': wait_time_if_number_not_avail,
            'after_call_processing': after_call_processing},
            'campaign/add')

    def camp_task_add(self, campaign_id: int, tasks: dict):
        return self.request({'campaign_id': str(campaign_id), 'tasks': tasks}, 'tasks/push')

    def campaign_start(self, campaign_id: int):
        return self.request({'campaign_id': campaign_id}, 'campaign/start')

    def campaign_stop(self, campaign_id: int):
        return self.request({'campaign_id': campaign_id}, 'campaign/stop')

    def campaign_del(self, campaign_id: int):
        return self.request({'campaign_id': campaign_id}, 'campaign/delete')

    def record_meth_get(self, record_id):
        times = str(int(time.time()) + 10800)
        sha = sha256(self.key.encode('utf-8') + times.encode('utf-8')
                     + record_id.encode('utf-8') + self.salt.encode('utf-8')).hexdigest()
        return get(f"{self.url}queries/recording/link/{record_id}/download/{self.key}/{times}/{sha}").url

    def record_meth_post(self, record_id, action):
        return self.request({'recording_id': record_id, 'action': action}, 'queries/recording/post/')

    def speech2text(self, record_id: str, with_terms: bool, with_names: bool):
        return self.request({'recording_id': f'[\"{record_id}\"]',
                             'with_terms': with_terms, 'with_names': with_names}, 'queries/recording_categories/')
