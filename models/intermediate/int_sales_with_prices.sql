{{ config(materialized='view') }}

WITH sales_source AS (

    SELECT *
    FROM {{ source('raw', 'sales_train_validation') }}

),

daily_sales AS (

    SELECT
        id,
        item_id,
        dept_id,
        cat_id,
        store_id,
        state_id,
        day_id,
        sales_quantity

    FROM sales_source

    UNPIVOT (
        sales_quantity FOR day_id IN (

            {% for i in range(1, 1914) %}
                d_{{ i }}{% if not loop.last %},{% endif %}
            {% endfor %}

        )
    )

),

calendar_data AS (

    SELECT
        d AS day_id,
        date,
        wm_yr_wk,
        weekday,
        wday,
        month,
        year,
        event_name_1,
        event_type_1,
        event_name_2,
        event_type_2

    FROM {{ source('raw', 'calendar') }}

),

daily_sales_with_calendar AS (

    SELECT
        s.id,
        s.item_id,
        s.dept_id,
        s.cat_id,
        s.store_id,
        s.state_id,

        c.date,
        c.wm_yr_wk,
        c.weekday,
        c.wday,
        c.month,
        c.year,

        c.event_name_1,
        c.event_type_1,
        c.event_name_2,
        c.event_type_2,

        s.sales_quantity

    FROM daily_sales s

    LEFT JOIN calendar_data c
        ON s.day_id = c.day_id

),

price_data AS (

    SELECT
        item_id,
        store_id,
        wm_yr_wk,
        sell_price

    FROM {{ source('raw', 'sell_prices') }}

)

SELECT
    s.id,
    s.item_id,
    s.dept_id,
    s.cat_id,
    s.store_id,
    s.state_id,

    s.date,
    s.wm_yr_wk,

    s.weekday,
    s.wday,
    s.month,
    s.year,

    s.event_name_1,
    s.event_type_1,
    s.event_name_2,
    s.event_type_2,

    s.sales_quantity,
    p.sell_price

FROM daily_sales_with_calendar s

LEFT JOIN price_data p
    ON s.item_id = p.item_id
    AND s.store_id = p.store_id
    AND s.wm_yr_wk = p.wm_yr_wk