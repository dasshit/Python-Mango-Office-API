#!/usr/bin/env python
import requests
import hashlib
import json
import time


def hashing_func(data, self):
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
        if self.url is None:
            self.url = 'https://app.mango-office.ru/vpbx/'
        else:
            self.url = self.url
        if data is None:
            data = {}
        else:
            data = data
        if api_command is None:
            return 'Undefined method'
        else:
            stringified = stringify(data)
            params = {
                'vpbx_api_key': self.key,
                'sign': hashing_func(stringified, self),
                'json': stringified
            }
            headers = {
                'Content-type': 'application/x-www-form-urlencoded'
            }
            if api_command == 'stats/result':
                return requests.post(
                    (self.url + api_command),
                    data=params,
                    headers=headers
                ).text
            elif api_command == 'queries/recording/post/':
                return requests.post(
                    (self.url + api_command),
                    data=params,
                    headers=headers
                )
            else:
                return json.loads(requests.post(
                    (self.url + api_command),
                    data=params,
                    headers=headers
                ).text)

    def sms(self, command_id=None, from_ext=None, text='Test', number=None, sender=None):
        if number is None:
            return 'Please, specify number'
        elif from_ext is None:
            return 'Please, specify user extension'
        else:
            data = {
                "text": text,
                "from_extension": from_ext,
                "to_number": number
            }
            if command_id:
                tier = {
                    "command_id": command_id
                }
                data.update(tier)
            else:
                tier = {
                    "command_id": "base"
                }
                data.update(tier)
            if sender:
                tier = {
                    "sms_sender": sender
                }
                data.update(tier)
            return self.request(data, 'commands/sms')

    def callback(self, command_id=None, from_ext=None, from_num=None, to_num=None, line=None, sip_head=None):
        if from_ext is None:
            return "Please, specify user extension"
        elif to_num is None:
            return "Please, specify calling number"
        else:
            data = {}
            if command_id:
                tier = {
                    "command_id": command_id
                }
                data.update(tier)
            else:
                tier = {
                    "command_id": 'base'
                }
                data.update(tier)
            if from_ext and from_num:
                tier = {
                    'from':
                        {
                            'extension': from_ext,
                            'number': from_num
                        },
                    'to_number': to_num
                }
                data.update(tier)
            else:
                tier = {
                    'from':
                        {
                            'extension': from_ext
                        },
                    'to_number': to_num
                }
                data.update(tier)
        if line:
            tier = {
                "line_number": line
            }
            data.update(tier)
        if sip_head:
            tier = {
                "sip_headers": sip_head
            }
            data.update(tier)
        return self.request(data, 'commands/callback')

    def group_callback(self, command_id=None, from_ext=None, to_num=None, line=None):
        if from_ext is None:
            return "Please, specify user extension"
        elif to_num is None:
            return "Please, specify calling number"
        else:
            data = {}
            if command_id:
                tier = {
                    "command_id": command_id
                }
                data.update(tier)
            else:
                tier = {
                    "command_id": 'base'
                }
                data.update(tier)
                tier = {
                    'from': from_ext,
                    "to": to_num
                }
                data.update(tier)
        if line:
            tier = {
                "line_number": line
            }
            data.update(tier)
        return self.request(data, 'commands/callback_group')

    def hangup(self, command_id=None, call_id=None):
        if command_id is None:
            command_id = 'base'
        if call_id is None:
            return 'Please specify call_id'
        else:
            data = {
                'command_id': command_id,
                'call_id': call_id
            }
            return self.request(data, 'commands/call/hangup')

    def start_record(self, command_id=None, call_id=None, call_party_number=None):
        if command_id is None:
            command_id = 'base'
        if call_id is None:
            return 'Please specify call_id'
        else:
            data = {
                'command_id': command_id,
                'call_id': call_id
            }
            if call_party_number:
                tier = {
                    'call_party_number': call_party_number
                }
                data.update(tier)
            else:
                return 'Please specify call_party_number'
            return self.request(data, 'commands/recording/start')

    def start_play(self, command_id=None, call_id=None, after_play_time=None, internal_id=None):
        if command_id is None:
            command_id = 'base'
        if call_id is None:
            return 'Please specify call_id'
        else:
            data = {
                'command_id': command_id,
                'call_id': call_id
            }
            if after_play_time:
                tier = {
                    'after_play_time': after_play_time
                }
                data.update(tier)
            if internal_id:
                tier = {
                    'internal_id': internal_id
                }
                data.update(tier)
            return self.request(data, 'commands/play/start')

    def route(self, command_id=None, call_id=None, to_number=None, sip_headers=None):
        if command_id is None:
            command_id = 'base'
        if call_id is None:
            return 'Please specify call_id'
        if to_number is None:
            return 'Please specify number transfer to'
        else:
            data = {
                'command_id': command_id,
                'call_id': call_id
            }
            if to_number is None:
                return 'Please specify number to route'
            else:
                tier = {
                    'to_number': to_number
                }
                data.update(tier)
                if sip_headers:
                    tier = {
                        'sip_headers': sip_headers
                    }
                    data.update(tier)
                return self.request(data, 'commands/route')

    def transfer(self, command_id=None, call_id=None, to_number=None, initiator=None, method=None):
        if command_id is None:
            command_id = 'base'
        if call_id is None:
            return 'Please specify call_id'
        if method is None:
            return 'Please specify transfer method'
        if to_number is None:
            return 'Please specify number transfer to'
        if initiator is None:
            return 'Please specify initiator'
        else:
            data = {
                'command_id': command_id,
                'call_id': call_id,
                'method': method,
                'to_number': to_number,
                'initiator': initiator
            }
            if initiator:
                tier = {'initiator': initiator}
                data.update(tier)
            return self.request(data, 'commands/transfer')

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
            result = json.loads(self.request(data, 'stats/request'))
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
            result = json.loads(self.request(data, 'stats/request'))
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
        if number:
            if isinstance(number, str):
                return self.request({
                    "number": number
                }, 'queries/user_info_by_dct_number/')
            else:
                return 'Wrong info type'
        else:
            return 'Please specify number'

    def dct_user_history(self, number=None):
        if number:
            if isinstance(number, str):
                return self.request({
                    "number": number
                }, 'queries/user_history_by_dct_number/')
            else:
                return 'Wrong info type'
        else:
            return 'Please specify number'

    def user_list(self, ext_fields=None, extension=None):
        data = {}
        if ext_fields:
            tier = {
                'ext_fields': ext_fields
            }
            data.update(tier)
        if extension:
            tier = {
                'extension': extension
            }
            data.update(tier)
        return self.request(data, 'config/users/request')

    def user_add(self, name=None, email=None, mobile=None,
                 department=None, position=None,
                 login=None, password=None,
                 use_status=None, use_cc_numbers=None,
                 access_role_id=None, extension=None,
                 line_id=None, trunk_number_id=None,
                 dial_alg=None, numbers=None):
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

    def user_upd(self, user_id=None, name=None,
                 email=None, mobile=None, department=None,
                 position=None, login=None,
                 password=None, use_status=None, use_cc_numbers=None,
                 access_role_id=None, extension=None, line_id=None,
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
        data = {
            'show_users': show_users
        }
        if group_id is None and operator_id is None and operator_extension is None:
            return self.request(data, 'groups')
        else:
            if group_id:
                tier = {
                    'group_id': group_id
                }
                data.update(tier)
            else:
                if operator_id:
                    tier = {
                        'operator_id': operator_id
                    }
                    data.update(tier)
                else:
                    if operator_extension:
                        tier = {
                            'operator_extension': operator_extension
                        }
                        data.update(tier)
        return self.request(data, 'groups')

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

    def schemas(self, ext_fields=0):
        if ext_fields != 0:
            return self.request({
                'ext_fields': [
                    'trunks_numbers'
                ]
            }, 'schemas/')
        else:
            return self.request({}, 'schemas/')

    def set_schema(self, line=None, trunk=None, schema=None):
        if schema and (line or schema):
            data = {
                'schema_id': schema
            }
            if line:
                tier = {
                    'line_id': line
                }
                data.update(tier)
            elif trunk:
                tier = {
                    'trunk_number_id': trunk
                }
                data.update(tier)
        else:
            return 'Specify params'
        return self.request(data, 'schema/set/')

    def roles(self):
        return self.request({}, 'roles')

    def sips_list(self):
        return self.request({}, 'sips')

    def sip_add(self, user_id=None, password=None, login=None, domain=None, description=None):
        if user_id and password:
            data = {
                'user_id': user_id,
                'password': password
            }
            if login and domain:
                tier = {
                    'login': login,
                    'domain': domain
                }
                data.update(tier)
            if description:
                tier = {
                    'description': description
                }
                data.update(tier)
            return self.request(data, 'sip/create')
        else:
            return 'Specify params'

    def sip_edit(self, sip_id=None, user_id=None, password=None, login=None, domain=None, description=None):
        if sip_id:
            if user_id and password:
                data = {
                    'sip_id': sip_id,
                    'user_id': user_id,
                    'password': password
                }
                if login and domain:
                    tier = {
                        'login': login,
                        'domain': domain
                    }
                    data.update(tier)
                if description:
                    tier = {
                        'description': description
                    }
                    data.update(tier)
                return self.request(data, 'sip/update')
        else:
            return 'Specify params'

    def domains_list(self):
        return self.request({}, 'domains')

    def trunk_num_list(self):
        return self.request({}, 'trunks/numbers')

    def bwlist_state(self):
        return self.request({}, 'bwlists/state/')

    def bwlist_nums(self):
        return self.request({}, 'bwlists/numbers/')

    def bwlist_add(self, number=None, list_type='black', num_type='tel', comment='API'):
        if number:
            return self.request({
                'number': number,
                'list_type': list_type,
                'number_type': num_type,
                'comment': comment
            }, 'bwlists/number/add/')
        else:
            return 'Specify number'

    def bwlist_del(self, num_id=None):
        if num_id:
            return self.request({
                'number_id': num_id
            }, 'bwlists/number/delete/')
        else:
            return 'Specify number'

    def campaign_info(self, campaign_id=None):
        if campaign_id:
            return self.request({
                'campaign_id': campaign_id
            },
                'campaign')
        else:
            return 'Specify campaign id'

    def camp_task_info(self, task_id=None):
        return self.request({
            'task_id': task_id
        },
            'task')

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

    def camp_task_add(self, campaign_id=None, tasks=None):
        return self.request({
            'campaign_id': str(campaign_id),
            'tasks': tasks
        },
            'tasks/push')

    def campaign_start(self, campaign_id=None):
        if campaign_id:
            return self.request({
                'campaign_id': campaign_id
            },
                'campaign/start')
        else:
            return 'Specify campaign id'

    def campaign_stop(self, campaign_id=None):
        if campaign_id:
            return self.request({
                'campaign_id': campaign_id
            },
                'campaign/stop')
        else:
            return 'Specify campaign id'

    def campaign_del(self, campaign_id=None):
        if campaign_id:
            return self.request({
                'campaign_id': campaign_id
            },
                'campaign/delete')
        else:
            return 'Specify campaign id'

    def record_meth_get(self, record_id):
        timestamp = str(int(time.time()) + 10800)
        url = self.url + 'queries/recording/link/' + record_id + '/download/' + self.key + '/' + str(
            timestamp) + '/' + hashlib.sha256(self.key.encode('utf-8') +
                                              timestamp.encode('utf-8') +
                                              record_id.encode('utf-8') +
                                              self.salt.encode('utf-8')).hexdigest()
        result = requests.get(url)
        return result.url

    def record_meth_post(self, record_id):
        return self.request({
            'recording_id': record_id,
            'action': 'download'
        },
            'queries/recording/post/')

    def speech2text(self, record_id=None, with_terms=None, with_names=None):
        if record_id:
            result = '[\"' + record_id + '\"]'
            data = {
                "recording_id": result
            }
            if with_terms:
                tier = {
                    'with_terms': True
                }
                data.update(tier)
            if with_names:
                tier = {
                    'with_names': True
                }
                data.update(tier)
            return self.request(data, 'queries/recording_categories/')
        else:
            return 'Specify params'
