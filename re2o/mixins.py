# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Gabriel Détraz
# Copyright © 2017  Charlie Jacomme

"""re2o.mixins
A set of mixins used all over the project to avoid duplicating code
"""

from reversion import revisions as reversion
from django.db import transaction
from django.utils.translation import ugettext as _


class RevMixin(object):
    """ A mixin to subclass the save and delete function of a model
    to enforce the versioning of the object before those actions
    really happen """
    def save(self, *args, **kwargs):
        """ Creates a version of this object and save it to database """
        if self.pk is None:
            with transaction.atomic(), reversion.create_revision():
                reversion.set_comment("Creation")
                return super(RevMixin, self).save(*args, **kwargs)
        return super(RevMixin, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Creates a version of this object and delete it from database """
        with transaction.atomic(), reversion.create_revision():
            reversion.set_comment("Deletion")
            return super(RevMixin, self).delete(*args, **kwargs)


class FormRevMixin(object):
    """ A mixin to subclass the save function of a form
    to enforce the versionning of the object before it is really edited """
    def save(self, *args, **kwargs):
        """ Create a version of this object and save it to database """
        if reversion.get_comment() != "" and self.changed_data != []:
            reversion.set_comment(
                reversion.get_comment() + ",%s"
                % ', '.join(field for field in self.changed_data)
            )
        elif self.changed_data:
            reversion.set_comment(
                "Field(s) altered : %s"
                % ', '.join(field for field in self.changed_data)
            )
        return super(FormRevMixin, self).save(*args, **kwargs)


class AclMixin(object):
    """This mixin is used in nearly every class/models defined in re2o apps.
    It is used by acl, in models (decorators can_...) and in templates tags
    :get_instance: Applied on a class, take an id argument, return an instance
    :can_create: Applied on a class, take the requested user, return if the
        user can do the creation
    :can_edit: Applied on an instance, return if the user can edit the
        instance
    :can_delete: Applied on an instance, return if the user can delete the
        instance
    :can_view: Applied on an instance, return if the user can view the
        instance
    :can_view_all: Applied on a class, return if the user can view all
        instances"""

    @classmethod
    def get_classname(cls):
        """ Returns the name of the class where this mixin is used """
        return str(cls.__name__).lower()

    @classmethod
    def get_modulename(cls):
        """ Returns the name of the module where this mixin is used """
        return str(cls.__module__).split('.')[0].lower()

    @classmethod
    def get_instance(cls, *_args, **kwargs):
        """Récupère une instance
        :param objectid: Instance id à trouver
        :return: Une instance de la classe évidemment"""
        object_id = kwargs.get(cls.get_classname() + 'id')
        return cls.objects.get(pk=object_id)

    @classmethod
    def can_create(cls, user_request, *_args, **_kwargs):
        """Verifie que l'user a les bons droits pour créer
        un object
        :param user_request: instance utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return (
            user_request.has_perm(
                cls.get_modulename() + '.add_' + cls.get_classname()
            ),
            (_("You don't have the right to create a %s object.")
                % cls.get_classname())
        )

    def can_edit(self, user_request, *_args, **_kwargs):
        """Verifie que l'user a les bons droits pour editer
        cette instance
        :param self: Instance à editer
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return (
            user_request.has_perm(
                self.get_modulename() + '.change_' + self.get_classname()
            ),
            (_("You don't have the right to edit a %s object.")
                % self.get_classname())
        )

    def can_delete(self, user_request, *_args, **_kwargs):
        """Verifie que l'user a les bons droits pour delete
        cette instance
        :param self: Instance à delete
        :param user_request: Utilisateur qui fait la requête
        :return: soit True, soit False avec la raison de l'échec"""
        return (
            user_request.has_perm(
                self.get_modulename() + '.delete_' + self.get_classname()
            ),
            (_("You don't have the right to delete a %s object.")
                % self.get_classname())
        )

    @classmethod
    def can_view_all(cls, user_request, *_args, **_kwargs):
        """Vérifie qu'on peut bien afficher l'ensemble des objets,
        droit particulier view objet correspondant
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return (
            user_request.has_perm(
                cls.get_modulename() + '.view_' + cls.get_classname()
            ),
            (_("You don't have the right to view every %s object.")
                % cls.get_classname())
        )

    def can_view(self, user_request, *_args, **_kwargs):
        """Vérifie qu'on peut bien voir cette instance particulière avec
        droit view objet
        :param self: instance à voir
        :param user_request: instance user qui fait l'edition
        :return: True ou False avec la raison de l'échec le cas échéant"""
        return (
            user_request.has_perm(
                self.get_modulename() + '.view_' + self.get_classname()
            ),
            (_("You don't have the right to view a %s object.")
                % self.get_classname())
        )

