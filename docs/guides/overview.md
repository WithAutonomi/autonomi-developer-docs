# Overview

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 9475782ffc85b677aa1866f0f79fb555fca12c45
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 33e9cfb666eef361a9eec6b1663c63df04cc4f0b
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

These guides cover tasks that apply across more than one Autonomi interface: retrieving data, preparing upload payments, running local development infrastructure, testing, and configuring production services.

If you are looking for tasks that are specific to one interface, look inside that interface's section instead:

- SDK task guides live under [SDK](../sdk/install.md).
- MCP setup and skill installation live under [Agent Tools](../mcp/use-mcp-with-ai-tools.md).
- CLI task guides start with [CLI](../cli/use-the-cli.md) and the [CLI Command Reference](../cli/command-reference.md).
- Direct Rust task guides live under [Direct Rust](../rust/README.md).

## What is here

- [Build Read-Only Features](build-read-only-features.md) - retrieve existing data without configuring upload payments.
- [Prepare a Wallet for Uploads](prepare-a-wallet-for-uploads.md) - configure wallet interfaces and understand their approval and balance limitations.
- [Estimate Costs and Handle Upload Payments](estimate-costs-and-handle-upload-payments.md) - inspect sampled upload estimates and understand when uploads can approve token spend automatically.
- [Set Up a Local Network](set-up-a-local-network.md) - prepare a pinned, isolated local Autonomi Network and account for known teardown risks.
- [Test Your Application](test-your-application.md) - separate unit tests from integration tests that need local Autonomi services.
- [Deploy to Mainnet](deploy-to-mainnet.md) - configure a mainnet-facing service with built-in EVM presets.

Choose a guide for your task, then follow the steps for the interface you use.

## If you are still deciding how to build

Start with [What is Autonomi?](../index.md) for a short introduction to the Autonomi Network and the available developer and agent tools.

## Next steps

- [What is Autonomi?](../index.md)
- [Build with the SDKs](../sdk/install.md)
- [Build with AI Tools](../mcp/use-mcp-with-ai-tools.md)
- [Use the CLI](../cli/use-the-cli.md)
- [Direct Rust](../rust/README.md)
