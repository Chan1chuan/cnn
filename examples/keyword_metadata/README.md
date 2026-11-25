# Keyword metadata audit

Check keyword coverage in a speech manifest and estimate a speaker-disjoint
train/test split. The fixture is wholly synthetic: no audio, dataset export,
or real speaker information is included.

From this directory with Python 3 (standard library only):

```sh
python3 audit.py synthetic.tsv --keywords go stop left --seed example --test-percent 40
python3 -m unittest -v
```

The UTF-8 TSV requires the columns `speaker`, `utterance`, and `text` in that
order. IDs must be nonempty and utterance IDs unique. Matching is on whole
Unicode alphanumeric tokens after case folding. A row with one distinct keyword
counts once, even if the word is repeated; rows with several distinct keywords
are counted as ambiguous.

A seeded hash assigns each speaker, and therefore all their utterances, to one
split. The same seed and speaker ID give the same split regardless of row
order. The requested test percentage is approximate; small manifests can have
an empty split. The assignment does not enforce class balance. JSON output
contains only aggregate counts, not IDs or transcripts.
