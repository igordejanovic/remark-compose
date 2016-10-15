import os
import sys
import click
import livereload
import jinja2
import glob2
from .rconf import get_rconf_meta
from .exceptions import RComposeException


class RComposeCLI(click.MultiCommand):

    def list_commands(self, ctx):
        return ['serve', 'build']

    def get_command(self, ctx, name):
        this_module = sys.modules[__name__]
        if not hasattr(this_module, name):
            raise RComposeException('Unknown command "{}".'.format(name))
        return getattr(this_module, name)

remarkc = RComposeCLI(
    help='Remark slides building from template with live HTTP server.')


def _find_files(glob_pattern):
    input_files = []
    for f in glob2.glob(glob_pattern):
        input_files.append(f)
    return input_files


def _load_rconf(rconf_file):
    if not rconf_file.endswith('.rconf'):
        rconf_file += '.rconf'
    return get_rconf_meta().model_from_file(rconf_file)


def _get_param(obj, name):

    for p in obj.params:
        if p.name == name:
            return p.value

    # If this object has parent than it is rule.
    # Continue search on the model level.
    if hasattr(obj, "parent"):
        for p in obj.parent.params:
            if p.name == name:
                return p.value

    raise RComposeException('"{}" parameter is not defined.'.format(name))


@click.command()
@click.argument('rconf_file')
@click.option('-p', '--port', default=9090,
              help='Port to listen to. Default is 9090.')
def serve(rconf_file, port):
    """
    Watch input markdown files for change and regenerates target files.
    """
    try:
        rconf_model = _load_rconf(rconf_file)

        def do_build():
            _internal_build(rconf_file)

        watch_files = set()

        template_file = _get_param(rconf_model, "template")
        if template_file:
            watch_files.add(template_file)

        for rule in rconf_model.rules:
            watch_files.update(_find_files(rule.input_file))

            # Add template file if the rule overrides global template
            watch_files.add(_get_param(rconf_model, "template"))

        server = livereload.Server()
        for f in watch_files:
            server.watch(f, do_build)

        server.serve(port=port)

    except RComposeException as e:
        click.echo(e)


@click.command()
@click.argument('rconf_file')
def build(rconf_file):
    """
    Generates target html files from markdown files and HTML template.
    """
    try:
        _internal_build(rconf_file)
    except RComposeException as e:
        click.echo(e)


def _internal_build(rconf_file):

    rconf_model = _load_rconf(rconf_file)

    click.echo("Building output files...")

    def _gen_html(input_file, template, params, output_file):

        with open(input_file, 'r') as f:
            content = f.read()
            params['content'] = content

        base_name = os.path.basename(input_file)
        base_name = os.path.splitext(base_name)[0]

        if not output_file:
            output_file = os.path.join(os.path.dirname(input_file),
                                       "{}.html".format(base_name))
        elif os.path.isdir(output_file):
            output_file = os.path.join(output_file,
                                       "{}.html".format(base_name))

        click.echo(output_file)

        with open(output_file, 'w') as f:
            f.write(template.render(**params))

    global_params = {p.name: p.value for p in rconf_model.params}

    for rule in rconf_model.rules:
        rule_params = {p.name: p.value for p in rule.params}

        # Take global params and override with rule params
        params = dict(global_params)
        params.update(rule_params)

        with open(_get_param(rule, "template"), 'r') as f:
            t = jinja2.Template(f.read())

        for f in _find_files(rule.input_file):
            _gen_html(f, t, params, rule.output_file)
