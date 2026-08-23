-- Total turnover by venue to track location performance and compare sites.
{{
    config(
        materialized='view',
        tags=['venue_turnover', 'marts']
    )
}}


select
    venue_code,
    sum(turnover_sum) as total_turnover

from {{ ref('stg_game_performance') }}

group by venue_code