delete_protocol_template = ''' -- Удаляем протокол
DELETE FROM `%(procedure_type)s`.protocol WHERE id = %(protocol_id)s; -- %(p_procedure_number)s'''

set_published_status_lot_p = ''' -- Устанавливаем статус лота в базе процедур
UPDATE `%(procedure_type)s`.lot SET status = 'lot.published' WHERE id = %(p_lot_id)s; -- %(p_procedure_number)s'''

set_published_status_procedure_c = ''' -- Устанавливаем статус процедуры в каталоге
UPDATE `sectionks_catalog_223`.procedure_223 SET status_id = 5, update_at = NOW() WHERE id = %(c_procedure_id)s; -- %(p_procedure_number)s'''

set_published_status_lot_c = ''' -- Устанавливаем статус лота в каталоге
UPDATE `sectionks_catalog_223`.procedure_223_lot SET status_id = 25, update_at = NOW() WHERE id = %(c_lot_id)s;  -- %(p_procedure_number)s'''

set_regulated_datetime_c = ''' -- Устанавливаем regulated_datetime
UPDATE `sectionks_catalog_223`.procedure_223_lot pl SET pl.regulated_datetime = '%(p_request_end_datetime)s' WHERE id = %(c_lot_id)s;  -- %(p_procedure_number)s'''

set_request_end_datetime_c = ''' -- Устанавливаем дату окончания приема заявок в каталоге
UPDATE `sectionks_catalog_223`.procedure_223_lot pl SET pl.request_end_give_datetime = '%(p_request_end_datetime)s' WHERE pl.id = %(c_lot_id)s;  -- %(p_procedure_number)s'''













