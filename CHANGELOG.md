# Changelog

For older changelog, please see [Re2o changelog](https://gitlab.federez.net/federez/re2o/blob/master/CHANGELOG.md).

## MR 1

View permission is now global in the project,
you need to remove the old permission, migrate, then manually add the new permission to groups.

```python
from django.contrib.auth.models import Permission
permissions = Permission.objects.filter(codename__startswith='view')
permissions.delete()
```

## MR 2

With the addition of Django Sites, you will need to change the site name in the management interface (sites menu).