{{
    config(
        severity='warn',
        tags=['raw_to_staging_completeness', 'tests']
    )
}}

-- Make sure the staging layer is not dropping or duplicating rows from the raw source.
with raw_count as (
    select count(*) as raw_row_count
    from {{ source('raw', 'game_performance') }}
),
staging_count as (
    select count(*) as staging_row_count
    from {{ ref('stg_game_performance') }}
)
select *
from raw_count
cross join staging_count
where raw_row_count <> staging_row_count
