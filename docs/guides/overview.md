# Overview

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: 09da0f4c94fb15d928b5e9f1d4a9ae484176c995
  verified_date: 2026-07-24
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 81848a0900fa9972e9af2d323bf3b49bf8d382aa
  verified_date: 2026-07-28
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: c3ffe5a7592bf3d5fa2fdfb2f87d9ddc7ecaaecf
  verified_date: 2026-07-28
  verification_mode: current-merged-truth
-->

Guides cover tasks that apply across more than one way of building on Autonomi — setting up a local network, preparing a wallet, handling payments, building read-only features, testing, and deploying.

If you are looking for tasks that are specific to one interface, look inside that interface's section instead:

- SDK-specific task guides live under [SDK](../sdk/install.md).
- MCP-specific task guides live under [MCP](../mcp/use-mcp-with-ai-tools.md).
- Rust-specific task guides live under [Developing in Rust](../rust/README.md).
- CLI task recipes are still limited. Start with [Using the Autonomi CLI](../cli/use-the-cli.md) and the [CLI Command Reference](../cli/command-reference.md).

## What is here

- [Set Up a Local Network](set-up-a-local-network.md) — run a local Autonomi network for development and testing.
- [Prepare a Wallet for Uploads](prepare-a-wallet-for-uploads.md) — create and fund a wallet so your application can pay for uploads.
- [Estimate Costs and Handle Upload Payments](estimate-costs-and-handle-upload-payments.md) — understand upload pricing and wire payment handling into your code.
- [Build Read-Only Features](build-read-only-features.md) — retrieve public data without needing to upload or pay.
- [Test Your Application](test-your-application.md) — strategies for testing code that reads from and writes to the network.
- [Deploy to Mainnet](deploy-to-mainnet.md) — move from local network and testing to the production Autonomi network.

Each page calls out which interfaces it applies to and links to the interface-specific equivalent where one exists.

## If you are still deciding how to build

Start with [What is Autonomi?](../index.md) for a short introduction to the network and a chooser across the four interfaces.

## Next steps

- [What is Autonomi?](../index.md)
- [Build with the SDKs](../sdk/install.md)
- [Use MCP with AI Tools](../mcp/use-mcp-with-ai-tools.md)
- [Use the CLI](../cli/use-the-cli.md)
- [Developing in Rust](../rust/README.md)
