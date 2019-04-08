# Changelog

For older changelog, please see [Re2o changelog](https://gitlab.federez.net/federez/re2o/blob/master/CHANGELOG.md).

## MR 1

View permission is now global in the project,
you need to remove the old permission then manually add the new permission to groups.

```python
from django.contrib.auth.models import Permission
permissions = Permission.objects.filter(codename__startswith='view')
permissions.delete()
```
