-- Revenue by venue and EGM to understand which machines are contributing most.
{{
    config(
        materialized='view',
        tags=['egm_venue_revenue', 'marts']
    )
}}

select
    venue_code,
    egm_description,
    sum(gmp_sum) as total_revenue

from {{ ref('stg_game_performance') }}

group by
    venue_code,
    egm_description