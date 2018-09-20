import argparse
import re
from datetime import datetime
from itertools import count
from sys import exit as s_exit
from ets.ets_mysql_lib import MysqlConnection as Mc
from ets.ets_xml_worker import PROCEDURE_223_TYPES
from queries import *
from queries_templates import *
from backup_templates import *


PROGNAME = 'Check published auctions Nagios plugin (223)'
DESCRIPTION = '''Плагин Nagios для проверки закупок на статусе прием заявок (223)'''
VERSION = '1.0'
AUTHOR = 'Belim S.'
RELEASE_DATE = '2018-09-20'

OK, WARNING, CRITICAL, UNKNOWN = range(4)
EXIT_DICT = {'exit_status': OK, 'ok': 0, 'warning': 0, 'critical': 0}
INFO_TEMPLATE = '%(p_procedure_number)s |%(p_procedure_id)s, %(p_lot_id)s|: %(error)s'


ok_counter = count(start=1, step=1)
warning_counter = count(start=1, step=1)
critical_counter = count(start=1, step=1)


# обработчик параметров командной строки
def create_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--version', action='store_true',
                        help="Показать версию программы")

    parser.add_argument('-a', '--auction', type=str, default='',
                        help="Номер процедуры")

    parser.add_argument('-f', '--file', type=str, default='',
                        help="Файл для сохранения корректировок")

    parser.add_argument('-t', '--type', type=str, default='', required=True,
                        choices=PROCEDURE_223_TYPES.keys(),
                        help="Тип процедуры (обязательный)")

    parser.add_argument('-c', '--print_corrections', action='store_true',
                        help="Вывод корректировок на консоль")

    parser.add_argument('-i', '--full_info', action='store_true',
                        help="Вывод полной информации на консоль")

    return parser

my_parser = create_parser()
namespace = my_parser.parse_args()


def show_version():
    print(PROGNAME, VERSION, '\n', DESCRIPTION, '\nAuthor:', AUTHOR, '\nRelease date:', RELEASE_DATE)


def correction_printer(query_template, input_file=None):
    """Декоратор вывода строки корректировки"""
    def decorator(func):
        def wrapped(auction_data):
            info = func(auction_data)
            if auction_data.get('error'):
                query_out = query_template % auction_data
                query_out = re.sub(r"'NULL'", "NULL", query_out, re.MULTILINE | re.DOTALL)

                if namespace.print_corrections:
                    print(query_out)

                if input_file:
                    with open(input_file, mode='a', encoding='utf8') as file_w_pl:
                        file_w_pl.write(query_out)
                        file_w_pl.write('\n')
            return info
        return wrapped
    return decorator


def out_printer(func):
    """Декоратор для вывода текста на консоль"""
    def wrapped(auction_data):
        info = func(auction_data)
        if info.get('error') and namespace.full_info:
            info_out = INFO_TEMPLATE % info
            print(info_out)
        return info
    return wrapped


def only_if_catalog_record_exists(func):
    """Декоратор для вывода текста на консоль"""
    def wrapped(auction_data):
        if 'c_procedure_id' in auction_data:
            info = func(auction_data)
        else:
            info = auction_data
        return info
    return wrapped


def set_warning(func):
    """Декоратор для для добавления warning"""
    def wrapped(auction_data):
        info = func(auction_data)
        if info.get('error'):
            info['error_flag'] = True
            EXIT_DICT['exit_status'] = WARNING if EXIT_DICT['exit_status'] < WARNING else EXIT_DICT['exit_status']
            EXIT_DICT['warning'] = next(warning_counter)
        info['error'] = None
        return info
    return wrapped


def set_critical(func):
    """Декоратор для для добавления critical"""
    def wrapped(auction_data):
        info = func(auction_data)
        if info.get('error'):
            info['error_flag'] = True
            EXIT_DICT['exit_status'] = CRITICAL if EXIT_DICT['exit_status'] < CRITICAL else EXIT_DICT['exit_status']
            EXIT_DICT['critical'] = next(critical_counter)
        info['error'] = None
        return info
    return wrapped


@set_critical
@correction_printer('''-- Требуется портировать сведения о процедуре в каталог''', input_file=namespace.file)
@out_printer
def check_catalog_procedure_exist_record(auction_data):
    catalog_procedure_info = cn_catalog.execute_query(get_catalog_procedure_info_query % row, dicted=True)
    if not catalog_procedure_info:
        auction_data['error'] = 'по процедуре отсутствует запись в каталоге'
    else:
        auction_data.update(catalog_procedure_info[0])
    return auction_data


@set_critical
@correction_printer('''-- Необходимо проверить состояние демона, отвечающего за смену статуса закупок''',
                    input_file=namespace.file)
@out_printer
def check_request_end_datetime(auction_data):
    """Проверка даты окончания подачи заявок"""
    if auction_data['p_request_end_datetime'] < datetime.now():
        auction_data['error'] = 'некорректная дата окончания приема заявок в базе процедур'
    return auction_data


@set_warning
@correction_printer(backup_regulated_datetime_c, input_file=namespace.file)
@correction_printer(set_regulated_datetime_c, input_file=namespace.file)
@out_printer
@only_if_catalog_record_exists
def check_regulated_datetime_c(auction_data):
    """Проверка regulated_datetime в каталоге"""
    if not auction_data['c_regulated_datetime'] == auction_data['p_request_end_datetime']:
        auction_data['error'] = 'некорректная дата по текущему статусу'
    return auction_data


@set_critical
@correction_printer(backup_request_end_datetime_c, input_file=namespace.file)
@correction_printer(set_request_end_datetime_c, input_file=namespace.file)
@out_printer
@only_if_catalog_record_exists
def check_request_end_datetime_c(auction_data):
    """Проверка даты окончания подачи заявок в каталоге"""
    if not auction_data['c_request_end_datetime'] == auction_data['p_request_end_datetime']:
        auction_data['error'] = 'некорректная дата окончания приема заявок в каталоге'
    return auction_data


@set_critical
@correction_printer(backup_published_status_lot_p, input_file=namespace.file)
@correction_printer(set_published_status_lot_p, input_file=namespace.file)
@out_printer
def check_lot_status_p(auction_data):
    """Проверка статуса лота в базе процедур"""
    if not auction_data['p_lot_status'] == 'lot.published':
        auction_data['error'] = 'некорректный статус лота в базе процедур'
    return auction_data


@set_critical
@correction_printer(backup_published_status_procedure_c, input_file=namespace.file)
@correction_printer(set_published_status_procedure_c, input_file=namespace.file)
@out_printer
def check_procedure_status_c(auction_data):
    """Проверка статуса процедуры в каталоге"""
    if not auction_data['c_procedure_status_id'] == 5:
        auction_data['error'] = 'некорректный статус процедуры в каталоге'
    return auction_data


@set_critical
@correction_printer(backup_published_status_procedure_c, input_file=namespace.file)
@correction_printer(set_published_status_lot_c, input_file=namespace.file)
@out_printer
def check_lot_status_c(auction_data):
    """Проверка статуса лота в каталоге"""
    if not auction_data['c_lot_status_id'] == 25:
        auction_data['error'] = 'некорректный статус лота в каталоге'
    return auction_data


@set_critical
@correction_printer(backup_protocol)
@correction_printer(delete_protocol_template)
@out_printer
def check_protocol_not_exists(auction_data):
    """Проверка отсутствия протокола"""
    protocol_exists = cn_procedures.execute_query(check_protocol_exists_query % row, dicted=True)
    if protocol_exists:
        auction_data.update(protocol_exists)
        auction_data['error'] = 'существует протокол на статусе прием заявок'
    return auction_data


@set_critical
@out_printer
@only_if_catalog_record_exists
def check_add_request_action_catalog(auction_data):
    """Проверка даты окончания подачи заявок"""
    add_request_action_status = cn_catalog.execute_query(check_add_request_action_status_query % auction_data)
    if not add_request_action_status:
        auction_data['error'] = 'отсутствует ссылка на подачу заявки'
    return auction_data

if __name__ == '__main__':
    try:
        # инициализируем подключения
        cn_procedures = Mc(connection=PROCEDURE_223_TYPES[namespace.type]['connection']).connect()
        cn_catalog = Mc(connection=Mc.MS_223_CATALOG_CONNECT).connect()

        if namespace.auction:
            all_published_procedures_info = cn_procedures.execute_query(get_one_published_procedures_info_query %
                                                                        namespace.auction, dicted=True)
        else:
            all_published_procedures_info = cn_procedures.execute_query(get_all_published_procedures_info_query,
                                                                        dicted=True)

        # если поиск по базе с текущими условиями ничего не дал, то указываем, что ничего не нашлось
        if not all_published_procedures_info:
            print('Nothing to check')
            s_exit(UNKNOWN)

        if namespace.file:
            with open(namespace.file, mode='w', encoding='utf8') as file_w:
                file_w.write('')

        # выполняем все проверки
        for row in all_published_procedures_info:
            row['procedure_type'] = namespace.type
            check_catalog_procedure_exist_record(row)
            check_lot_status_p(row)
            check_procedure_status_c(row)
            check_lot_status_c(row)
            check_request_end_datetime(row)
            check_request_end_datetime_c(row)
            check_regulated_datetime_c(row)
            check_add_request_action_catalog(row)
            check_protocol_not_exists(row)

            # если все проверки завершились успешно, то увеличиваем количество ok на единицу
            if not row.get('error_flag'):
                EXIT_DICT['ok'] = next(ok_counter)

        # в режиме плагина выводим только краткую информацию
        if namespace.print_corrections or namespace.full_info:
            if EXIT_DICT['exit_status'] == OK:
                print('All OK!')
        else:
            print('''Checking status:\nOK: %(ok)s\nWarning: %(warning)s\nCritical: %(critical)s''' % EXIT_DICT)

        s_exit(EXIT_DICT['exit_status'])

    except Exception as err:
        print('Plugin error')
        print(err)
        s_exit(UNKNOWN)

    show_version()
    print('For more information run use --help')
    s_exit(UNKNOWN)












