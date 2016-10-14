import os
from textx.metamodel import metamodel_from_file
from .exceptions import RComposeException


def validate_rule(rule):
    """
    RConf rule validation. Glob pattern rules must have directory for
    output or None.
    """

    if '*' in rule.input_file:
        if rule.output_file:
            if not os.path.isdir(rule.output_file):
                raise RComposeException(
                    'Error: output must be directory for glob pattern inputs.')


def get_rconf_meta():

    grammar_file = os.path.join(os.path.dirname(__file__),
                                'rconf.tx')
    mm = metamodel_from_file(grammar_file)
    mm.register_obj_processors({'Rule': validate_rule})

    return mm
