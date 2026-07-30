# Schemas

Ten JSON Schema 2020-12 **draft proposals** now define the first Pack, namespace, source, artifact, review, external publication decision, chunk, candidate-catalog, entity, and relation contracts. They compile and are exercised by adversarial fixtures, but they have **not been canonically adopted**.

The proposals are generated deterministically by `tools/build_schemas.py`. Regeneration must not change their bytes unless the generator changed.

Schema proposals must:

- fail closed for missing identity, rights, provenance, review, EDENA, integrity, or lifecycle information;
- keep risk tier, data class, action mode, evidence, review, and authority separate;
- distinguish public attribution from private intake records;
- bind reviews and publication decisions to exact candidate bytes;
- preserve localization and supersession lineage;
- make generated indexes reproducible from authorized Knowledge Packs;
- support quarantine, retirement, withdrawal, recall, and deletion from active retrieval.

A schema file becomes canonical only after explicit review, adversarial fixtures, validator tests, and a named human adoption decision.

Current automated validation proves structural, referential, screening, and integrity contracts only. It does not establish rights clearance, educational quality, clinical validity, institutional authorization, or publication approval.
