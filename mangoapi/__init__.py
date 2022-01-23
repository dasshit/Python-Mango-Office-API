#!/usr/bin/env python
import time
from hashlib import sha256
from json import dumps, loads
from requests import get, post
from typing import List, Dict


def stringify(data):
    return dumps(data, separators=(',', ':'))


class MangoAPI:

    __slots__ = ['url', 'key', 'salt', 'logger', 'headers']
    
    def __init__(self, api_url, key, salt, logger=None, headers={'Content-type': 'application/x-www-form-urlencoded'}):
        self.url = api_url
        self.key = key
        self.salt = salt
        self.logger = logger
        self.headers = headers
        if self.url:  # strip vpbx
            pos = self.url.find('vpbx')
            if pos > 0:
                self.url = self.url[0: pos]

    def hash(self, data):
        return sha256(self.key.encode('utf-8') +
                      data.encode('utf-8') +
                      self.salt.encode('utf-8')).hexdigest()

    def request(self, data=None, api_command=None):
        if self.url is None:
            self.url = 'https://app.mango-office.ru/'
        else:
            self.url = self.url
        if api_command is None:
            raise ValueError('Undefined method')
        else:
            stringified = stringify(data)
            params = {'vpbx_api_key': self.key,
                      'sign': self.hash(stringified),
                      'json': stringified}
            if self.logger is not None:
                self.logger.info({"url": self.url + api_command, "headers": self.headers, "data": params})
            result = post((self.url + api_command), data=params, headers=self.headers)
            if self.logger is not None:
                self.logger.info({"data": result.request.body})

            if self.logger is not None and result.status_code not in [401, 404]:
                self.logger.error({'status': result.status_code, 'headers': result.headers, 'response': result.text})
            elif self.logger is not None:
                self.logger.error({'status': result.status_code, 'headers': result.headers, 'response': result.text})
                self.logger.error({"details": "For details you can contact techsupport, "
                                              "please write this log in your request, http-request-id",
                                   "X-Uuid": result.headers.get('X-Uuid')})
            if not result.ok:
                raise result.raise_for_status()
            if api_command in ['stats/result', 'stats/request', 'queries/recording/post/']:
                return result
            else:
                return result.json()

    def sms(self, command_id="base", from_ext=None, text='Test', number=None, sender=None):
        if number is None:
            raise ValueError('Please, specify number')
        if from_ext is None:
            raise ValueError('Please, specify user extension')
        else:
            data = {
                "command_id": command_id,
                "text": text,
                "from_extension": from_ext,
                "to_number": number
            }
            if sender is not None:
                data.update({"sms_sender": sender})
            return self.request(data, 'vpbx/commands/sms')

    def callback(self, command_id="base", from_ext=None, from_num=None, to_num=None, line=None, sip_head=None):
        if from_ext is None:
            raise ValueError("Please, specify user extension")
        if to_num is None:
            raise ValueError("Please, specify calling number")
        else:
            data = {"command_id": command_id}
            if from_ext is not None and from_num is not None:
                data.update({'from': {'extension': from_ext, 'number': from_num}, "to_number": to_num})
            else:
                data.update({'from': {'extension': from_ext}, "to_number": to_num})
            if line is not None:
                data.update({"line_number": line})
            if sip_head is not None:
                data.update({"sip_headers": sip_head})
            return self.request(data, 'vpbx/commands/callback')

    def group_callback(self, command_id="base", from_ext=None, to_num=None, line=None):
        if from_ext is None:
            raise ValueError("Please, specify user extension")
        if to_num is None:
            raise ValueError("Please, specify calling number")
        else:
            data = {
                "command_id": command_id,
                "from": from_ext,
                "to": to_num
            }
            if line is not None:
                data.update({"line_number": line})
            return self.request(data, 'vpbx/commands/callback_group')

    def hangup(self, command_id="base", call_id=None):
        if call_id is None:
            raise ValueError('Please specify call_id')
        else:
            return self.request({'command_id': command_id, 'call_id': call_id}, 'commands/call/hangup')

    def start_record(self, command_id="base", call_id=None, call_party_number=None):
        if call_id is None:
            raise ValueError('Please specify call_id')
        else:
            if call_party_number is not None:
                return self.request(
                    {'command_id': command_id, 'call_id': call_id, 'call_party_number': call_party_number},
                    'commands/recording/start')
            else:
                raise ValueError('Please specify call_party_number')

    def start_play(self, command_id="base", call_id=None, after_play_time=None, internal_id=None):
        if call_id is None:
            raise ValueError('Please specify call_id')
        else:
            data = {'command_id': command_id, 'call_id': call_id}
            if after_play_time is not None:
                data.update({'after_play_time': after_play_time})
            if internal_id is not None:
                data.update({'internal_id': internal_id})
            return self.request(data, 'vpbx/commands/play/start')

    def route(self, command_id="base", call_id=None, to_number=None, sip_headers=None):
        if call_id is None:
            raise ValueError('Please specify call_id')
        if to_number is None:
            raise ValueError('Please specify number transfer to')
        else:
            if to_number is None:
                raise ValueError('Please specify number to route')
            else:
                data = {'command_id': command_id, 'call_id': call_id, 'to_number': to_number}
                if sip_headers is not None:
                    data.update({'sip_headers': sip_headers})
                return self.request(data, 'vpbx/commands/route')

    def transfer(self, command_id=None, call_id=None, to_number=None, initiator=None, method=None):
        if command_id is None:
            command_id = 'base'
        if call_id is None:
            raise ValueError('Please specify call_id')
        if method is None:
            raise ValueError('Please specify transfer method')
        if to_number is None:
            raise ValueError('Please specify number transfer to')
        if initiator is None:
            raise ValueError('Please specify initiator')
        else:
            data = {'command_id': command_id, 'call_id': call_id, 'method': method, 'to_number': to_number,
                    'initiator': initiator}
            if initiator is not None:
                tier = {'initiator': initiator}
                data.update(tier)
            return self.request(data, 'vpbx/commands/transfer')

    def get_stats_from(self, request_id=None, from_ext=None, from_num=None, date_from=None, date_to=None, fields=None):
        if date_from is not None and date_to is not None and (from_ext is not None or from_num is not None):
            data = {'date_from': str(date_from),
                    'date_to': str(date_to)}
            if from_ext is not None:
                data.update({'from': {'extenstion': from_ext}})
            else:
                data.update({'from': {'number': from_num}})
            if fields is not None:
                data.update({'fields': fields})
            if request_id is not None:
                data.update({'request_id': request_id})
            result = self.request(data, 'vpbx/stats/request')
            if result.status_code == 401:
                return result.json()
            data = {}
            result = result.json()
            if request_id is not None:
                data.update({'request_id': request_id})
            try:
                if result['key'] is not None:
                    data.update({'key': result['key']})
            except KeyError as error:
                raise KeyError(error)
            return self.request(data, 'vpbx/stats/result')
        else:
            raise ValueError('Please specify params')

    def get_stats_to(self, request_id=None, to_ext=None, to_num=None, date_from=None, date_to=None, fields=None):
        if date_from is not None and date_to is not None and (to_ext is not None or to_num is not None):
            data = {'date_from': str(date_from),
                    'date_to': str(date_to)}
            if to_ext is not None:
                data.update({'to': {'extenstion': to_ext}})
            else:
                data.update({'to': {'number': to_num}})
            if fields is not None:
                data.update({'fields': fields})
            if request_id is not None:
                data.update({'request_id': request_id})
            result = self.request(data, 'vpbx/stats/request')
            if result.status_code == 401:
                return result.json()
            data = {}
            result = result.json()
            if request_id is not None:
                data.update({'request_id': request_id})
            try:
                if result['key'] is not None:
                    data.update({'key': result['key']})
            except KeyError as error:
                raise KeyError(error)
            return self.request(data, 'vpbx/stats/result')
        else:
            raise ValueError('Please specify params')

    def get_stats_call_party(self, request_id=None, call_party_ext=None, call_party_num=None, date_from=None,
                             date_to=None, fields=None):
        if date_from is not None and date_to is not None and (call_party_ext is not None or call_party_num is not None):
            data = {'date_from': str(date_from),
                    'date_to': str(date_to)}
            if call_party_ext is not None:
                data.update({'call_party': {'extenstion': call_party_ext}})
            else:
                data.update({'call_party': {'number': call_party_num}})
            if fields is not None:
                data.update({'fields': fields})
            if request_id is not None:
                data.update({'request_id': request_id})
            result = self.request(data, 'vpbx/stats/request')
            if result.status_code == 401:
                return result.json()
            data = {}
            result = result.json()
            if request_id is not None:
                data.update({'request_id': request_id})
            try:
                if result['key'] is not None:
                    data.update({'key': result['key']})
            except KeyError as error:
                raise KeyError(error)
            return self.request(data, 'vpbx/stats/result').text
        else:
            raise ValueError('Please specify params')

    def dct_user_info(self, number=None):
        if number is not None:
            if isinstance(number, str):
                return self.request({"number": number}, 'queries/user_info_by_dct_number/')
            else:
                raise ValueError('Wrong info type')
        else:
            raise ValueError('Please specify params')

    def dct_user_history(self, number=None):
        if number is not None:
            if isinstance(number, str):
                return self.request({"number": number}, 'queries/user_history_by_dct_number/')
            else:
                raise ValueError('Wrong info type')
        else:
            raise ValueError('Please specify params')

    def user_list(self, ext_fields=None, extension=None):
        data = {}
        if ext_fields is not None:
            data.update({'ext_fields': ext_fields})
        if extension is not None:
            data.update({'extension': extension})
        return self.request(data, 'vpbx/config/users/request')

    def user_add(self, name=None, email=None, mobile=None,
                 department=None, position=None, login=None,
                 password=None, use_status=None, use_cc_numbers=None,
                 access_role_id=None, extension=None, line_id=None,
                 trunk_number_id=None, dial_alg=None, numbers=None):

        return self.request(
            {'name': name, 'email': email, 'mobile': mobile, 'department': department, 'position': position,
             'login': login, 'password': password,
             'use_status': use_status, 'use_cc_numbers': use_cc_numbers, 'access_role_id': access_role_id,
             'extension': extension,
             'line_id': line_id, 'trunk_number_id': trunk_number_id, 'dial_alg': dial_alg, 'numbers': numbers},
            'member/create')

    def user_upd(self, user_id=None, name=None, email=None,
                 mobile=None, department=None, position=None,
                 login=None, password=None, use_status=None,
                 use_cc_numbers=None, access_role_id=None, extension=None,
                 line_id=None, trunk_number_id=None, dial_alg=None,
                 numbers=None):

        return self.request(
            {'user_id': user_id, 'name': name, 'email': email, 'mobile': mobile, 'department': department,
             'position': position, 'login': login, 'password': password,
             'use_status': use_status, 'use_cc_numbers': use_cc_numbers, 'access_role_id': access_role_id,
             'extension': extension,
             'line_id': line_id, 'trunk_number_id': trunk_number_id, 'dial_alg': dial_alg, 'numbers': numbers},
            'member/update')

    def user_del(self, user_id):
        return self.request({'user_id': user_id}, 'member/delete')

    def group_list(self, group_id=None, operator_id=None, operator_extension=None, show_users=1):
        data = {'show_users': show_users}
        if group_id is None and operator_id is None and operator_extension is None:
            return self.request(data, 'vpbx/groups')
        else:
            if group_id is not None:
                data.update({'group_id': group_id})
            else:
                if operator_id is not None:
                    data.update({'operator_id': operator_id})
                else:
                    if operator_extension is not None:
                        data.update({'operator_extension': operator_extension})
        return self.request(data, 'vpbx/groups')

    def group_add(self, name=None, description=None, extension=None,
                  dial_alg_group=None, dial_alg_users=None, auto_redirect=None,
                  auto_dial=None, line_id=None, use_dynamic_ivr=None,
                  use_dynamic_seq_num=None, melody_id=None, operators=None):

        return self.request(
            {'name': name, 'description': description, 'extension': extension, 'dial_alg_group': dial_alg_group,
             'dial_alg_users': dial_alg_users, 'auto_redirect': auto_redirect,
             'auto_dial': auto_dial, 'line_id': line_id, 'use_dynamic_ivr': use_dynamic_ivr,
             'use_dynamic_seq_num': use_dynamic_seq_num, 'melody_id': melody_id, 'operators': operators},
            'group/create')

    def group_upd(self, group_id=None, name=None, description=None,
                  extension=None, dial_alg_group=None, dial_alg_users=None,
                  auto_redirect=None, auto_dial=None, line_id=None,
                  use_dynamic_ivr=None, use_dynamic_seq_num=None,
                  melody_id=None, operators=None):

        return self.request(
            {'group_id': group_id, 'group': {'name': name, 'description': description, 'extension': extension,
                                             'dial_alg_group': dial_alg_group, 'dial_alg_users': dial_alg_users,
                                             'auto_redirect': auto_redirect,
                                             'auto_dial': auto_dial, 'line_id': line_id,
                                             'use_dynamic_ivr': use_dynamic_ivr,
                                             'use_dynamic_seq_num': use_dynamic_seq_num, 'melody_id': melody_id,
                                             'operators': operators}}, 'group/update')

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
            data = {'ext_fields': ['trunks_numbers']}
        else:
            data = {}
        return self.request(data, 'vpbx/schemas/')

    def set_schema(self, line=None, trunk=None, schema=None):
        if schema is not None and (line is not None or schema is not None):
            data = {'schema_id': schema}
            if line is not None:
                data.update({'line_id': line})
            elif trunk is not None:
                data.update({'trunk_number_id': trunk})
        else:
            raise ValueError('Please specify params')
        return self.request(data, 'vpbx/schema/set/')

    def roles(self):
        return self.request({}, 'roles')

    def sips_list(self):
        return self.request({}, 'sips')

    def sip_add(self, user_id=None, password=None, login=None, domain=None, description=None):
        if user_id is not None and password is not None:
            data = {'user_id': user_id, 'password': password}
            if login is not None and domain is not None:
                data.update({'login': login, 'domain': domain})
            if description is not None:
                data.update({'description': description})
            return self.request(data, 'vpbx/sip/create')
        else:
            raise ValueError('Please specify params')

    def sip_edit(self, sip_id=None, user_id=None, password=None, login=None, domain=None, description=None):
        if sip_id is not None:
            if user_id is not None and password is not None:
                data = {'sip_id': sip_id, 'user_id': user_id, 'password': password}
                if login is not None and domain is not None:
                    data.update({'login': login, 'domain': domain})
                if description is not None:
                    data.update({'description': description})
                return self.request(data, 'vpbx/sip/update')
            else:
                raise ValueError('Please specify params')
        else:
            raise ValueError('Please specify params')

    def domains_list(self):
        return self.request({}, 'domains')

    def trunk_num_list(self):
        return self.request({}, 'trunks/numbers')

    def bwlist_state(self):
        return self.request({}, 'bwlists/state/')

    def bwlist_nums(self):
        return self.request({}, 'bwlists/numbers/')

    def bwlist_add(self, number=None, list_type='black', num_type='tel', comment='API'):
        if number is not None:
            return self.request({'number': number, 'list_type': list_type, 'number_type': num_type, 'comment': comment},
                                'bwlists/number/add/')
        else:
            raise ValueError('Please specify params')

    def bwlist_del(self, num_id=None):
        if num_id is not None:
            return self.request({'number_id': num_id}, 'bwlists/number/delete/')
        else:
            raise ValueError('Please specify params')

    def campaign_info(self, campaign_id=None):
        if campaign_id is not None:
            return self.request({'campaign_id': campaign_id}, 'campaign')
        else:
            raise ValueError('Please specify params')

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

        return self.request({'name': name, 'line_id': line_id, 'created_by': created_by, 'priority': priority,
                             'start_date': start_date, 'end_date': end_date, 'schedule': schedule,
                             'operators': operators, 'dial_mode': dial_mode, 'voice_message_id': voice_message_id,
                             'hold_message_id': hold_message_id, 'max_redial_count_if_busy': max_redial_count_if_busy,
                             'max_redial_count_if_no_answ': max_redial_count_if_no_answ,
                             'max_redial_count_if_number_not_avail': max_redial_count_if_number_not_avail,
                             'max_wait_time': max_wait_time,
                             'additional_calls_coefficient': additional_calls_coefficient,
                             'wait_time_if_busy': wait_time_if_busy,
                             'wait_time_if_no_answ': wait_time_if_no_answ,
                             'wait_time_if_number_not_avail': wait_time_if_number_not_avail,
                             'after_call_processing': after_call_processing}, 'campaign/add')

    def camp_task_add(self, campaign_id=None, tasks=None):
        return self.request({'campaign_id': str(campaign_id), 'tasks': tasks}, 'tasks/push')

    def campaign_start(self, campaign_id=None):
        if campaign_id is not None:
            return self.request({'campaign_id': campaign_id}, 'campaign/start')
        else:
            raise ValueError('Please specify params')

    def campaign_stop(self, campaign_id=None):
        if campaign_id is not None:
            return self.request({'campaign_id': campaign_id}, 'campaign/stop')
        else:
            raise ValueError('Please specify params')

    def campaign_del(self, campaign_id=None):
        if campaign_id is not None:
            return self.request({'campaign_id': campaign_id}, 'campaign/delete')
        else:
            raise ValueError('Please specify params')

    def record_meth_get(self, record_id):
        url = self.url + 'queries/recording/link/' + record_id + '/download/' + self.key + '/' + \
              str(int(time.time()) + 10800) + '/' + sha256(self.key.encode('utf-8') +
                                                           str(int(time.time()) + 10800).encode('utf-8') +
                                                           record_id.encode('utf-8') +
                                                           self.salt.encode('utf-8')).hexdigest()
        result = get(url)
        if self.logger is not None and result.status_code not in [401, 404]:
            self.logger.info({"url": result.url, "headers": result.request.headers, "data": result.request.body})
            try:
                self.logger.error(
                    {'status': result.status_code, 'headers': result.headers, 'response': loads(result.text)})
            except:
                self.logger.error({'status': result.status_code, 'headers': result.headers, 'response': result.text})
        elif self.logger is not None:
            self.logger.info({"url": result.url, "headers": result.request.headers, "data": result.request.body})
            self.logger.error({'status': result.status_code, 'headers': result.headers})
            self.logger.error({"details": "For details you can contact techsupport, "
                                          "please write this log in your request, http-request-id",
                               "X-Uuid": result.headers.get('X-Uuid')})
        return result.url

    def record_meth_post(self, record_id):
        return self.request({'recording_id': record_id, 'action': 'download'}, 'queries/recording/post/').url

    def speech2text(self, record_id=None, with_terms=None, with_names=None):
        if record_id is not None:
            data = {"recording_id": '[\"' + record_id + '\"]'}
            if with_terms is not None:
                data.update({'with_terms': True})
            if with_names is not None:
                data.update({'with_names': True})
            return self.request(data, 'vpbx/queries/recording_categories/')
        else:
            raise ValueError('Please specify params')

    # AddressBook ...
    # /ab/organization/         - Получить организацию по id
    # /ab/organizations/init    - Получить список организаций, инициация отчета
    # /ab/organizations/cursor  - Получить список организаций, постраничное получение
    # /ab/organizations/create  - Добавить организацию
    # /ab/organizations/update  - Редактировать организацию
    # /ab/organizations/delete  - Удалить организацию POST
    # /ab/group                 - Получить группу по id
    # /ab/groups/init           - Получить список групп, инициация отчета
    # /ab/groups/cursor         - Получить список групп, постраничное получение
    # /ab/groups/create/        - Добавить группу
    # /ab/groups/update         - Редактировать группу
    # /ab/groups/delete         - Удалить группу

    def ab_contact(self, contact_id, contact_ext_fields=None):
        if contact_id is not None:
            data = {"contact_id": contact_id}
            if contact_ext_fields is not None:
                data.update({'contact_ext_fields': contact_ext_fields})
            return self.request(data, 'vpbx/ab/contact/')
        else:
            raise ValueError('Please specify params')

    def ab_contact_init(self, query="", limit_rows=None, order=None, contact_ext_fields=None):
        if query is not None:
            data = {"query": query}
            if limit_rows is not None:
                data.update({'limit_rows': limit_rows})
            if order is not None:
                data.update({'order': order})
            if contact_ext_fields is not None:
                data.update({'contact_ext_fields': contact_ext_fields})
            return self.request(data, 'vpbx/ab/contact/init/')
        else:
            raise ValueError('Please specify params')

    def ab_contact_cursor(self, mode=None, cursor=None, contact_ext_fields=None):
        if mode is not None and cursor is not None:
            data = {"query": query, "cursor": cursor}
            if contact_ext_fields is not None:
                data.update({'contact_ext_fields': contact_ext_fields})
            return self.request(data, 'vpbx/ab/contact/cursor/')
        else:
            raise ValueError('Please specify params')

    def ab_contacts_create(self, type=0, name=None, office=None, site=None, org=None, importance=None, comment=None,
                           birthday=None, sex=None, phones: List = None, emails: List = None, groups=None,
                           nets: List = None, messengers: List = None, in_favorites: List = None,
                           custom_values: List = None, user_id=None, on_error="skip"):
        if type is not None and name is not None:
            contact_data = {"type": type, 'name': name}
            if office is not None:
                contact_data.update({'office': office})
            if site is not None:
                contact_data.update({'site': site})
            if org is not None:
                contact_data.update({'org': org})
            if importance is not None:
                contact_data.update({'importance': importance})
            if comment is not None:
                contact_data.update({'comment': comment})
            if birthday is not None:
                contact_data.update({'birthday': birthday})
            if sex is not None:
                contact_data.update({'sex': sex})
            if phones is not None:
                contact_data.update({'phones': phones})
            if emails is not None:
                contact_data.update({'emails': emails})
            if groups is not None:
                contact_data.update({'groups': groups})
            if nets is not None:
                contact_data.update({'nets': nets})
            if messengers is not None:
                contact_data.update({'messengers': messengers})
            if in_favorites is not None:
                contact_data.update({'in_favorites': in_favorites})
            if custom_values is not None:
                contact_data.update({'custom_values': custom_values})
            if user_id is not None:
                contact_data.update({'user_id': user_id})

            data = {"data": [contact_data]}
            if on_error is not None:
                data.update({'on_error': on_error})

            return self.request(data, 'vpbx/ab/contacts/create/')
        else:
            raise ValueError('Please specify params')

    def ab_contact_update(self, contact_id, type=None, name=None, office=None, site=None, org=None, importance=None,
                          comment=None, birthday=None, sex=None, phones: List = None, emails: List = None, groups=None,
                          nets: List = None, messengers: List = None, in_favorites: List = None,
                          custom_values: List = None, user_id=None, on_error="skip"):
        if contact_id is not None:
            contact_data = {"contact_id": contact_id}
            if type is not None:
                contact_data.update({'type': type})
            if name is not None:
                contact_data.update({'name': name})
            if office is not None:
                contact_data.update({'office': office})
            if site is not None:
                contact_data.update({'site': site})
            if org is not None:
                contact_data.update({'org': org})
            if importance is not None:
                contact_data.update({'importance': importance})
            if comment is not None:
                contact_data.update({'comment': comment})
            if birthday is not None:
                contact_data.update({'birthday': birthday})
            if sex is not None:
                contact_data.update({'sex': sex})
            if phones is not None:
                contact_data.update({'phones': phones})
            if emails is not None:
                contact_data.update({'emails': emails})
            if groups is not None:
                contact_data.update({'groups': groups})
            if nets is not None:
                contact_data.update({'nets': nets})
            if messengers is not None:
                contact_data.update({'messengers': messengers})
            if in_favorites is not None:
                contact_data.update({'in_favorites': in_favorites})
            if custom_values is not None:
                contact_data.update({'custom_values': custom_values})
            if user_id is not None:
                contact_data.update({'user_id': user_id})

            data = {"data": [contact_data]}
            if on_error is not None:
                data.update({'on_error': on_error})

            return self.request(data, 'vpbx/ab/contacts/update/')
        else:
            raise ValueError('Please specify params')

    # /events/ab        - Уведомление об операциях с адресной книгой
    # /ab/custom_fields - Получение набора пользовательских полей

    def cc_deal_list(self, product_id, from_date=None, until_date=None,
                     members_ids=None, contact_id=None,
                     status=None
                     ):
        if product_id:
            data = {'product_id': product_id}
            if from_date is not None:
                data.update({'from_date': from_date})
            if from_date is not None:
                data.update({'from_date': from_date})
            if until_date is not None:
                data.update({'until_date': until_date})
            if members_ids is not None:
                data.update({'members_ids': members_ids})
            if contact_id is not None:
                data.update({'contact_id': contact_id})
            if status is not None:
                data.update({'status': status})
            return self.request(data, 'cc/deal/list')
        else:
            raise ValueError('Please specify params')

    def cc_deal_create(self, product_id, contact_id=None, name=None, description=None, amount=None, member_id=None,
                       funnel_id=None, step_id=None, create_date=None, status=None, custom_fields: Dict = None,
                       status_change_reason=None, reason_comment=None):
        if name is not None and product_id is not None:
            data = {"name": name, "product_id": product_id}
            if contact_id is not None:
                data.update({'contact_id': contact_id})
            if description is not None:
                data.update({'description': description})
            if amount is not None:
                data.update({'amount': amount})
            if member_id is not None:
                data.update({'member_id': member_id})
            if funnel_id is not None:
                data.update({'funnel_id': funnel_id})
            if step_id is not None:
                data.update({'step_id': step_id})
            if create_date is not None:
                data.update({'create_date': create_date})
            if status is not None:
                data.update({'status': status})
            if status_change_reason is not None:
                data.update({'status_change_reason': status_change_reason})
            if custom_fields is not None:
                data.update({'custom_fields': custom_fields})
            if reason_comment is not None:
                data.update({'reason_comment': reason_comment})
            return self.request(data, 'cc/deal/create/')
        else:
            raise ValueError('Please specify params')

    def cc_deal_update(self, deal_id, product_id, contact_id=None, name=None, description=None, amount=None,
                       member_id=None, funnel_id=None, step_id=None, create_date=None, status=None,
                       custom_fields: Dict = None, status_change_reason=None, reason_comment=None):
        if deal_id is not None and product_id is not None and name is not None:
            data = {"deal_id": deal_id, "product_id": product_id, "name": name}
            if contact_id is not None:
                data.update({'contact_id': contact_id})
            if name is not None:
                data.update({'name': name})
            if description is not None:
                data.update({'description': description})
            if amount is not None:
                data.update({'amount': amount})
            if member_id is not None:
                data.update({'member_id': member_id})
            if funnel_id is not None:
                data.update({'funnel_id': funnel_id})
            if step_id is not None:
                data.update({'step_id': step_id})
            if create_date is not None:
                data.update({'create_date': create_date})
            if status is not None:
                data.update({'status': status})
            if status_change_reason is not None:
                data.update({'status_change_reason': status_change_reason})
            if custom_fields is not None:
                data.update({'custom_fields': custom_fields})
            if reason_comment is not None:
                data.update({'reason_comment': reason_comment})
            return self.request(data, 'cc/deal/update/')
        else:
            raise ValueError('Please specify params')

    def cc_deal_funnels_list(self, product_id):
        if product_id is not None:
            data = {"product_id": product_id, }
            return self.request(data, 'cc/deal/funnels.list/')
        else:
            raise ValueError('Please specify params')
