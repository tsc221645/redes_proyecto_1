# Phase 5: SQL Anywhere data model

The local source is SQL Anywhere 17, exposed through a configured server on
the configured TCP port. Python must connect through the installed 64-bit ODBC driver
`SQL Anywhere 17` and a read-only database user.

## Business scope

The valid-sales rule is applied by the analytical view and must not be omitted:

```sql
m.TIPO = 'FA' AND m.ESTADO = 'V'
```

The main relationship is:

```text
PT_MOVIMIENTOS 1 --- * PT_D_MOVIMIENTOS * --- 1 PT_PRODUCTOS
PT_PRODUCTOS   * --- 1 PT_LINEAS
PT_PRODUCTOS   * --- 1 PT_PAISES
PT_MOVIMIENTOS.FECHA_INGRESO --- TC_HISTORICO_BANGUAT.FECHA
```

The preferred read model is `V_LINEAS_FACTURADAS_ANALITICAS`. It contains
line-level metrics with invoice discounts allocated proportionally and amounts
converted to quetzales when the invoice currency is `US$`. The source tables
must not be queried directly by the future LLM or MCP tools.

## Security and anonymization

The local database may contain real business data, but application logs must
not contain customer names, NITs, invoice identifiers, product descriptions or
full transaction rows. The remote dataset should replace sensitive values with
stable labels such as `Producto_0001`, `Cliente_0001`, `Marca_0001` and
`Linea_0001`. `NOMBRE_CLIENTE` and `NIT` are excluded from analytical outputs.

All monetary metrics are expressed in quetzales. Q and US$ values must never be
aggregated before conversion using `TC_HISTORICO_BANGUAT`.

## Initial repository query

The first repository method uses the view and filters `ANIO` through parameters.
This keeps SQL fixed and prevents arbitrary SQL from entering the application.
The returned metrics are sales amount, estimated margin, margin percentage and
average ticket; the margin is an estimate, not an accounting result.
