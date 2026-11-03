#!/usr/bin/env python3
"""Apply guarded source-derived notation to a fresh MusicXML conversion."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from score_compare import read_xml, iter_notes

NOTE_FIELDS = {'accidental', 'stem', 'notehead', 'beam', 'notations/technical/fingering',
               'notations/technical/string', 'notations/technical/fret',
               'notations/technical/pluck', 'notations/slur', 'notations/slide',
               'notations/fermata', 'notations/articulations', 'notations/ornaments'}
MEASURE_FIELDS = {'print', 'direction', 'harmony', 'barline'}
ORDER = ['grace','cue','chord','pitch','unpitched','rest','duration','tie','instrument',
         'footnote','level','voice','type','dot','accidental','time-modification',
         'stem','notehead','notehead-text','staff','beam','notations','lyric','play','listen']


def apply(root, annotations):
    if annotations.get('version') != 1:
        raise ValueError('expected annotation schema version 1')
    if set(annotations)-{'version','notes','measures','description'}:
        raise ValueError('unknown annotation fields')
    notes = list(iter_notes(root))
    touched = set()
    for kind in ('notes', 'measures'):
        for annotation in annotations.get(kind, []):
            target = annotation['target']
            if kind == 'notes':
                required = {'part','measure','voice','staff','onset','member','expect_pitch'}
                if set(target) != required:
                    raise ValueError(f'note target must contain exactly {sorted(required)}')
                matches = [n for t, n, d in notes if t == target]
                allowed = NOTE_FIELDS
            else:
                if set(target) != {'part','measure'}:
                    raise ValueError('measure target requires part and measure')
                pi, mi = target['part'], target['measure']
                parts = root.findall('part')
                matches = [] if pi < 1 or pi > len(parts) else parts[pi-1].findall('measure')[mi-1:mi] if mi >= 1 else []
                allowed = MEASURE_FIELDS
            if len(matches) != 1:
                raise ValueError(f'expected exactly one attachment for {target}, found {len(matches)}')
            node = matches[0]
            for path, snippets in annotation['replace'].items():
                if path not in allowed:
                    raise ValueError(f'field {path} must be encoded in ABC or a documented separate extension')
                key = (id(node), path)
                if key in touched:
                    raise ValueError(f'duplicate replacement {target}: {path}')
                touched.add(key)
                parent = node
                bits = path.split('/')
                for bit in bits[:-1]:
                    found = parent.findall(bit)
                    if len(found) > 1:
                        raise ValueError(f'ambiguous parent {bit}')
                    parent = found[0] if found else ET.SubElement(parent, bit)
                tag = bits[-1]
                new = [ET.fromstring(s) for s in snippets]
                if any(e.tag != tag for e in new):
                    raise ValueError(f'replacement tag must be {tag}')
                old = parent.findall(tag)
                insertion = min((list(parent).index(e) for e in old), default=len(parent))
                if kind == 'measures' and not old:
                    if tag == 'print':
                        insertion = 0
                    elif tag in ('direction', 'harmony'):
                        insertion = next((i for i,e in enumerate(parent) if e.tag == 'note'), len(parent))
                for e in old:
                    parent.remove(e)
                for e in reversed(new):
                    parent.insert(insertion, e)
            if kind == 'notes':
                node[:] = sorted(node, key=lambda e: ORDER.index(e.tag) if e.tag in ORDER else len(ORDER))
    return root


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source');p.add_argument('annotations');p.add_argument('output')
    a = p.parse_args()
    if Path(a.source).resolve() == Path(a.output).resolve():
        p.error('write to a separate output, preserving the fresh conversion')
    root = apply(read_xml(a.source), json.loads(Path(a.annotations).read_text()))
    ET.indent(root)
    ET.ElementTree(root).write(a.output, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    main()
