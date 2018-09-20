get_all_published_procedures_info_query = '''SELECT
  p.id as p_procedure_id,
  p.eisRegistrationNumber as p_procedure_number,
  l.id as p_lot_id,
  l.number as p_lot_number,
  l.status as p_lot_status,
  p.requestEndDateTime as p_request_end_datetime
FROM procedures p
  JOIN lot l
    ON l.procedureId = p.id
    AND l.actualId IS NULL
    AND l.archive = 0
    AND l.active = 1
WHERE p.status = 'procedure.published'
AND p.actualId IS NULL
AND p.archive = 0
AND p.active = 1
;'''

get_one_published_procedures_info_query = '''SELECT
  p.id as p_procedure_id,
  p.eisRegistrationNumber as p_procedure_number,
  l.id as p_lot_id,
  l.number as p_lot_number,
  l.status as p_lot_status,
  p.requestEndDateTime as p_request_end_datetime
FROM procedures p
  JOIN lot l
    ON l.procedureId = p.id
    AND l.actualId IS NULL
    AND l.archive = 0
    AND l.active = 1
WHERE p.status = 'procedure.published'
AND p.actualId IS NULL
AND p.archive = 0
AND p.active = 1
AND p.eisRegistrationNumber = '%s'
;'''

check_add_request_action_status_query = '''SELECT
  pla.id
FROM procedure_223_lot_action pla
WHERE pla.code = 'addRequest'
AND pla.deleted_at IS NULL
AND pla.lot_id = %(c_lot_id)s
;'''


get_catalog_procedure_info_query = '''SELECT
  p.status_id AS c_procedure_status_id,
  l.status_id AS c_lot_status_id,
  p.id AS c_procedure_id,
  l.id AS c_lot_id,
  l.request_end_give_datetime AS c_request_end_datetime,
  l.regulated_datetime AS c_regulated_datetime
FROM procedure_223 p
  JOIN procedure_223_lot l
    ON l.procedure_id = p.id
    AND l.deleted_at IS NULL
WHERE p.deleted_at IS NULL
AND p.etp_id = %(p_procedure_id)s
AND l.etp_id = %(p_lot_id)s
AND p.oos_registration_number = '%(p_procedure_number)s'
;'''


check_protocol_exists_query = '''SELECT
id AS protocol_id,
createDateTime AS protocol_create_datetime,
editDateTime AS protocol_edit_datetime,
publishDateTime AS protocol_publish_datetime,
status AS protocol_status,
lotId AS protocol_lot_id,
signatureId AS protocol_signature_id,
discriminator AS protocol_discriminator,
additionalInfo AS protocol_additional_info,
withMultipleParticipants AS protocol_with_multiple_participants,
documentId AS protocol_document_id,
guid AS protocol_guid
  FROM protocol
  WHERE lotId = %(p_lot_id)s'''




