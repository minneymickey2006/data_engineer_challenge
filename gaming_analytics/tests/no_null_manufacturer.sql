{{
    config(
        severity='ERROR',
        tags=['no_null_manufacturer', 'tests']
    )
}}

select *
from {{ ref('stg_game_performance') }}
where manufacturer is null or manufacturer = ''
