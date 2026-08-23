{{
    config(
        severity='warn',
        tags=['positive_turnover', 'tests']
    )
}}

-- This test checks the business rule that turnover should not be zero or negative.
-- In the staging layer we cast turnover_sum to NUMERIC(18,2) so values keep their cents and behave predictably in reporting.
select *
from {{ ref('stg_game_performance') }}
where turnover_sum <= 0