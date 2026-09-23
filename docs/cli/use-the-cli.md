# Using the Autonomi CLI

<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 9475782ffc85b677aa1866f0f79fb555fca12c45
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

The Autonomi command-line interface (CLI) lets you download and upload files, check your wallet, and manage nodes that contribute storage to the Autonomi Network. Use it from your terminal, include it in scripts and pipelines, or [let your AI agent use it for you](../mcp/use-mcp-with-ai-tools.md).

The command is `ant`. Start with a free download; you do not need a wallet or tokens.

## Install the CLI

Choose your operating system. The installer adds `ant` and its connection settings.

{% tabs %}
{% tab title="Linux and macOS" %}
```bash
curl -fsSL https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.sh | bash
ant --version
```

{% endtab %}
{% tab title="Windows" %}
Run in PowerShell:

```powershell
irm https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.ps1 | iex
ant --version
```

The installer adds `ant` to your user PATH, the command search path. If an already-open terminal cannot find it, open a new terminal.
{% endtab %}
{% endtabs %}

Run `ant --help` to explore the commands. For manual downloads and signature verification, use the [CLI release instructions](https://github.com/WithAutonomi/ant-client/releases/latest); the installer scripts do not verify archive signatures.

## Download your first file

Download a public image of Lucky the dog. Run this in a directory where `lucky.jpg` does not already exist, because the command can replace an existing file:

```bash
ant file download 711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a -o lucky.jpg
```

When the command prints `Download complete!`, open `lucky.jpg` to see the image. No wallet or payment is needed.

The long address identifies the public file; `-o lucky.jpg` chooses the filename on your computer. To download another public file, replace the address and choose a new output filename.

## Upload a file when you are ready

Uploading is optional and **costs money**. The cost and upload commands are the same on Windows, macOS, and Linux; only the wallet setup differs.

### 1. Choose a file and check the cost

Choose an existing file you want to share. The examples use `photo.jpg`; replace it with your filename or a quoted path such as `"My Photos/holiday.jpg"`.

```sh
ant file cost photo.jpg
```

The estimate does not spend funds and is not a maximum charge. A public upload also stores access information for the file, which adds to the cost; transaction fees can vary.

### 2. Configure wallet access

Use a low-value wallet funded with Autonomi Network Token (ANT) for storage and ETH for transaction fees on Arbitrum One. The CLI reads its private key from `SECRET_KEY`, an environment variable in your terminal. Enter the key at the hidden prompt, not in the command or an AI conversation.

{% tabs %}
{% tab title="macOS / Linux" %}
Run in Bash or zsh:

```bash
unset SECRET_KEY
printf 'Wallet private key: '
read -r -s SECRET_KEY
printf '\n'
export SECRET_KEY
```

When you finish using the wallet, run `unset SECRET_KEY` in this terminal.
{% endtab %}
{% tab title="Windows" %}
Run in PowerShell:

```powershell
Remove-Item Env:SECRET_KEY -ErrorAction SilentlyContinue
$env:SECRET_KEY = [System.Net.NetworkCredential]::new(
    '', (Read-Host 'Wallet private key' -AsSecureString)
).Password
```

When you finish using the wallet, run `Remove-Item Env:SECRET_KEY` in this terminal.
{% endtab %}
{% endtabs %}

Keep using the same terminal for the upload. Commands launched from it can access the key until you clear it or close the terminal.

To confirm which wallet you selected, see [CLI wallet checks](../guides/prepare-a-wallet-for-uploads.md#5-inspect-a-direct-cli-wallet). The CLI reports its address and ANT balance, not its ETH balance.

### 3. Upload the file

**Before uploading:** `--public` lets anyone with the returned address read the file. Do not use it for secrets. The upload can also grant the payment contract unlimited permission to spend ANT when its existing allowance is insufficient. The command does not ask for a separate payment confirmation.

```sh
ant file upload photo.jpg --public
```

This uses Arbitrum One for payment when no local-development manifest or network override is supplied. Clear the key using the command in your wallet-setup tab when you finish.

On success, the CLI prints a public address and upload details. Keep the address: you can use it with `ant file download` to retrieve the file. If the upload fails, inspect the error and any payments before retrying; a failure does not mean nothing was charged.

For private storage, omit `--public`. The CLI saves a local DataMap file and prints its path. Protect and back up that file: it lets you retrieve the data. See [private-file retrieval](command-reference.md#download-a-file) for the download command.

## Common errors

**Command not found**: Use the installer's printed destination in your command search path, or reopen your terminal after Windows installation.

**No bootstrap peers**: The installer supplies a `bootstrap_peers.toml` connection file but preserves an existing copy. For manual installation, follow the configuration instructions supplied with your [CLI release](https://github.com/WithAutonomi/ant-client/releases/latest).

## Next steps

- [CLI Command Reference](command-reference.md): explore file, wallet, and node commands.
- [Build with AI Tools](../mcp/use-mcp-with-ai-tools.md): let an agent help you use Autonomi.
- [Set Up a Local Network](../guides/set-up-a-local-network.md): test in an isolated environment using that guide's component versions.
- [Build with the SDKs](../sdk/install.md): use a language library in your application.
- [Build Directly in Rust](../rust/build-directly-in-rust.md): integrate using the Rust library.
- [Build the CLI from source](https://github.com/WithAutonomi/ant-client#development).
