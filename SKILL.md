---
name: omr-transcription
description: Transcribe printed or scanned musical notation, usually PDF pages, into source-faithful editable ABC, MusicXML, and an engraved proof. Use for visual OMR and source-to-score correction; not for audio transcription.
---

# Visual music transcription

The objective is an accurate, editable **ABC transcription of the supplied notation**. The normal pipeline is source image/PDF → ABC → MusicXML → engraved PDF. ABC is the musical master; keep it, the conversion recipe and any unavoidable annotations needed to reconstruct the delivered MusicXML. Respect a different format or scope when the user explicitly requests it. Preserve the source input and the user's checked corrections.

## Decide the engraving's purpose

Infer the purpose from the request. If none is specified, use **user verification**: provide an engraved proof that makes the ABC easy for both user and agent to check against the source. Retain the original's information and, when practical, recognizable system/bar layout and visual relationships. An explicitly requested performance edition, teaching score or arrangement can have different layout or musical requirements; do not silently substitute one purpose for another. If the choice materially changes the result and cannot be inferred, ask.

## Transcribe

1. Inventory pages and editions. Render every relevant source page at sufficient resolution and inspect the music visually; include text-only pages where requested. Identify instrument roles, clefs, octave signs, key and time signatures, pickups, repeats, voices and layout. Keep distinct arrangements, editions and user-approved corrections separate; an external rendition is not an authority over the supplied scan.
2. As a default, inspect a complete system first, then transcribe its measures in traceable order, retaining source page/system/measure identifiers. Choose a larger or smaller view when it is more useful: keep neighboring notation visible when needed for clefs, key and carried accidentals, ties, beams or voices crossing measure or system boundaries; enlarge difficult details without losing their context. This is a guideline, not a fixed crop size or a requirement for a separate model call per measure.
3. Establish clef, key, octave/transposition and accidental context before reading individual notes. In ABC preserve pitches and spelling, simultaneous and sustained voices, rests, timing, ties/slurs, key changes, explicit accidentals, lyrics and expressive marks. Preserve source beam groups, including secondary breaks and hook directions; durations alone do not determine them. For guitar preserve printed fingering numbers, string/position/tuning signs and their note attachments. Preserve other instrument-specific marks as relevant. Distinguish printed notation, handwritten annotations and user-approved corrections; do not silently treat an annotation as the printed reading.
4. Keep ordinary musical content in ABC. For information the chosen ABC/conversion route cannot preserve, use annotations that the build actually consumes, with unambiguous musical attachment points and expected-value guards. Read [conversion-and-preservation.md](references/conversion-and-preservation.md) when choosing the build recipe, adding annotations or checking exports. Identify anything a generic ABC renderer cannot reproduce. If a scan is ambiguous, retain the alternatives and evidence; never substitute musical plausibility for the visible mark.

## Build a proof and correct the master

Use the loop **source → draft ABC → MusicXML → proof → source review → master correction → rebuild**. Build an early proof when useful, for example after a system, rather than waiting for a supposedly checked full transcription. Changes to pitches, rhythm or voice membership go back into ABC; supplementary notation corrections go into consumed annotations. Do not leave a correction only in exported MusicXML or a native editor file. Regenerate deliverables from the master and the recorded recipe.

## Verify the transcription against the source

Read [pitch-review.md](references/pitch-review.md). Source checking applies regardless of the engraving's eventual purpose. Review every measure, including each chord tone and simultaneous/sustained voice, and account for every musical marking. Keep compact coverage records by measure or system for (a) pitches/rhythm and (b) notation/text, marked reviewed, uncertain or unreviewed; detailed note evidence is needed for problems, not every easy note. A review record describes work done, not a guarantee of correctness.

Choose source/proof comparison or a fresh source-only reading according to the passage; do not assume that either method is more reliable. Use a different view or method when it adds evidence. Inspect objectively difficult passages (ledger lines, dense chords, conflicting voices, damaged or overwritten symbols) even when the first reading seems confident. Neither a fresh session nor model agreement certifies source truth. Do not require a particular model or silently spend on a more expensive one.

Use `scripts/staff_position.py` when a locally measured notehead position is difficult: supply the five local staff-line y coordinates and the notehead center. It computes a *written diatonic* position; it does not detect the notehead, decide accidentals, resolve notation or establish source truth. Inspect and retain the underlying crop and measurements. Use the reference for the exact arithmetic and limitations.

## Convert and deliver

Compare semantic event timelines by part, staff, voice, onset, duration and spelled pitch, accounting explicitly for written versus sounding octave, ties, chords, pickups and shared unisons. Separately check printed accidentals, every beam level/hook, fingerings and attachments, key/clef/time, lyrics and other source details. Use `scripts/score_compare.py` for inspectable XML inventories/differences; it reports encoded differences, not source correctness. Document necessary mappings (such as voice renumbering) rather than globally ignoring those fields. A round trip, plausible duration, MIDI playback, or agreement with another file derived from the same reading is **not** evidence that the scan was read correctly.

Import into an available notation editor, re-export if useful, and inspect every final PDF page against the scan. Inspect fingering placement, accidentals, beams and lyrics; verify guitar octave and tuning in native score/playback when relevant. Preserve the separate lyrics/text page if requested or part of the source. Recheck affected source measures after corrections, including dependent passages when clef/key/accidental context or a cross-bar connection changes. Repeat structural/import checks after rebuilding. Keep transformations for a requested arrangement distinct from corrections to the source transcription.

Deliver the requested editable ABC, MusicXML and engraving with a short note stating the source review, conversion checks, engraving purpose and unresolved or omitted information. Do not claim independent or human verification unless it occurred.
