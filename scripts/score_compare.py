#!/usr/bin/env python3
"""Inventory/compare encoded MusicXML content without reducing pitches to MIDI.

Geometry and typography are ignored. Encoded structural differences are retained;
inspect exporter normalizations explicitly. This does not establish scan truth.
"""
import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

COSMETIC = {'default-x', 'default-y', 'relative-x', 'relative-y', 'font-family',
            'font-size', 'font-weight', 'font-style', 'color', 'id', 'xml:space'}


def read_xml(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            container = ET.fromstring(z.read('META-INF/container.xml'))
            rootfile = next(e for e in container.iter() if e.tag.split('}')[-1] == 'rootfile')
            root = ET.fromstring(z.read(rootfile.attrib['full-path']))
    else:
        root = ET.parse(path).getroot()
    for e in root.iter():
        e.tag = e.tag.split('}')[-1]
    if root.tag != 'score-partwise':
        raise ValueError('only score-partwise MusicXML is supported')
    return root


def canonical(element):
    if element is None:
        return None
    attrs = {k: v for k, v in sorted(element.attrib.items())
             if k not in COSMETIC and not k.startswith('font-')}
    return [element.tag, attrs, (element.text or '').strip(), [canonical(e) for e in element]]


def pitch_name(note):
    p = note.find('pitch')
    if p is None:
        return 'rest' if note.find('rest') is not None else 'unpitched'
    alteration = Fraction(p.findtext('alter', '0'))
    if alteration.denominator != 1:
        return f"{p.findtext('step')}({alteration}){p.findtext('octave')}"
    alter = int(alteration)
    return p.findtext('step') + ('#'*alter if alter >= 0 else 'b'*(-alter)) + p.findtext('octave')


def iter_notes(root):
    """Yield selectors, note elements and durations; preserve duplicate unisons."""
    for pi, part in enumerate(root.findall('part'), 1):
        divisions = 1
        for mi, measure in enumerate(part.findall('measure'), 1):
            pos = Fraction(0)
            onset = Fraction(0)
            members = Counter()
            for e in measure:
                if e.tag == 'attributes':
                    divisions = int(e.findtext('divisions', str(divisions)))
                    if divisions <= 0:
                        raise ValueError('divisions must be positive')
                elif e.tag in ('backup', 'forward'):
                    pos += (-1 if e.tag == 'backup' else 1)*Fraction(int(e.findtext('duration')), divisions)
                    if pos < 0:
                        raise ValueError(f'negative cursor at part {pi}, measure {mi}')
                elif e.tag == 'note':
                    duration = Fraction(int(e.findtext('duration', '0')), divisions)
                    if e.find('chord') is None:
                        onset = pos
                        pos += duration
                    voice, staff = e.findtext('voice', '1'), e.findtext('staff', '1')
                    key = (voice, staff, onset)
                    target = {'part': pi, 'measure': mi, 'voice': voice, 'staff': staff,
                              'onset': str(onset), 'member': members[key], 'expect_pitch': pitch_name(e)}
                    members[key] += 1
                    yield target, e, duration


def inventory(path):
    root = read_xml(path)
    events = []
    for target, note, duration in iter_notes(root):
        data = {**target, 'duration': str(duration), 'chord': note.find('chord') is not None,
                'visible': note.get('print-object', 'yes'), 'type': note.findtext('type'),
                'dots': len(note.findall('dot'))}
        for field in ('pitch', 'rest', 'unpitched', 'grace', 'cue', 'accidental', 'time-modification', 'stem'):
            data[field] = canonical(note.find(field))
        data['ties'] = sorted(e.get('type', '') for e in note.findall('tie'))
        data['beams'] = sorted((int(e.get('number', '1')), (e.text or '').strip()) for e in note.findall('beam'))
        data['notations'] = [canonical(e) for n in note.findall('notations') for e in n]
        data['lyrics'] = [canonical(e) for e in note.findall('lyric')]
        events.append(data)
    contexts = []
    for pi, part in enumerate(root.findall('part'), 1):
        div = 1
        for mi, measure in enumerate(part.findall('measure'), 1):
            pos = Fraction(0)
            for e in measure:
                if e.tag == 'attributes':
                    div = int(e.findtext('divisions', str(div)))
                    items = [canonical(c) for c in e if c.tag != 'divisions']
                    if items:
                        contexts.append({'part': pi, 'measure': mi, 'onset': str(pos), 'attributes': items})
                elif e.tag in ('direction', 'harmony', 'barline'):
                    # Position offsets are expressed in divisions; normalize them.
                    obj = ET.fromstring(ET.tostring(e))
                    off = obj.find('offset')
                    offset = Fraction(off.text)/div if off is not None else Fraction(0)
                    if off is not None:
                        obj.remove(off)
                    contexts.append({'part': pi, 'measure': mi, 'onset': str(pos+offset), e.tag: canonical(obj)})
                elif e.tag == 'note' and e.find('chord') is None:
                    pos += Fraction(int(e.findtext('duration', '0')), div)
                elif e.tag in ('backup', 'forward'):
                    pos += (-1 if e.tag == 'backup' else 1)*Fraction(int(e.findtext('duration')), div)
    return {'parts': len(root.findall('part')),
            'measures': [len(p.findall('measure')) for p in root.findall('part')],
            'events': events, 'contexts': contexts}


def compare(left, right):
    differences = []
    def walk(a, b, path):
        if type(a) != type(b):
            differences.append({'path': path, 'left': a, 'right': b})
        elif isinstance(a, dict):
            for key in sorted(set(a) | set(b)):
                walk(a.get(key), b.get(key), f'{path}/{key}')
        elif isinstance(a, (list, tuple)):
            if len(a) != len(b):
                differences.append({'path': path+'/length', 'left': len(a), 'right': len(b)})
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f'{path}/{i}')
        elif a != b:
            differences.append({'path': path, 'left': a, 'right': b})
    walk(left, right, '')
    return {'equal': not differences, 'difference_count': len(differences), 'differences': differences}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('left')
    p.add_argument('right', nargs='?')
    p.add_argument('--report')
    p.add_argument('--inventory', action='store_true')
    a = p.parse_args()
    left = inventory(a.left)
    if a.inventory:
        result = left
    elif a.right:
        result = compare(left, inventory(a.right))
    else:
        p.error('provide right input or --inventory')
    text = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    if a.report:
        Path(a.report).write_text(text)
        print(json.dumps({k: v for k, v in result.items() if k != 'differences'} if not a.inventory else {'events': len(left['events'])}))
    else:
        print(text, end='')
    raise SystemExit(0 if a.inventory or result['equal'] else 1)


if __name__ == '__main__':
    main()
