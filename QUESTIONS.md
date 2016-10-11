# Glossary

**New** - Any item created after the creation of the back-up.

# Questions

## What *new* items will be lost after a database restore?

The following **new** items will be lost: -

- changes / reviews
- groups
- dashboards

## What happens to *new* reviews after a restore?

**New** review are lost if the database is restored as they are stored in the database after it was backed up.

## What happen to *new* repos after a restore?

**New** repos are picked-up by the reindexing of gerrit. However if the database is restored their reviews will be lost.

## Is it possible to restore deleted repos?

> **TODO:** Add support for repo only restore, via ```gerrit_backup_tool```.

Yes, via restore argument ```--repo-list gerrit_backup_repos.txt```. However currently this will restore the database also, deleting **new** reviews. So it's a good idea to do a back-up first and then a restore.

## Have to select a specific back-up versions

> **TODO:** Implement, the main task was to restore data onto a new server after an unrecovable failer of an active server.
