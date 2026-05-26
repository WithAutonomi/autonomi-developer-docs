# Overview

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: 7a113b390522d76d28b8f3e5b4078f9c9418d46f
  verified_date: 2026-05-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: e67472424f94acd4b9188a342271210d4ab9f94d
  verified_date: 2026-05-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 2a8b91deada5506c72b7d234655119b2ab803d92
  verified_date: 2026-05-26
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
