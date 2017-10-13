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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', nargs='*', help='name of the output')
    args = parser.parse_args()

    org = Organizer()

    if not args.output:
        org.output_list()

if __name__ == "__main__":
    main()
