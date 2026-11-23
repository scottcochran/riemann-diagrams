/-
Deps.lean: the direct dependencies of every declaration in compiled Lean modules, read from the .olean files
alone, without importing anything they import.

For the parts of one module on the command line, prints one JSON line per constant each part
holds: its name, its kind, the file it came from, the constants its type references (`type`), and those its
value references (`value`: a theorem's proof, a definition's body). Nothing is elaborated or checked; this reads
what the compiler wrote.

Run with the toolchain the files were built with, which must match exactly, once per module:
  deps A.olean A.olean.server A.olean.private > A.jsonl   (run-deps.sh does this for a tree)
-/
import Lean
open Lean

def kind : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "def"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quot"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "ctor"
  | .recInfo _ => "recursor"

/-- The constants an expression mentions, by an explicit worklist over its DAG: Lean's own
`Expr.getUsedConstants` recurses as deep as the term, and some proofs here are deep enough to overflow the
stack. Each shared subterm is visited once, by pointer. -/
unsafe def constsImpl (roots : Array Expr) : NameSet := Id.run do
  let mut seen : PtrSet Expr := mkPtrSet
  let mut todo := roots
  let mut out : NameSet := {}
  while h : todo.size > 0 do
    let e := todo.back
    todo := todo.pop
    if seen.contains e then continue
    seen := seen.insert e
    match e with
    | .const n _ => out := out.insert n
    | .app f a => todo := todo.push f |>.push a
    | .lam _ t b _ | .forallE _ t b _ => todo := todo.push t |>.push b
    | .letE _ t v b _ => todo := todo.push t |>.push v |>.push b
    | .mdata _ b => todo := todo.push b
    | .proj s _ b => out := out.insert s; todo := todo.push b
    | _ => pure ()
  return out

@[implemented_by constsImpl] opaque consts (roots : Array Expr) : NameSet

def sorted (s : NameSet) (self : Name) : Array Name :=
  (s.erase self).toArray.qsort Name.lt

/-- What the statement mentions, and what the value mentions: a theorem's proof, a definition's body. The
blueprint distinguishes a statement's uses from its proof's, so the two are kept apart. -/
def uses (ci : ConstantInfo) : Array Name × Array Name :=
  let v := match ci.value? (allowOpaque := true) with
    | some v => sorted (consts #[v]) ci.name
    | none => #[]
  (sorted (consts #[ci.type]) ci.name, v)

/-- The arguments are the parts of one module in the order Lean writes them (.olean, .olean.server,
.olean.private). A later part shares objects with the earlier ones, so the parts are read together by
`readModuleDataParts`; reading one alone with `readModuleData` follows pointers into regions not mapped. The
regions are never freed: the process is short-lived. -/
def main (args : List String) : IO UInt32 := do
  let paths := args.toArray.map System.FilePath.mk
  let parts ← readModuleDataParts paths
  let out ← IO.getStdout
  for (path, (data, _)) in paths.zip parts do
    for ci in data.constants do
      let (t, v) := uses ci
      let j := Json.mkObj [("name", toJson ci.name), ("kind", kind ci), ("file", toJson path.toString),
                           ("type", toJson t), ("value", toJson v)]
      out.putStrLn j.compress
  out.flush
  return 0
