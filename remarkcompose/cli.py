# -*- encoding: utf-8 -*-
import os
import sys
import click
import livereload
import jinja2
import glob2
import codecs
from datetime import datetime
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


jinja_env = None


@click.command()
@click.argument('rconf_file')
@click.option('-p', '--port', default=9090,
              help='Port to listen to. Default is 9090.')
@click.option('-f', '--force', default=False, is_flag=True,
              help='Build all files always. Don\'t check file update time.')
def serve(rconf_file, port, force):
    """
    Watch input markdown files for change and regenerates target files.
    """
    if not rconf_file.endswith('.rconf'):
        rconf_file += '.rconf'

    def _get_from_rel(f):
        """Returns path given relatively to rconf file."""
        return os.path.join(os.path.dirname(rconf_file), f)

    try:
        rconf_model = _load_rconf(rconf_file)

        def do_build(report_files=False):
            """Callback triggered when file change is detected."""
            _internal_build(rconf_file, force, port=port,
                            report_files=report_files)

        watch_files = set()
        watch_files.add(rconf_file)

        # Add template defined on the rconf model level to the
        # list of watched files.
        template_file = _get_param(rconf_model, "template")
        if template_file:
            watch_files.add(_get_from_rel(template_file))

        # Add all input files to the list of watched files together
        # with rule-level defined template if any.
        for rule in rconf_model.rules:
            watch_files.update(_find_files(rule.input_file,
                                           parent=rconf_file,
                                           strip_parent=False))

            watch_files.add(_get_from_rel(_get_param(rule, "template")))

        server = livereload.Server()
        for f in watch_files:
            server.watch(f, do_build)

        # Build if necessary
        do_build(report_files=True)

        # Start server
        server.serve(port=port, root=os.path.dirname(rconf_file))

    except RComposeException as e:
        click.echo(e)


@click.command()
@click.argument('rconf_file')
@click.option('-f', '--force', default=False, is_flag=True,
              help='Build all files. Don\'t check file update time.')
def build(rconf_file, force):
    """
    Generates target html files from markdown files and HTML template.
    """

    try:
        _internal_build(rconf_file, force)
    except RComposeException as e:
        click.echo(e)


def _internal_build(rconf_file, force=False, port=None, report_files=False):
    """
    Build all output file for changed input files.
    Args:
        rconf_file(path): rconf file to use
        force (bool): Build all files, don't check modification time.
        port (int): If in server mode this is the server TCP port.
        report_file(bool): If all file links should be reported
            (used on startup).
    """

    global jinja_env

    if not rconf_file.endswith('.rconf'):
        rconf_file += '.rconf'

    # Loading of templates and input files is relative to rconf model
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(rconf_file)))

    jinja_env.filters['dtformat'] = _dtformat

    rconf_model = _load_rconf(rconf_file)

    click.echo("Building output files...")

    def _gen_html(input_file, main_template, params, output_file):

        global jinja_env

        # Calculate output file name
        base_name = os.path.basename(input_file)
        base_name = os.path.splitext(base_name)[0]

        if not output_file:
            output_file = os.path.join(
                os.path.dirname(os.path.join(os.path.dirname(rconf_file),
                                             input_file)),
                "{}.html".format(base_name))
        elif os.path.isdir(output_file):
            output_file = os.path.join(output_file,
                                       "{}.html".format(base_name))

        rebuild = True
        if not force and os.path.exists(output_file):
            # Do not build file if output is newer than input and template
            ofile_mtime = os.path.getmtime(output_file)
            ifile_mtime = os.path.getmtime(
                os.path.join(os.path.dirname(rconf_file), input_file))
            tfile_mtime = os.path.getmtime(
                os.path.join(os.path.dirname(rconf_file), main_template))
            rconf_mtime = os.path.getmtime(rconf_file)
            if ofile_mtime > rconf_mtime and ofile_mtime > ifile_mtime \
               and ofile_mtime > tfile_mtime:
                rebuild = False

        # Content input file is processed by template engine
        params['now'] = datetime.now()

        # Remark uses `{{content}}` for reference of the place to insert new
        # content on partial slides. Do not change that.
        params['content'] = '{{content}}'
        content = jinja_env.get_template(input_file).render(**params)

        # Pass rendered input as the parameter to output html template
        params['content'] = content

        if rebuild or report_files:
            if port:
                click.echo('http://127.0.0.1:%s/%s' % (port, output_file))
            else:
                click.echo(output_file)

        if rebuild:
            t = jinja_env.get_template(main_template)
            with codecs.open(output_file, 'w', 'utf-8') as f:
                f.write(t.render(**params))

    global_params = {p.name: p.value for p in rconf_model.params}

    for rule in rconf_model.rules:
        rule_params = {p.name: p.value for p in rule.params}

        # Take global params and override with rule params
        params = dict(global_params)
        params.update(rule_params)

        for f in _find_files(rule.input_file, parent=rconf_file):
            _gen_html(f, _get_param(rule, "template"), params,
                      rule.output_file)


def _find_files(glob_pattern, parent=None, strip_parent=True):
    """Searces for files given by glob_pattern relative to parent."""

    input_files = []

    if parent:
        parent = os.path.dirname(parent)
    if parent:
        glob_pattern = os.path.join(parent, glob_pattern)

    for f in glob2.glob(glob_pattern):
        input_files.append(f)

    # Strip parent from founded names
    if parent and strip_parent:
        input_files = [os.path.relpath(x, parent) for x in input_files]

    return input_files


def _join_dir(parent, f):
    return os.path.join(os.path.dirname(parent), f)


def _load_rconf(rconf_file):
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


def _dtformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)
