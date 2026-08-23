{{
    config(
        severity='warn',
        tags=['valid_games_played', 'tests']
    )
}}


select *
from {{ ref('stg_game_performance') }}
where games_played_sum < 0
