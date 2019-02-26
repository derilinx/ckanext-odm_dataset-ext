


-- # simple move: (possible wrap bare string in json dict or array
-- mv = [ ('note_translated', 'MD_DataIdentification_abstract'),
--        ('taxonomy', 'MD_DataIdentification_topicCategory'),
--        ('odm_language', 'MD_DataIdentification_language'),
--        ('odm_access_and_use_constraints', 'MD_Constraints'),
--        ('odm_accuracy', 'DQ_PositionalAccuracy'),
--        ('odm_logical_consistency', 'DQ_LogicalConsistency'),
--        ('odm_completeness', 'DQ_Completeness'),
--        ('odm_process', 'LI_ProcessStep'),
--        ('odm_source', 'LI_Lineage'),
--        ('odm_contact', 'CI_ResponsibleParty_Contact'),
--        ('odm_metadata_reference_information', 'MD_Metadata.contact'),
--        ('odm_attributes', 'MD_ScopeDescription.attributes'),
-- ]
-- # convert to iso style date, or timestamp
-- date_formatter = [
--     ('odm_date_created', 'CI_Citation.date'),
--     ('odm_date_uploaded', 'MD_Metadata.dateStamp'),
--     ('odm_date_modified', 'CI_Citation_lastRevision'),
-- ]

-- split_formatter = [
--     ('odm_temporal_range', ('EX_TemporalExtent.startDate', 'EX_TemporalExtent.enddate')),
--     ]


-- ### sql for reading

-- select package_extra.*, tr.* from package_extra inner join package on(package_extra.package_id=package.id) inner join ( VALUES
--     ('note_translated', 'MD_DataIdentification_abstract'),
--     ('taxonomy', 'MD_DataIdentification_topicCategory'),
--     ('odm_language', 'MD_DataIdentification_language'),
--     ('odm_access_and_use_constraints', 'MD_Constraints'),
--     ('odm_accuracy', 'DQ_PositionalAccuracy'),
--     ('odm_logical_consistency', 'DQ_LogicalConsistency'),
--     ('odm_completeness', 'DQ_Completeness'),
--     ('odm_process', 'LI_ProcessStep'),
--     ('odm_source', 'LI_Lineage'),
--     ('odm_contact', 'CI_ResponsibleParty_Contact'),
--     ('odm_metadata_reference_information', 'MD_Metadata.contact'),
--     ('odm_attributes', 'MD_ScopeDescription.attributes'),
--     ('odm_date_created', 'CI_Citation.date'),
--     ('odm_date_uploaded', 'MD_Metadata.dateStamp'),
--     ('odm_date_modified', 'CI_Citation_lastRevision')
-- ) as tr (original, translated) on (package_extra.key = tr.original)
-- where
-- package.type = 'dataset'
-- and value is not null
-- and value != '';


begin;
-- # sql for updating
-- Convention is UU_TitleCase_camelCase, all underscores

-- there's one package that is preventing indexing
update package set metadata_created=metadata_modified where state='active' and metadata_created is null;

-- # sql for updating
update package_extra set key=translated
  from package,  ( VALUES
    ('note_translated', 'MD_DataIdentification_abstract'),
    ('taxonomy', 'MD_DataIdentification_topicCategory'),
    ('odm_language', 'MD_DataIdentification_language'),
    ('odm_access_and_use_constraints', 'MD_Constraints'),
    ('odm_accuracy', 'DQ_PositionalAccuracy'),
    ('odm_logical_consistency', 'DQ_LogicalConsistency'),
    ('odm_completeness', 'DQ_Completeness'),
    ('odm_process', 'LI_ProcessStep'),
    ('odm_source', 'LI_Lineage'),
    ('odm_contact', 'CI_ResponsibleParty_contact'),
    ('odm_metadata_reference_information', 'MD_Metadata_contact'),
    ('odm_attributes', 'MD_ScopeDescription_attributes'),
    ('odm_date_created', 'CI_Citation_date'),
    ('odm_date_uploaded', 'MD_Metadata_dateStamp'),
    ('odm_date_modified', 'CI_Citation_lastRevision'),
    ('odm_temporal_range', 'EX_TemporalExtent_startDate')
) as tr (original, translated)
where
package_extra.package_id = package.id
and package_extra.key = tr.original
and package.type = 'dataset'
and value is not null
and value != '';

commit;

-- begin;
-- -- Only on existing upgraded systems with the old schema
-- update package_extra set key=translated
--   from package,  ( VALUES
--     ('CI_ResponsibleParty_Contact', 'CI_ResponsibleParty_contact'),
--     ('MD_Metadata.contact', 'MD_Metadata_contact'),
--     ('MD_ScopeDescription.attributes', 'MD_ScopeDescription_attributes'),
--     ('CI_Citation.date', 'CI_Citation_date'),
--     ('MD_Metadata.dateStamp', 'MD_Metadata_dateStamp'),
--     ('EX_TemporalExtent.startDate', 'EX_TemporalExtent_startDate')
-- ) as tr (original, translated)
-- where
-- package_extra.package_id = package.id
-- and package_extra.key = tr.original
-- and package.type = 'dataset'
-- and value is not null
-- and value != '';

-- commit;

begin;

update package_extra set value = trim(replace(value, 'to', ':'))
  from package
  where
  package_extra.package_id = package.id
  and package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value like '% to %';

update package_extra set value = trim(replace(value,'+',''))
  from package
  where
  package_extra.package_id = package.id
  and package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value like '%+%';

insert into package_extra (id, package_id, key, value, revision_id, state)
  select reverse(pe.id), pe.package_id, 'EX_TemporalExtent_endDate',
         trim(split_part(value, '-',2)) , pe.revision_id, pe.state
  from package_extra as pe inner join package on (pe.package_id = package.id)
  where
  package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value not like '%:%'
  and value like '%-%';

update package_extra set value = trim(split_part(value, '-', 1))
  from package
  where
  package_extra.package_id = package.id
  and package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value not like '%:%'
  and value not like '%to%'
  and value like '%-%';

update package_extra set value = trim(replace(replace(value, '0000 - 00 - 00', ''), ':',''))
  from package
  where
  package_extra.package_id = package.id
  and package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value like '%0000 - 00 - 00%';

update package_extra set value = trim(replace(replace(value, '0000-00-00', ''),':',''))
  from package
  where
  package_extra.package_id = package.id
  and package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value like '%0000-00-00%';

update package_extra set value = trim(replace(replace(value, '00/00/0000', ''),':',''))
  from package
  where
  package_extra.package_id = package.id
  and package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value like '%00/00/0000%';

  
-- iso date format
update package_extra set value = trim(replace(replace(value, ' -','-'), '- ','-'))
  from package
  where
  package_extra.package_id = package.id
  and package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and (value like '%- %' or value like '% -');

insert into package_extra (id, package_id, key, value, revision_id, state)
  select reverse(pe.id), pe.package_id, 'EX_TemporalExtent_endDate',
         trim(split_part(value, ':',2)) , pe.revision_id, pe.state
  from package_extra as pe inner join package on (pe.package_id = package.id)
  where
  package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value like '%:%';

update package_extra set value = trim(split_part(value, ':', 1))
  from package
  where
  package_extra.package_id = package.id
  and package.type = 'dataset'
  and key = 'EX_TemporalExtent_startDate'
  and value like '%:%';

commit;
