# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Matthieu Michelet
# Copyright © 2018  Gabriel Detraz

"""
Write in a python file the list of all contributors sorted by number of
commits. This list is extracted from the current gitlab repository.
"""

import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ The command object for `gen_contrib` """
    help = 'Update contributors list'

    @staticmethod
    def _contrib_file_generator(contributors):
        """
        Generate the content of contributors.py
        """
        buffer = "# -*- mode: python; coding: utf-8 -*-\n"
        buffer += "\"\"\"re2o.contributors\n"
        buffer += "A list of the proud contributors to Re2o\n"
        buffer += "\"\"\"\n"
        buffer += "\n"
        buffer += "CONTRIBUTORS = [\n"
        for name in contributors:
            # Split name into parts
            names = name.split()

            # Normalize it
            names = list(map(str.capitalize, names))

            # Put it back together
            name_text = " ".join(names)
            buffer += "    '{}',\n".format(name_text)
        buffer += "]"

        return buffer

    def handle(self, *args, **options):
        contributors = [
            item.split('\t')[1]
            for item in os.popen("git shortlog -s -n").read().split("\n")
            if '\t' in item
        ]
        self.stdout.write(self.style.SUCCESS("Exportation Successful"))
        with open("re2o/contributors.py", "w") as contrib_file:
            content = self._contrib_file_generator(contributors)
            contrib_file.write(content)
