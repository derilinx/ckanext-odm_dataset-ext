begin;

update package set author = null, author_email = null where author is not null;
update package_revision set author = null, author_email = null where author is not null;

update package set maintainer = null, maintainer_email = null where maintainer is not null;
update package_revision set maintainer = null, maintainer_email = null where maintainer is not null;

update activity
set data = jsonb_set(jsonb_set(data::jsonb, '{package,author}', '""'),
                    '{package,author_email}'
                    , '""')
where data::jsonb #> '{package,author}' is not null;

update activity_detail
set data = jsonb_set(jsonb_set(data::jsonb, '{package,author}', '""'),
                    '{package,author_email}'
                    , '""')
where data::jsonb #> '{package,author}' is not null;

update activity
set data = jsonb_set(jsonb_set(data::jsonb, '{package,maintainer}', '""'),
                    '{package,maintainer_email}'
                    , '""')
where data::jsonb #> '{package,maintainer}' is not null;

update activity_detail
set data = jsonb_set(jsonb_set(data::jsonb, '{package,maintainer}', '""'),
                    '{package,maintainer_email}'
                    , '""')
where data::jsonb #> '{package,maintainer}' is not null;

commit;
