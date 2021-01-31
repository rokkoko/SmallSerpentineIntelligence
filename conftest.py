from pytest_postgresql import factories

# We do custom fixture to have fixed port for easier local connection
postgresql_custom_fixture = factories.postgresql_proc(port=5433)

postgres = factories.postgresql(
    'postgresql_custom_fixture',
    load=['database_schema.sql']
)
