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
        wm_yr_wk

    FROM {{ source('raw', 'calendar') }}

),

price_data AS (

    SELECT
        item_id,
        store_id,
        wm_yr_wk,
        sell_price

    FROM {{ source('raw', 'sell_prices') }}

),

daily_sales_enriched AS (

    SELECT
        s.id,
        s.item_id,
        s.dept_id,
        s.cat_id,
        s.store_id,
        s.state_id,
        c.date,
        c.wm_yr_wk,
        s.sales_quantity,
        p.sell_price

    FROM daily_sales s

    LEFT JOIN calendar_data c
        ON s.day_id = c.day_id

    LEFT JOIN price_data p
        ON s.item_id = p.item_id
        AND s.store_id = p.store_id
        AND c.wm_yr_wk = p.wm_yr_wk

)

SELECT
    item_id,
    dept_id,
    cat_id,
    store_id,
    state_id,

    wm_yr_wk,

    MIN(date) AS week_start_date,
    MAX(date) AS week_end_date,

    SUM(sales_quantity) AS total_sales_quantity,

    AVG(sales_quantity) AS avg_daily_sales,

    AVG(sell_price) AS avg_sell_price,

    COUNT(DISTINCT date) AS sales_days

FROM daily_sales_enriched

GROUP BY
    item_id,
    dept_id,
    cat_id,
    store_id,
    state_id,
    wm_yr_wk