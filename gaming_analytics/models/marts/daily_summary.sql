
-- Daily totals by date for business reporting and trend checks.
{{
    config(
        materialized='view',
        tags=['daily_summary', 'marts']
    )
}}

select
    bus_date,
    sum(turnover_sum) as total_turnover,
    sum(gmp_sum) as total_revenue,
    sum(games_played_sum) as total_games_played

from {{ ref('stg_game_performance') }}

group by bus_date