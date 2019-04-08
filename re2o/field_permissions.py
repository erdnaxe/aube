# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2018  Maël Kervella

"""re2o.field_permissions
A model mixin and a field mixin used to remove some unauthorized fields
from the form automatically generated from the model. The model must
subclass `FieldPermissionModelMixin` and the form must subclass
`FieldPermissionFieldMixin` so when a Django form is generated from the
fields of the models, some fields will be removed if the user don't have
the rights to change them (can_change_{name})
"""

class FieldPermissionModelMixin:
    """ The model mixin. Defines the `has_field_perm` function """
    field_permissions = {}  # {'field_name': callable}
    FIELD_PERM_CODENAME = 'can_change_{model}_{name}'
    FIELD_PERMISSION_GETTER = 'can_change_{name}'
    FIELD_PERMISSION_MISSING_DEFAULT = True

    def has_field_perm(self, user, field):
        """ Checks if a `user` has the right to edit the `field`
        of this model """
        if field in self.field_permissions:
            checks = self.field_permissions[field]
            if not isinstance(checks, (list, tuple)):
                checks = [checks]

        else:
            checks = []

            # Consult the optional field-specific hook.
            getter_name = self.FIELD_PERMISSION_GETTER.format(name=field)
            if hasattr(self, getter_name):
                checks.append(getattr(self, getter_name))

            # Try to find a static permission for the field
            else:
                perm_label = self.FIELD_PERM_CODENAME.format(**{
                    'model': self._meta.model_name,
                    'name': field,
                })
                if perm_label in dict(self._meta.permissions):
                    checks.append(perm_label)

        # No requirements means no restrictions.
        if not len(checks):
            return self.FIELD_PERMISSION_MISSING_DEFAULT

        # Try to find a user setting that qualifies them for permission.
        for perm in checks:
            if callable(perm):
                result, _reason = perm(user_request=user)
                if result is not None:
                    return result
            else:
                # Don't supply 'obj', or else infinite recursion.
                result = user.has_perm(perm)
                if result:
                    return True

        # If no requirement can be met, then permission is denied.
        return False


class FieldPermissionFormMixin:
    """
    Construit le formulaire et retire les champs interdits
    """
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')

        super(FieldPermissionFormMixin, self).__init__(*args, **kwargs)
        to_be_deleted = []
        for name in self.fields:
            if not self.instance.has_field_perm(user, field=name):
                to_be_deleted.append(name)
        for name in to_be_deleted:
            self.remove_unauthorized_field(name)

    def remove_unauthorized_field(self, name):
        """ Remove one field from the fields of the form """
        del self.fields[name]
