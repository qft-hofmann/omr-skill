# Build and preservation contract

ABC owns notes, rests, rhythm, voices and other features the selected converter supports. Supplementary annotations own explicitly documented unsupported notation. Generated XML/native/PDF files are reproducible products, not separate musical masters. Keep inputs immutable and save converter versions, commands and source/crop mappings.

## A practical recipe

1. Locate an available ABC-to-MusicXML converter (for example `abc2xml.py`); record its version and options. Try a small passage containing the score's fragile features before converting the entire piece. An installed music-transcription skill or project vendor directory may supply the converter; this skill assumes no personal absolute path.
2. Convert to a fresh intermediate file. Apply consumed source-derived annotations to a new output file, then import into the notation editor. `scripts/apply_annotations.py input.xml annotations.json output.musicxml` supplies guarded note/measure annotations. A score-specific build script is also acceptable if it consumes the annotations and fails on ambiguous attachments.
3. Export and inspect the proof. A Linux MuseScore example is `env -u DISPLAY -u WAYLAND_DISPLAY APPIMAGE_EXTRACT_AND_RUN=1 QT_QPA_PLATFORM=offscreen MU_QT_QPA_PLATFORM=offscreen musescore4 -o proof.pdf score.musicxml`.
4. Compare exports with `python scripts/score_compare.py before.musicxml after.musicxml --report comparison.json`. `--inventory` writes a single-input inventory. The script reports encoded differences; it cannot certify ABC parsing, source reading, rendering, tuning or playability. Document normalizations for known exporter behavior and retain the raw report. Never discard all voices, spelling, rests, ties or secondary beams to obtain a pass.
5. Correct ABC/annotations, rebuild from fresh intermediate files and recheck affected source contexts. Deliver the recipe and required annotation files with the master.

Do not reverse-convert XML to ABC during a blind visual-OMR test. Reference preparation from supplied XML is a separate task.

## Annotation schema

Version 1 has `notes` and `measures` arrays. Part and measure selectors are **one-based document ordinals**, including pickups, independent of printed numbers. Note selectors use encoded voice, staff, onset in quarter-note units, and a zero-based member of the simultaneous group in that voice. An expected XML pitch (`C#4`, `Db4`, `F##5`) or `rest` guards the attachment. These strings use encoded XML octaves, not an assumed sounding/display convention. A pitch change requires revisiting its annotation. Selectors must resolve uniquely.

```json
{
  "version": 1,
  "notes": [{
    "target": {"part": 2, "measure": 3, "voice": "1", "staff": "1", "onset": "1/2", "member": 0, "expect_pitch": "C5"},
    "replace": {
      "beam": ["<beam number=\"1\">continue</beam>", "<beam number=\"2\">backward hook</beam>"],
      "notations/technical/fingering": ["<fingering>3</fingering>"]
    }
  }],
  "measures": [{
    "target": {"part": 1, "measure": 5},
    "replace": {"print": ["<print new-system=\"yes\"/>"]}
  }]
}
```

Replacement sets the complete selected field, including an empty array to remove it. Other fields remain. The helper permits notation/layout fields, not pitches, durations, voices, backups or keys. It rejects same input/output paths, duplicate replacements, invalid selectors and malformed annotation XML before writing. Applying annotations must not accumulate beams or fingerings. For unsupported features use a documented guarded extension, not silent omission.

## What to compare

- **Events:** part/staff/voice, onset, duration, rests (including visible versus invisible), spelled pitch, chord membership, grace notes and ties. A shared notehead can represent distinct voice events. Equal MIDI numbers do not establish identical notation.
- **Notation:** printed/cautionary accidentals; every beam level and hook direction; fingerings, string/fret/position attachments; slurs, articulations, tuplets, lyrics and directions. Avoid automatic rebeaming as a substitute for reading the source.
- **Context:** clef, key, meter, transposition, repeats/endings, tuning and source layout. Check rendered and sounding guitar octaves: neither an instrument name nor a clef symbol alone establishes a particular file's pitch convention.

For shared guitar noteheads, trace both stems all the way to their beam or flag. A beam-connected eighth and a downstem quarter can share one head: retain both voice events and their different durations. Do not remove one as a duplicate merely because the pitches and attacks coincide. Distinguish **written voice roles** from **physical sounding events**: when source evidence or user adjudication establishes a single plucked string, explicitly link those roles as one attack with the sustained duration. Preserve this identity in consumed, guarded annotations (structured ABC comments are one option), and carry it through conversion, engraving and playback. Standard ABC alone does not portably express this relationship. Never coalesce all equal-pitch simultaneous notes: true unisons may be separate strings or performers. Score written roles, physical identity and printed appearance separately, allowing documented representation equivalences without overlooking lost notation.

For an unequal-duration shared hollow head, MusicXML `notehead filled="no"` can preserve the half-note appearance of a beam-connected eighth; inspect the imported proof. If native playback duplicates the attack, suppress only the explicitly declared alias while retaining the sustained owner. Verify the resulting attack count and sustain, not merely the MIDI pitch set. Preserve guitar barre brackets and their chord attachments even when no fret number is printed; do not invent a number or encode the bracket as an arpeggiation sign. Converter/editor-specific placement or playback adapters must be reproducible and reject target drift.

Conversely, an invisible padding event must not become an added sounding note. Inspect visible pickup rests individually before hiding secondary-voice rests. Check fermata orientation explicitly when voice ordering differs from stem direction.

`score_compare.py` reports encoded structural differences, including note types, directions and explicit context changes, while ignoring purely geometric/font attributes. It preserves duplicate events and spelling. Exporters may renumber voices or materialize defaults; inspect/document those cases. Full ornament semantics, playback, page layout and arbitrary XML extensions still need targeted/rendered review.

If an editor renders a source detail correctly but exports it incorrectly, retain the faithful master-derived MusicXML, the raw export/difference report and visual evidence of the affected feature. Do not change the reference to match an exporter defect or report a clean round trip. Beam elements can be attached to only one member of a chord on export: compare beam topology per stem/attack as well as raw per-note encoding, preserving each level and hook direction. Invisible padding rests within a beam are different from added visible notes/rests.

## Workflow evaluation

Keep hidden references separate from the test agent's source images and skill/tools. Freeze source/reference hashes before evaluation. Original scans test scan transcription; rasterized arrangement engravings test clean-score transcription and must be labelled accordingly. Preserve first-draft and reviewed ABC, build outputs, review notes and observed tool use. Distinguish reading mistakes, conversion failures, notation losses and uncertainty. Score final event/notation content and correction effort, not just a same/different verdict. References are provisional until their particular source/edition has been reviewed.

Adjudicate discrepancies against the image rather than assuming the reference wins. If the reference is wrong, preserve the frozen version and initial results, record source evidence and the correction, and publish the rescored result separately. A candidate can expose a reference error without becoming the authority for the correction. Distinguish harmless local voice-number choices and duplicate chord-level notation tags from visible or sounding differences.
