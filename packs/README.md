# Knowledge Pack distribution

No Knowledge Packs are published in this repository.

The English `AI Literacy Foundations for Nurses` Pack exists only as `v0.1.0-draft.1`, an AI-assisted D0/Green review candidate. It is not independently reviewed, accepted, published, certified, clinically validated, institutionally authorized, or approved for translation. It is excluded from the public catalog.

Future accepted packs will be distributed as exact versioned release assets with manifests, checksums, rights records, review scope, limitations, and lifecycle state. Published bytes at one version/digest identity must not be overwritten; corrections create a new version.

A download, opening action, or extraction will not install, authorize, or activate a pack. Active content requires an approved sandbox. Quarantine, rights removal, privacy response, withdrawal, and recall must remain possible.

The initial public ceiling is D0, Green, and bounded Yellow. Do not place PHI, confidential institutional material, patient-specific tools, credentials, or secrets here.

Local derivative builds use `tools/build_pack.py`. Each authoritative artifact declares a durable `content_unit_id`; generated chunk IDs remain disposable and citations resolve to the declared source unit. Candidate catalog, chunk, graph, shard-lock, and SQLite/FTS5 artifacts remain rebuildable and do not become authoritative merely because the build succeeds.
