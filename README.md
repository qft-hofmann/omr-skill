# OMR transcription

An agent skill for transcribing printed or scanned music into accurate, editable ABC, then producing MusicXML and an engraved PDF for checking against the source.

```text
Source PDF or image → ABC → MusicXML → engraved PDF
                       ↑                    │
                       └── source review ───┘
```

**Accurate ABC is the target. The engraving's default purpose is user verification:** it helps both the agent and the user find transcription errors. The proof should preserve the source's musical information and visual relationships, including beam structure, stems, guitar fingerings and shared noteheads. Performance editions and arrangements require an explicitly different purpose.

This repository supplies agent instructions and small verification utilities. The agent reads the score visually; the Python scripts do not recognize notes from images or run an automatic PDF-to-score pipeline. No particular model or provider is required.

## Install

The repository root is the skill directory: keep `SKILL.md`, `references/` and `scripts/` together. Download or clone this repository into a directory named `omr-transcription`, then install it in your agent's skill directory.

For a Codex installation using `$CODEX_HOME/skills` (default `~/.codex/skills`), run this from the downloaded repository root:

```sh
skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/omr-transcription"
mkdir -p "$(dirname "$skill_dir")"
# Refuse to overwrite an existing installation.
if [ -e "$skill_dir" ]; then
  echo "Skill already exists: $skill_dir"
else
  mkdir "$skill_dir"
  cp SKILL.md "$skill_dir/"
  cp -R references scripts agents "$skill_dir/"
  cp README.md LICENSE "$skill_dir/"
fi
```

Start a new agent session after installation. For another skill-capable agent, use its installation convention with the same directory contents. `agents/openai.yaml` is optional Codex UI metadata; the workflow itself is in [SKILL.md](SKILL.md).

## Use

Example request:

> Use $omr-transcription to transcribe `score.pdf` to ABC, convert it to MusicXML, and engrave a PDF for user verification. Preserve source beams, stems, fingerings and lyrics. Deliver the build recipe, any required annotations, and a record of uncertain passages.

The agent needs image-viewing and file-execution tools, plus:

| Task | Requirement |
| --- | --- |
| Run the supplied helpers and tests | Python 3.10 or newer; standard library only |
| Inspect a PDF | A PDF-to-image renderer, such as Poppler, and visual access to the rendered pages |
| Convert ABC to MusicXML | An available converter, such as `abc2xml.py` |
| Engrave MusicXML | A notation editor or renderer, such as MuseScore |

Converters, PDF renderers and notation editors are **not bundled**. Their installation and command names depend on the environment. Record their versions and the exact commands used for each transcription. Test a passage containing the score's difficult notation before choosing a conversion route.

## Workflow and deliverables

1. Inventory the source pages and editions. Usually inspect a whole system first, then measures and difficult details; choose a view that retains enough context for clefs, accidentals and voices.
2. Transcribe into ABC, preserving spelling, rhythm, voices, ties, lyrics and source notation. Keep user-checked corrections and uncertainty visible.
3. Convert to MusicXML. Apply guarded supplementary annotations for notation the chosen ABC conversion cannot carry.
4. Engrave a proof and review every measure against the source, checking all chord tones and voices. Track pitch/rhythm coverage separately from notation/text coverage.
5. Correct the ABC or its consumed annotations, rebuild, and inspect every final PDF page.

Deliver the ABC, MusicXML and engraved PDF together with the build recipe, required annotation files and a brief review record. Generated files must be reconstructible from the master and recipe. A change made only in a notation editor is not a completed correction.

For guitar, two stems sharing one notehead can describe two written voice roles but one physical pluck. Standard ABC does not portably encode that identity. Preserve both roles and record the source-established relationship in consumed annotations; do not automatically merge equal pitches. The included annotation helper can set stems and hollow noteheads, but shared-attack playback and some barre-bracket placements require a documented editor-specific adapter. No such adapter is bundled.

See [pitch review](references/pitch-review.md) and the [conversion and preservation contract](references/conversion-and-preservation.md) for the detailed rules and annotation schema.

## Helper commands

Run these from the repository root. Input names below stand for files from your transcription.

### Inspect manually measured staff geometry

```sh
python scripts/staff_position.py \
  --lines 100 110 120 130 140 --head 120 --clef treble \
  --measurement-error 1
```

This example yields written diatonic `B4`. Supply five local staff-line y coordinates from top to bottom and the notehead-center y coordinate, measured at the same horizontal position. The JSON includes rounding and geometry diagnostics. It does not detect noteheads or determine accidentals, transposition or voice membership.

### Inventory or compare MusicXML

```sh
python scripts/score_compare.py score.musicxml --inventory --report inventory.json
python scripts/score_compare.py before.musicxml after.musicxml --report comparison.json
```

The reader accepts `score-partwise` MusicXML, including compressed `.mxl`. It retains encoded voice, spelled pitch, duration, beam and notation differences while ignoring selected geometric and font attributes. Inventory mode exits successfully; comparison exits with `0` for equality and `1` for differences. Read the JSON report before interpreting a difference as an error: exporters may renumber voices or encode the same visible notation differently.

This is an encoded-content comparison, not a complete MusicXML validator or an engraving/playback comparison. It does not inventory every XML field; for example, notehead appearance still needs targeted and visual checks.

### Apply guarded annotations

```sh
python scripts/apply_annotations.py converted.musicxml annotations.json score.musicxml
```

Use the [documented JSON schema](references/conversion-and-preservation.md#annotation-schema). Note selectors include document part/measure ordinals, voice, staff, onset, chord member and expected pitch. The helper rejects mismatched attachments and musical overrides such as pitch or duration changes; make those changes in ABC. Always retain the fresh converter output and write annotations to a different output file.

## Verification limits

Successful conversion, matching MIDI, a clean round trip or agreement between models does not prove that the source was read correctly. Inspect the original image and the final engraving. Distinguish source-reading mistakes, conversion losses, engraving differences and unresolved ambiguity.

Benchmark references can themselves be wrong, including their stem directions. Treat reference agreement as provisional until the relevant source notation has been checked. If a reference is corrected, retain the original predictions and results and rescore separately with unchanged evaluation rules. This package makes no numerical accuracy claim and includes no benchmark scores, scans or model transcripts.

## Development

```sh
python -m unittest discover -s tests -v
python scripts/staff_position.py --help
python scripts/score_compare.py --help
python scripts/apply_annotations.py --help
```

The tests use small synthetic examples and cover staff geometry, spelling, secondary beams, notation attachments, annotation guards and duration normalization. They test the helper code, not an agent's ability to read a scan. GitHub Actions runs them on Python 3.10, 3.12 and 3.13.

For changes to transcription behavior, include a minimal example, the expected source reading and the effect on the ABC-to-proof workflow. Use material you can share; keep large scores, generated artifacts and private benchmark data outside this repository. New preservation features should include a focused test where practical and an explicit account of any remaining visual checks.

```text
SKILL.md                       Agent workflow and constraints
agents/openai.yaml             Optional Codex UI metadata
references/                    Pitch review and preservation guidance
scripts/                       Standard-library Python helpers
tests/                         Synthetic regression tests
.github/workflows/tests.yml    Continuous integration
```

## License

The skill documentation, helper scripts and tests are licensed under the [MIT License](LICENSE). External converters and renderers retain their own licenses. This license does not grant rights to scores supplied for transcription or to third-party material.
