{{
    config(
        materialized='incremental',
        unique_key=['bus_date', 'venue_code', 'egm_description', 'manufacturer', 'fp'],
        tags=['staging', 'stg_game_performance']
    )
}}

-- Keep the staging layer clean and typed for downstream reporting.
select
    cast(bus_date as date) as bus_date,
    venue_code,
    egm_description,
    manufacturer,
    fp,
    cast(turnover_sum as numeric(18,2)) as turnover_sum,
    cast(gmp_sum as numeric(18,2)) as gmp_sum,
    cast(games_played_sum as numeric(18,2)) as games_played_sum

from {{ source('raw', 'game_performance') }}

-- Only pick up rows that are newer than the latest date already in staging.
{% if is_incremental() %}
where cast(bus_date as date) > (
    select max(cast(bus_date as date))
    from {{ this }}
)
{% endif %}