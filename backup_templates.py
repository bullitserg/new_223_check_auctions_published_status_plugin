backup_published_status_lot_p = ''' -- UPDATE `%(procedure_type)s`.lot SET status = '%(p_lot_status)s' WHERE id = %(p_lot_id)s; -- %(p_procedure_number)s'''

backup_published_status_procedure_c = ''' -- UPDATE `sectionks_catalog_223`.procedure_223 SET status_id = %(c_procedure_status_id)s, update_at = NOW() WHERE id = %(c_procedure_id)s; -- %(p_procedure_number)s'''

backup_published_status_lot_c = ''' -- UPDATE `sectionks_catalog_223`.procedure_223_lot SET status_id = %(c_lot_status_id)s, update_at = NOW() WHERE id = %(c_lot_id)s;  -- %(p_procedure_number)s'''

backup_protocol = '''-- INSERT INTO protocol(id, createDateTime, editDateTime, publishDateTime, status, lotId, signatureId, discriminator, additionalInfo, withMultipleParticipants, documentId, guid)
--  VALUES('%(protocol_id)s', '%(protocol_create_datetime)s', '%(protocol_edit_datetime)s', '%(protocol_publish_datetime)s',
-- '%(protocol_status)s', '%(protocol_lot_id)s', '%(protocol_signature_id)s', '%(protocol_discriminator)s',
-- '%(protocol_additional_info)s', '%(protocol_with_multiple_participants)s', '%(protocol_document_id)s', '%(protocol_guid)s');  -- %(p_procedure_number)s'''

backup_regulated_datetime_c = ''' -- UPDATE `sectionks_catalog_223`.procedure_223_lot pl SET pl.regulated_datetime = '%(c_regulated_datetime)s' WHERE id = %(c_lot_id)s;  -- %(p_procedure_number)s'''

backup_request_end_datetime_c = ''' -- UPDATE `sectionks_catalog_223`.procedure_223_lot pl SET pl.request_end_give_datetime = '%(c_request_end_datetime)s' WHERE pl.id = %(c_lot_id)s;  -- %(p_procedure_number)s'''

backup_add_request_action_c = '''-- DELETE FROM procedure_223_lot_action WHERE code = 'addRequest' AND deleted_at IS NULL AND lot_id = %(c_lot_id)s'''