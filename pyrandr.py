#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple xrandr wrapper for organising output layout
"""
import argparse
import logging
import re
import subprocess


DISPLAY_RE = re.compile(r'^(?P<output>[a-zA-Z0-9-]+)\s'
                        r'(?P<status>d?i?s?connected)\s'
                        r'(?P<is_primary>primary\s)?'
                        r'(?P<active>\d+x\d+\+\d+\+\d+\s)?'
                        r'.*')
RESOLUTION_RE = re.compile(r'^\s+(?P<width>\d+)x(?P<height>\d+)\s.*')


def setup_logger(args):
    """Setup logger format and level"""

    level = logging.WARNING

    if args.quiet:
        level = logging.ERROR
        if args.quiet > 1:
            level = logging.CRITICAL

    if args.verbose:
        level = logging.INFO
        if args.verbose > 1:
            level = logging.DEBUG

    logging.basicConfig(level=level,
                        format="%(levelname)s: %(message)s")


class Output(object):
    def __init__(self, name, connected, primary):
        self.name = name
        self.connected = connected
        self.primary = primary
        self.active = False

        self.x = 0
        self.y = 0
        self.shift_x = 0
        self.shift_y = 0

    def __repr__(self):
        active = 'active' if self.active else 'inactive'
        connected = 'conected' if self.connected else 'disconnected'
        primary = 'primary ' if self.primary else ''
        if self.connected:
            return "%s %s %s %s(%dx%s)" % (self.name, connected, active,
                                           primary, self.x, self.y)
        else:
            return "%s %s %s" % (self.name, connected, active)

    def get_randr_options(self, primary=False):
        """Return options for xrandr command as a list"""
        if self.connected:
            options = ['--output', self.name,
                       '--mode', "%dx%d" % (self.x, self.y),
                       '--pos', "%dx%d" % (self.shift_x, self.shift_y),
                       '--rotate', "normal"]
            if primary:
                options.append('--primary')
        else:
            if primary:
                raise ValueError('Cannot set output to be primary since it\'s'
                                 ' not connected.')
            options = ['--output', self.name, '--off']

        return options


class Organizer(object):
    def __init__(self):
        self._outputs = {}
        self._get_outputs()

    def __repr__(self):
        return str(self._outputs)

    def _get_outputs(self):
        xrandr = subprocess.check_output(['xrandr'])

        in_output = False

        for line in xrandr.decode().split('\n'):
            match = DISPLAY_RE.match(line)
            if match:
                data = match.groupdict()
                name = data['output']
                connected = data['status'] == 'connected'
                primary = bool(data['is_primary'])
                self._outputs[name] = Output(name, connected, primary)
                self._outputs[name].active = bool(data['active'])
                in_output = True
                continue

            match = RESOLUTION_RE.match(line)
            if match and in_output:
                in_output = False
                data = match.groupdict()
                self._outputs[name].x = int(data['width'])
                self._outputs[name].y = int(data['height'])

                continue

    def output_list(self):
        for name in sorted(self._outputs):
            print(self._outputs[name])

    def panic(self, primary):
        """Just turn on all outputs at once in "mirror" mode"""
        logging.info('Panic mode')
        cmd = ['xrandr']
        for name in self._outputs:
            out = self._outputs[name]
            cmd.extend(out.get_randr_options(primary == out.name))

        logging.debug("command to execute: \n%s", " ".join(cmd))
        subprocess.call(cmd)

    def set_outputs(self, output_list, primary):
        """
        Arrange displays in horizontal way, starting from first outpu in
        output_list as leftmost
        """
        logging.info('Set output horizontally in order: %s',
                     ' '.join(output_list))

        # check, if primary is in output_list
        if primary and primary not in output_list:
            raise ValueError("Cannot set primary to '%s', since it is not "
                             "connected or it is turned off" % primary)

        # check if output_list contains right names
        for name in output_list:
            if name not in self._outputs:
                raise ValueError("Output `%s' doesn't exists" % name)

        # "disconnect" output, so that we can turn it off
        for name in self._outputs:
            if name not in output_list:
                self._outputs[name].connected = False

        # calculate position for every output
        shift = 0
        for name in output_list:
            self._outputs[name].shift_x = shift
            logging.debug(self._outputs[name])
            shift = self._outputs[name].x

        cmd = ['xrandr']
        for name in self._outputs:
            cmd.extend(self._outputs[name].get_randr_options(primary == name))

        logging.debug("command to execute: \n%s", " ".join(cmd))
        subprocess.call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('outputs', nargs='*', help='name of the output')
    parser.add_argument('-a', '--panic', action='store_true', help='Turn on '
                        'all connected outputs')
    parser.add_argument('-p', '--primary', help='Set specified output as '
                        'primary')

    parser.add_argument('-v', '--verbose', help='Be verbose. Adding more "v" '
                        'will increase verbosity', action="count",
                        default=None)
    parser.add_argument('-q', '--quiet', help='Be quiet. Adding more "q" will '
                        'decrease verbosity', action="count", default=None)

    args = parser.parse_args()
    setup_logger(args)

    org = Organizer()

    if args.panic:
        org.panic(args.primary)
        return

    if args.outputs:
        org.set_outputs(args.outputs, args.primary)
        return

    # just display outputs
    org.output_list()


if __name__ == "__main__":
    main()
