"""Provenance record for the delivery artifact (E4, fail-closed).

Generates provenance.json in SLSA v1 shape for sbom.cdx.json built from the
current git commit. Requires sbom.cdx.json to exist (run sbom first) and git
to be available. Missing inputs fail loudly; never passes silently.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SBOM = ROOT / "sbom.cdx.json"
OUT = ROOT / "provenance.json"
DOCKERFILE = ROOT / "Dockerfile"


def run_git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git"] + args, cwd=ROOT, capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        print(f"provenance: FAIL — git {' '.join(args)} failed: {proc.stderr.strip()}")
        sys.exit(1)
    return proc.stdout.strip()


def sha256_file(path: pathlib.Path) -> str:
    try:
        data = path.read_bytes()
    except OSError as exc:
        print(f"provenance: FAIL — cannot read {path.name}: {exc}")
        sys.exit(1)
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if not SBOM.is_file():
        print("provenance: FAIL — sbom.cdx.json missing; run the sbom verb first")
        return 1
    commit = run_git(["rev-parse", "HEAD"])
    if not commit:
        print("provenance: FAIL — empty commit sha")
        return 1
    sbom_digest = sha256_file(SBOM)
    docker_digest = sha256_file(DOCKERFILE) if DOCKERFILE.is_file() else "absent"
    record = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [{"name": "sbom.cdx.json", "digest": {"sha256": sbom_digest}}],
        "predicate": {
            "buildDefinition": {
                "buildType": "https://github.com/G1DO/service-starter/.github/workflows/deliver.yml",
                "externalParameters": {
                    "artifact": "service-starter:local",
                    "source_commit": commit,
                    "Dockerfile_sha256": docker_digest,
                },
                "resolvedDependencies": [
                    {
                        "uri": f"git+https://github.com/G1DO/service-starter@{commit}",
                        "digest": {"sha1": commit},
                    }
                ],
            },
            "runDetails": {
                "builder": {
                    "id": "https://github.com/G1DO/service-starter/.github/workflows/deliver.yml"
                },
                "metadata": {"invocationId": "deliver-workflow"},
                "note": "Unsigned local record; hosted release signs and publishes with the artifact",
            },
        },
    }
    OUT.write_text(json.dumps(record, indent=2) + "\n")
    print(f"provenance: ok ({OUT.name} for {SBOM.name} at {commit[:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
