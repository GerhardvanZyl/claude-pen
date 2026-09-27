# Review lanes — Unity

One card per lane. A reviewer reads **only its own card** — never the whole
file — plus the slice context the lead provides.

The point of these cards is that every concern has exactly one owner. If a lane
finds something owned by another lane, it does not raise it. Duplicate findings
across lanes cost the lead triage time and inflate the round's finding count,
which makes the termination condition harder to reach.

Each card has three parts:

- **Owns** — raise these.
- **Does not own** — you will notice some of these. Say nothing; another lane has
  them.
- **Quality brake** — the specific way this lane goes wrong. Read it twice.

---

## Unity

- **Owns:** serialized data loss (renamed/moved `[SerializeField]` or public
  field without `[FormerlySerializedAs]`, changed type of a serialized field);
  asset-database integrity (missing `.meta`, GUID changed on move, orphaned
  `.meta`); broken fileID/GUID references in `.unity`/`.prefab`/`.asset` YAML;
  `.asmdef` references and platform constraints; lifecycle-order dependence
  (`Awake`/`OnEnable`/`Start`, script execution order); Unity API calls off the
  main thread; per-frame allocations and `Find`/`GetComponent` in
  `Update`/`FixedUpdate`/`LateUpdate`; `UnityEditor` APIs in runtime assemblies;
  `== null` misuse on destroyed `UnityEngine.Object`s.
- **Does not own:** general logic defects (technical / correctness), naming
  (standards), visual result (visual), package manifests and CI (artifacts).
- **Quality brake:** a per-frame allocation is only a finding if the code runs
  every frame in a shipping path — not in an editor tool, a one-off `Start`, or
  a greybox placeholder script. Serialized-field findings must name the asset
  that would lose data, or be marked `low`.

## Visual

- **Owns:** a brief element missing or wrong in a shot; scale contradicting the
  brief; a shot whose framing does not show what the brief says it must;
  lighting or palette contradicting stated intent; a shot that failed to
  communicate its purpose (e.g. key object occluded, unlit, off-frame).
- **Does not own:** code, assets' internal structure, anything not visible in
  the PNGs.
- **Quality brake:** every finding quotes the brief line it violates. "Would
  look better", taste, and polish beyond greybox fidelity are not findings. A
  brief that never stated the thing you want is a finding against the brief,
  not the shot.
