---
type: application-bundle/domain-map
title: Domain map — graph and semantic-layer vocabulary
description: The vocabulary of the published graph and its Semantica-based semantic layer in Knowledge
  Foundation core, what each term means and where it lives in code.
generated:
  by: process:building-application-bundles@0.1.0
  at: '2026-10-20T19:30:00-05:00'
sources:
- id: repo
  kind: source-repo
  repo: muthub-ai/knowledge-foundation
  commit_sha: 78d41952391c91356afbebfaee129b8b40a12561
- id: graph
  kind: code-graph
  path: code-graph/code-graph.jsonl
  sha256: 881e9bd0100d27591d42a861bc0797c5ae5cb88f764837f511242482b5d82a7d
x_kf:
  schema: kf-application-bundle/1
  appid: kfcor
  bundle_kind: application
  domain: graph-semantic-layer
  bootstrap: true
---
# Domain map — graph and semantic-layer vocabulary

## Graph terms

| Term | Meaning | Where it lives |
|---|---|---|
| Backbone | the deterministic part of the graph: theme, note and source nodes with folder, link, source and frontmatter-relation edges, built without any model call | `graph.build` [^graph-doc] [^g-build] |
| Edge origin | where an edge came from: `frontmatter`, `folder`, `link`, `source` or `extracted` | `schemas/graph.schema.json` [^schema-origin] |
| Typed relation | one of ten curator-written frontmatter types such as `builds_on`, `refines`, `contradicts` or `supersedes`; it replaces an untyped link between the same notes | `ontology/edge-types.yaml`, `graph.build.edge` [^edge-types] [^graph-edge] |
| Derived edge types | `links_to`, `in_folder`, `draws_on` and `mentions`, produced by the builder rather than written by a curator | `ontology/edge-types.yaml` [^edge-types] |
| `ext:` node | an entity found by an extractor that matches no note title or alias, with id `ext:<slug>` and trust `machine-confirmed` | `graph.build` [^graph-ext] |
| `graph.json` | the only contract with the site, with precomputed positions and Louvain communities so the browser only draws | `schemas/graph.schema.json`, `graph.write_outputs` [^schema-doc] [^g-write] |

## Semantic-layer terms

| Term | Meaning | Where it lives |
|---|---|---|
| Extractor | anything implementing `extract(notes) -> Extraction`; `semantica` and `none` are registered | `extractors/__init__.py` [^ext-proto] [^ext-get] |
| `ExtractorUnavailable` | raised when the library or credentials are missing; the build then publishes the deterministic graph and says so in the report | `extractors/__init__.py`, `graph.build` [^ext-unavail] [^graph-ext] |
| Entity types | the five types Concept, Standard, Tool, Organization and Practice; people, places, dates and amounts are dropped | `semantica_adapter.py` [^ent-types] |
| Kept entity | an entity mentioned in two or more notes, an acronym, or a capitalised standard, tool or organisation | `semantica_adapter._keep` [^keep] [^g-keep] |
| Entity resolution | spelling and plural folding, Semantica's fuzzy resolver, an acronym rule and an optional checked model pass; merged names become aliases | `resolution.resolve` [^res-doc] [^g-resolve] |
| Acronym rule | an all-capitals label merges with a long form whose significant words spell it, never with a longer phrase that merely contains it | `resolution.acronym_pairs` [^res-acronym] |
| Note relation | a model-proposed typed relation between two notes, with verbatim evidence and a confidence | `NoteRelation`, `relations.extract_note_relations` [^ext-noterel] [^g-extract-rel] |
| Candidate notes | for each note, up to eight other notes sharing the most resolved entities, excluding pairs the author already linked | `relations.candidates` [^rel-cands] |
| Evidence check | a proposal survives only with an allowed type, an offered target, the quote found verbatim in the note after Markdown is stripped, and confidence of at least 0.7 | `relations.evidence_in`, `relations.extract_note_relations` [^rel-consts] [^rel-filter] |
| Promotion | `kb propose` copies chosen `extracted` relations into note frontmatter on a branch, never touching `verified` | `governance.propose` [^gov-propose] |
| Canary | the non-required `tests.yml` matrix that runs the real library per method and fails if Semantica did not actually run | `tests.yml` `semantica-canary` [^canary] |

*Assessment:* The vocabulary draws a hard line between what an author wrote (typed relations, links) and what a model found (`ext:` nodes, `extracted` edges), and that line is enforced in the builder, not just labelled for the site.[^graph-edge] [^graph-ext] [^schema-origin]

[^graph-doc]: src · tools/kb/graph.py#L1-L8 · sha256:964b834e717b2d35347caa900fd1709266066480b374675651f45aa3a0e7c67d
[^g-build]: graph · tools/kb/graph.py::build
[^schema-origin]: src · schemas/graph.schema.json#L188-L197 · sha256:7b723739aa6e90b465c3b1150caac170f148606adc6e0198f60cf33cf1c3cac2
[^edge-types]: src · ontology/edge-types.yaml#L1-L17 · sha256:dba7bc6f754b2446e68a0b747f999d6672a5c96cef6cba5f39b07d8f5c9945bb
[^graph-edge]: src · tools/kb/graph.py#L91-L126 · sha256:2e388555783d6803a35a397ed636ae5002f2a24465980b61c484879c6c76d187
[^graph-ext]: src · tools/kb/graph.py#L128-L161 · sha256:7209d16518d7c68ff6f3eed76c6e3aa0b050c52e9bc59555fb6a450cb2024c71
[^schema-doc]: src · schemas/graph.schema.json#L1-L5 · sha256:37020d62468eebe60bdb900fcf137ca38c6d60c0fb0dd51ac63c864c66604658
[^g-write]: graph · tools/kb/graph.py::write_outputs
[^ext-proto]: src · tools/kb/extractors/__init__.py#L60-L63 · sha256:d9ffd7feacbce97ee1a56d3ab39590c1caa168b62413125284e17c964f63afde
[^ext-get]: src · tools/kb/extractors/__init__.py#L66-L75 · sha256:9b932ae05adfd838a7077817c65b2a7aa4c1beb4f9eb5d04c3f951ab84b32769
[^ext-unavail]: src · tools/kb/extractors/__init__.py#L13-L14 · sha256:576ebc9498d458cd06886ee86fc19f1e722ecfbdaf59ecb8f3923049be76ad00
[^ent-types]: src · tools/kb/extractors/semantica_adapter.py#L30-L45 · sha256:90da60cae1de3ba6173af5311046f288680a5dae7808a3792945f95893031934
[^keep]: src · tools/kb/extractors/semantica_adapter.py#L97-L102 · sha256:bd4acf99a6cbf8d4eda7da6df28575b00a52bdaa42631c635435711d69ff4459
[^g-keep]: graph · tools/kb/extractors/semantica_adapter.py::_keep
[^res-doc]: src · tools/kb/extractors/resolution.py#L1-L13 · sha256:cd7dc9e087d4c36cd63d826e75f0ca5a48c4a56628a7c282c63a4f5ddc9bed5b
[^g-resolve]: graph · tools/kb/extractors/resolution.py::resolve
[^res-acronym]: src · tools/kb/extractors/resolution.py#L58-L69 · sha256:097fc3c9d39ec170316453b5619ba523fa133ab7e72aba5e5eeea4f4cb4d659d
[^ext-noterel]: src · tools/kb/extractors/__init__.py#L41-L48 · sha256:9459500bdcc40b5a5fe5fd9dbd20d5b6ee6fff187f0d4392235f5531c7a4ad4d
[^g-extract-rel]: graph · tools/kb/extractors/relations.py::extract_note_relations
[^rel-cands]: src · tools/kb/extractors/relations.py#L56-L71 · sha256:1795ec3577a4d20979a656d26ef336a70ded896816064da87eddcce58ac68a1d
[^rel-consts]: src · tools/kb/extractors/relations.py#L36-L53 · sha256:e3d962d7ae572d8f5fc11395ee37fb16946d2741ff7cab56931480bb026e18eb
[^rel-filter]: src · tools/kb/extractors/relations.py#L139-L149 · sha256:aea4442722aae7c54a138314d3217f10c849b02f80b39c4c61d25253a11a7234
[^gov-propose]: src · tools/kb/governance.py#L74-L95 · sha256:e23a0d66865e0125ecc96ea1c9e581e08bec30c2eddba807ace6cf11cb6d37e1
[^canary]: src · .github/workflows/tests.yml#L96-L111 · sha256:061933095538ba480f3777574d533e6a10a782cf0e56bb7b45034a784483ccc5
