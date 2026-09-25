# Post-Quantum Cryptography

<!-- verification:
  source_repo: saorsa-pqc
  source_ref: main
  source_commit: 4fbb31d3d29f710726edd32e12ce7b1f64a2aae1
  verified_date: 2026-08-04
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-transport
  source_ref: main
  source_commit: 75a1e11e49872fa4ebe768d85f20ae3a8db9e91d
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-keygen
  source_ref: main
  source_commit: 902442f123e16f57de0aeb0f1bfbacf385aa2e87
  verified_date: 2026-08-08
  verification_mode: current-merged-truth
-->

Post-quantum cryptography uses algorithms designed to resist attacks from quantum computers; Autonomi uses them for transport key exchange, transport authentication, and release signing.

## Why it matters

If you are reasoning about security, transport identity, or release authenticity, you need to know which cryptographic primitives the stack uses.

## How it works

### saorsa-pqc

`saorsa-pqc 0.5.1` is a broader post-quantum cryptography library that includes:

- ML-KEM key encapsulation variants
- ML-DSA signature variants
- SLH-DSA signature variants
- BLAKE3, SHA3, HMAC, HKDF, AES-256-GCM, and ChaCha20-Poly1305

So the library itself is broader than any single Autonomi-facing transport choice.

### saorsa-transport

`saorsa-transport 0.36.3` uses this pair for transport:

- ML-KEM-768 for key exchange
- ML-DSA-65 for signatures

The transport layer has no classical fallback.

### ant-keygen

`ant-keygen` is the release-signing CLI that uses ML-DSA-65. It generates release-signing keypairs, signs files, verifies signatures, and supports a signing context for domain separation.

Before installing a release, follow its signature-verification instructions and check the [known signing limitations](../reference/source-repositories.md#source-identity-limitations).

### Key separation and signing contexts

`saorsa-pqc` provides HKDF-SHA3-256 and HKDF-SHA3-512 as key-derivation primitives.

That means the crypto library can derive new key material from shared secrets or existing key material. `ant-keygen` also supports a signing context so one signing domain stays separate from another. The default context is `ant-node-release-v1`.

## Practical example

`ant-keygen 0.1.0` relies on the process umask when it creates a secret key. This demonstration sets `umask 077` so newly created key files are accessible only to the process owner, uses an isolated temporary directory, and removes the throwaway key when it exits. Production release keys need protected, durable storage and a separate access policy.

```bash
set -euo pipefail

umask 077
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

printf 'release artifact\n' > "$WORK_DIR/artifact.tar.gz"
ant-keygen generate "$WORK_DIR/keys"

ant-keygen sign \
  --key "$WORK_DIR/keys/release-signing-key.secret" \
  --input "$WORK_DIR/artifact.tar.gz" \
  --output "$WORK_DIR/artifact.sig"

ant-keygen verify \
  --key "$WORK_DIR/keys/release-signing-key.pub" \
  --input "$WORK_DIR/artifact.tar.gz" \
  --signature "$WORK_DIR/artifact.sig"

# Expected final line: Signature is VALID
```

## Packages and tools

- [`saorsa-pqc 0.5.2`](https://crates.io/crates/saorsa-pqc/0.5.2) ships with `antd 0.14.0`, `ant-cli 0.3.8`, and `ant-node 0.20.0`
- [`saorsa-transport 0.37.0`](https://crates.io/crates/saorsa-transport/0.37.0) ships with `antd 0.14.0`, `ant-cli 0.3.8`, and `ant-node 0.20.0`
- [`ant-keygen v0.1.0`](https://github.com/WithAutonomi/ant-keygen/releases/tag/v0.1.0)

## Related pages

- [Self-encryption](self-encryption.md)
- [Core Concepts Overview](overview.md)
- [Source Repositories](../reference/source-repositories.md)
