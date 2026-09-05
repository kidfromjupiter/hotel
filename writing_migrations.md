## How to write migrations

All migrations should be placed inside ./db/migrations and must follow the `V<version>__<description>.sql` naming convention exactly.
Unapplied migrations will be auto applied by `Flyway` during `docker compose up` automatically.
Migrations are applied sequentially, and as such, the `<version>` part of the naming convention must be a strictly increasing sequence.


## What are db migrations

We could define the entire db within the sql cmdline, but that would be a hassle to write and confusing for other developers since only the 
one who developed the db, knows whats going on. 
With migrations, every change we do to the database is documented in migrations/ folder. 
This also makes it easier to revert back to a preexisting version if neccessary.

Migrations are written using standard sql. Although, note that we're using postgres, so sql functions and triggers will need to be written in 
postgres-specific way.


## What is in seed/

Seed data is data that we populate as example data in the database when we first run the database. We use seed data so that all members of the team have
the same db data for testing.
