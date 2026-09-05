from backend.data_access.postgres import PostgresRepository


def test_postgres_translates_top_parameter():
    sql, params = PostgresRepository._translate("SELECT TOP ? id FROM items ORDER BY id", (5, "x"))
    assert "SELECT id" in sql
    assert sql.endswith("LIMIT %s")
    assert params == ("x", 5)


def test_postgres_translates_fixed_top():
    sql, params = PostgresRepository._translate("SELECT TOP 1 id FROM items", ())
    assert sql == "SELECT id FROM items LIMIT %s"
    assert params == (1,)
