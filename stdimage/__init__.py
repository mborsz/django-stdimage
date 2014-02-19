from __future__ import absolute_import

from .fields import StdImageField

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^stdimage\.fields"])
except ImportError:
    pass
