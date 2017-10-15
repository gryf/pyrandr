#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple xrandr wrapper for organising output layout
"""
import argparse
import subprocess
import re


DISPLAY_RE = re.compile(r'^(?P<output>[a-zA-Z0-9-]+)\s'
                        r'(?P<status>d?i?s?connected)\s'
                        r'(?P<is_primary>primary\s)?'
                        r'(?P<active>\d+x\d+\+\d+\+\d+\s)?'
                        r'.*')
RESOLUTION_RE = re.compile(r'^\s+(?P<width>\d+)x(?P<height>\d+)\s.*')


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
        if self.connected:
            return "%s %s %s (%dx%s)" % (self.name, connected, active,
                                         self.x, self.y)
        else:
            return "%s %s %s" % (self.name, connected, active)

    def get_randr_options(self):
        """Return options for xrandr command as a list"""
        if self.connected:
            return ['--output', self.name,
                    '--mode', "%dx%d" % (self.x, self.y),
                    '--pos', "%dx%d" % (self.shift_x, self.shift_y),
                    '--rotate', "normal"]
        else:
            return ['--output', self.name, '--off']


class Organizer(object):
    def __init__(self):
        self._outputs = {}
        self._get_outputs()

    def __repr__(self):
        return str(self._outputs)

    def _get_outputs(self):
        xrandr = subprocess.check_output(['xrandr'])

        in_output = False

        for line in xrandr.split('\n'):
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
        for name in sorted(self._outputs.keys()):
            print self._outputs[name]

    def set_single(self, out_name):
        pass

    def set(self, outputs, options):
        if len(outputs) == 1:
            self.set_single(outputs[0])
            return

        for name, out in self._outputs.items():
            if name not in outputs:
                out.active = False
            else:
                out.active = True

    def panic(self):
        """Just turn on all outputs at once in "mirror" mode"""
        cmd = ['xrandr']
        for name in self._outputs:
            out = self._outputs[name]
            cmd.extend(out.get_randr_options())

        subprocess.call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', nargs='*', help='name of the output')
    parser.add_argument('-p', '--panic', action='store_true', help='Turn on '
                        'all connected outputs')
    args = parser.parse_args()

    org = Organizer()

    if args.panic:
        org.panic()
        return

    if not args.output:
        org.output_list()
        return


if __name__ == "__main__":
    main()
