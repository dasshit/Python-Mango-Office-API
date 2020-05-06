#!/usr/bin/env python
#API wrapper for Mango Office

#Example:


from mangoofficeapi import MangoAPI
api_vpbx_key = 'your_key'
api_vpbx_salt = 'your_salt'
api_vpbx_url = 'https://app.mango-office.ru/vpbx/'

api = MangoAPI(api_vpbx_url, api_vpbx_key, api_vpbx_salt)

api.sms(from_ext='66613', text='Test API', number='79999999999') # Отправляем СМС на номер 79999999999 от имени сотрудника с внутренним номером 66613

api.callback(from_ext='66613', to_num='79999999999', line='74994725673') # Обратный звонок номеру 79999999999 от внутреннего номера 66613

api.group_callback(from_ext='51545', to_num='79999999999', line='74994725673') # Групповой обратный звонок

api.hangup(call_id='MToxMDA1NzU5Mzo1MDI6NjI1ODM4MzQ=') # Команда завершения вызова

api.start_record(call_id='MToxMDA1NzU5Mzo0ODE6NjI0MzQ2NjU4', call_party_number='66613') # Команда начала записи разговора относительно сотрудника 66613

api.start_play(call_id='MToxMDA1NzU5MzoyNDE6NjQzNDY5OTYwOjE=', internal_id='1000237176') # Команда для проигрывания нужной записи в IVR

api.route(call_id='MToxMDA1NzU5MzozNjE6NjIxNTE1NjE2OjE=', to_number='1050')  # Команда маршрутизации вызова (пока он IVR)

api.transfer(call_id='MToxMDA1NzU5MzozNjE6NjIxNTE1OTE1', to_number='66613', method='blind', initiator='1050') # Перевод вызова

api.get_stats_to(to_ext='66613', date_from=1583020800, date_to=1585609200, fields="records, start, finish, answer, from_extension, from_number, to_extension,to_number, disconnect_reason, line_number, location, create, entry_id")  # Получение статистики входящих для указанного абонента

api.get_stats_from(from_ext='66613', date_from=1583020800, date_to=1585609200, fields="records, start, finish, answer, from_extension, from_number, to_extension,to_number, disconnect_reason, line_number, location, create, entry_id")  # Получение статистики исходящих для указанного абонента

api.get_stats_call_party(call_party_ext='66613', date_from=1583020800, date_to=1585609200, fields="records, start, finish, answer, from_extension, from_number, to_extension,to_number, disconnect_reason, line_number, location, create, entry_id")  # Получение статистики всех вызовов для указанного абонента

api.dct_user_info(number='8 (495) 149-5361') # Получение меток ДКТ

api.dct_user_history(number='8 (495) 149-5361') # Получение истории переходов пользователя

listt = ["general.user_id","general.sips","groups","general.access_role_id","telephony.dial_alg","telephony.numbers.schedule","telephony.line_id","telephony.trunk_number_id","general.mobile","general.login","general.use_status","general.use_cc_numbers"]
result = api.user_list(ext_fields=listt) # Получение списка сотрудников

api.group_list(group_id='11863903', operator_id='400741444') # Получение списка групп

api.balance() # Получение баланса

api.lines() # Получение исходящих линий

api.audio() # Получение списка аудиозаписей

api.schemas(ext_fields=1) # Получение списка схем

api.set_schema(schema=10426699, line=400741445) # Установка схемы на номере

api.roles() # Получение списка ролей

api.sips_list() # Получение списка sip-учеток

api.domains_list() # Получения списка доменов

api.trunk_num_list() # Получение списка номеров из транков

api.bwlist_state() # Статус ЧБ списка

api.bwlist_nums() # Получение списка номеров в ЧБ списке

api.bwlist_add(number='79123124123') # Добавление номера в ЧБ

api.bwlist_del(10660389) # Удаление номера из ЧБ списка

api.campaign_info(campaign_id=12312) # Получение информации о кампании ИО
