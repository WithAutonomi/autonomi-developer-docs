# Using the Autonomi CLI

<!-- verification:
  source_repo: ant-client
  source_ref: ant-cli-v0.3.12
  source_commit: 6096b1c8caf6688d6825fcb9ff61fa1b590d984b
  verified_date: 2026-10-29
  verification_mode: target-manifest
-->

The Autonomi command-line interface (CLI) lets you download and upload files, check your wallet, and manage nodes that contribute storage to the Autonomi Network. Use it from your terminal, include it in scripts and pipelines, or [let your AI agent use it for you](../mcp/use-mcp-with-ai-tools.md).

The command is `ant`. Start with a free download; you do not need a wallet or tokens.

## Install the CLI

Choose an installation method. Use npm if you have Node.js, or use the installer for your operating system.

{% tabs %}
{% tab title="npm" %}
With [Node.js 18 or later](https://nodejs.org/en/download), run:

```sh
npm install -g @withautonomi/ant
```

This installs the CLI for your platform on macOS, Linux, or Windows. Keep npm's optional dependencies enabled; they contain the executable.
{% endtab %}
{% tab title="Linux and macOS" %}
```bash
curl -fsSL https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.sh | bash
```

{% endtab %}
{% tab title="Windows" %}
Run in PowerShell:

```powershell
irm https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.ps1 | iex
```

The installer adds `ant` to your user PATH, the command search path. If an already-open terminal cannot find it, open a new terminal.
{% endtab %}
{% endtabs %}

Confirm the installation and explore the commands:

```bash
ant --version
ant --help
```

For manual downloads and signature verification, use the [CLI release instructions](https://github.com/WithAutonomi/ant-client/releases/latest); the installer scripts do not verify archive signatures.

## Download your first file

Download a public image of Lucky the dog. Run this in a directory where `lucky.jpg` does not already exist, because the command can replace an existing file:

```bash
ant file download 711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a -o lucky.jpg
```

When the command prints `Download complete!`, open `lucky.jpg` to see the image. No wallet or payment is needed.

The long address identifies the public file; `-o lucky.jpg` chooses the filename on your computer. To download another public file, replace the address and choose a new output filename.

## Store data with the CLI

The CLI supports private and public file uploads, cost estimates, manifests, chunks, and mutable pointers. Uploads and pointer writes are paid operations. On the default Arbitrum One network, they require a wallet funded with Autonomi Network Token (ANT) for storage and ETH for transaction fees.

Before spending funds, review the exact commands, payment requirements, and visibility rules in the [CLI Command Reference](command-reference.md). This onboarding page does not provide a paid upload walkthrough.

## Update the CLI

If you installed with npm:

```sh
npm update -g @withautonomi/ant
```

For installations made with the shell or PowerShell installer:

```sh
ant update
```

Use the same installation method for updates. See the [update reference](command-reference.md#update-command) for channel options.

## Common errors

**Command not found**: Use the installer's printed destination in your command search path, or reopen your terminal after Windows installation.

**npm cannot find the platform executable**: Reinstall without `--omit=optional` or `--no-optional`; the CLI binary comes from an optional platform package.

**Failed to create dual-stack network nodes**: The computer or container has no working IPv6. Add `--ipv4-only` before the subcommand, for example `ant --ipv4-only file download <ADDRESS> -o <FILE>`.

**Not found after `found 0 peers`**: The CLI could not reach any bootstrap peer, so the address may still be correct. Check that your network allows outbound UDP, which the CLI uses to connect over QUIC.

**Connection configuration errors**: The CLI includes built-in bootstrap peers, so npm does not need to create a `bootstrap_peers.toml` file for normal use. A custom config file or explicit peer settings take precedence; check those if you have configured them.

## Next steps

- [CLI Command Reference](command-reference.md): explore file, wallet, and node commands.
- [Build with AI Tools](../mcp/use-mcp-with-ai-tools.md): let an agent help you use Autonomi.
- [Set Up a Local Network](../guides/set-up-a-local-network.md): test in an isolated environment using that guide's component versions.
- [Build with the SDKs](../sdk/install.md): use a language library in your application.
- [Build Directly in Rust](../rust/build-directly-in-rust.md): integrate using the Rust library.
- [Build the CLI from source](https://github.com/WithAutonomi/ant-client#development).
