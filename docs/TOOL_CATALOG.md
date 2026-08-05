# Business tool catalog

The previous MCI queries are suitable as controlled implementations because
they read from `V_LINEAS_FACTURADAS_ANALITICAS`. They must be converted from
`UNLOAD SELECT` exports into repository queries that return structured rows.
They must also receive date ranges and limits as parameters.

## General analytical tool

`query_business_metrics` is the general-purpose tool for executive questions.
It accepts controlled dimensions, metrics, filters, sorting and a bounded row
limit. It does not accept SQL text from the model.

Supported dimensions:

```text
year, month, product_code, product_name, brand, line, country, client, currency
```

Supported metrics:

```text
sales, gross_sales, cost, margin, units, invoice_count, line_count
```

For local execution, the tool resolves catalog codes to readable names using:

```sql
V_LINEAS_FACTURADAS_ANALITICAS.MARCA = PT_MARCAS.MARCA
```

and returns `PT_MARCAS.NOMBRE` for the `brand` dimension. The same approach
is applied to `PT_CLIENTES.NOMBRE_CLIENTE` for the `client` dimension. It should
also be applied to `PT_LINEAS.NOMBRE` and `PT_PAISES.NOMBRE` when those joins
are confirmed in the database.

## Candidate tools

| Query | MCP tool | Main parameters |
|---|---|---|
| Monthly sales | `get_sales_summary` | `start_date`, `end_date`, `currency` |
| Annual sales | `get_annual_sales` | `start_date`, `end_date`, `currency` |
| Top products by sales | `get_top_products` | dates, `limit`, `line_code`, `country_code` |
| Top products by margin | `get_top_products_by_margin` | dates, `limit`, line |
| Sales vs. margin matrix | `get_product_sales_margin_matrix` | dates, `limit` |
| Sales by line | `get_sales_by_product_line` | dates, line |
| Sales by brand | `get_sales_by_brand` | dates, `limit` |
| Top customers | `get_top_customers` | dates, `limit` |
| Product Pareto | `get_product_pareto` | dates, `limit` |
| Product ABC | `get_product_abc` | dates |
| Prescriptive product recommendations | `get_product_recommendations` | dates, product/line filters |
| Recommendation summary | `get_recommendation_summary` | dates |
| General bounded analytics | `query_business_metrics` | dates, dimensions, metrics, filters, limit |

The CSV `UNLOAD` clauses are intentionally excluded from the application.
Tools return bounded structured data; exports can be a later, explicit feature.
For the current local environment, real product and brand names remain
available to support development and validation. Customer identifiers and
other sensitive fields must still be handled carefully in logs. Anonymization
will be applied to the remote dataset and/or its presentation layer before
deployment. All tools must use parameterized date filters and enforce a maximum
row limit.
