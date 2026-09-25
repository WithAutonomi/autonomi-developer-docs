# Start the Local Daemon

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 33e9cfb666eef361a9eec6b1663c63df04cc4f0b
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

Start a local daemon, a service that connects your applications to the Autonomi Network. Autonomi's daemon is called `antd`. Install it, keep it running in a terminal, and download a public image without setting up a wallet or making a payment.

## Steps

### 1. Install the daemon

Choose your operating system. These commands download the executable into a new directory and check its checksum before running it; they do not install a system service or change your `PATH`.

{% tabs %}
{% tab title="macOS" %}
Use Terminal on a Mac with Apple Silicon. The prebuilt macOS executable is ARM64; for an Intel Mac, see [Build from source](#build-from-source-instead).

```bash
set -euo pipefail
mkdir antd-0.14.0
cd antd-0.14.0
curl --fail --location --show-error \
  https://github.com/WithAutonomi/ant-sdk/releases/download/v0.14.0/antd-darwin-arm64 \
  --output antd
printf '6175801e60018518a6d9c3b5d728364f3d0970e22304cef182ca3964eef7fc26  antd\n' | shasum -a 256 -c -
chmod u+x antd
./antd --version
```

{% endtab %}
{% tab title="Linux" %}
Run these commands in Bash with `curl` and `sha256sum` installed. The x64 and ARM64 executables require glibc 2.38 or later; check your version with `ldd --version`. The commands select the executable for your machine. For an older system, see [Build from source](#build-from-source-instead).

```bash
set -euo pipefail
case "$(uname -m)" in
  x86_64)
    ASSET=antd-linux-amd64
    SHA256=096f5a42f3c6908be6746c683bb9216c8e9fdde2c544d1202c9dee9049c72fbf
    ;;
  aarch64|arm64)
    ASSET=antd-linux-arm64
    SHA256=2717f3f3fd24422bb5f0cd21517f88e153498b196d1638faa2690f948c4e4bed
    ;;
  *) printf 'No prebuilt executable for this architecture.\n' >&2; exit 1 ;;
esac
mkdir antd-0.14.0
cd antd-0.14.0
curl --fail --location --show-error \
  "https://github.com/WithAutonomi/ant-sdk/releases/download/v0.14.0/$ASSET" \
  --output antd
printf '%s  antd\n' "$SHA256" | sha256sum -c -
chmod u+x antd
./antd --version
```

{% endtab %}
{% tab title="Windows" %}
Use PowerShell on Windows x64. The executable runs from the download directory, without an installer or administrator access.

```powershell
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path antd-0.14.0 | Out-Null
Set-Location antd-0.14.0
Invoke-WebRequest -UseBasicParsing `
  -Uri 'https://github.com/WithAutonomi/ant-sdk/releases/download/v0.14.0/antd-windows-amd64.exe' `
  -OutFile antd.exe
$hash = (Get-FileHash -Algorithm SHA256 .\antd.exe).Hash
if ($hash -ne '2bece8f0d35d85567df6fdf1a2f4274e258b1db583c22abe7bea65f8923fefac') {
  throw 'Checksum mismatch. Do not run the downloaded file.'
}
Write-Output 'antd.exe: OK'
.\antd.exe --version
if ($LASTEXITCODE -ne 0) { throw 'antd did not report its version successfully.' }
```

{% endtab %}
{% endtabs %}

Expect `antd: OK` (`antd.exe: OK` on Windows), followed by `antd 0.14.0 (build dbf6a7d3d951)`. The checksum checks the file's contents; it is not a separate signature verification.

The [release page](https://github.com/WithAutonomi/ant-sdk/releases/tag/v0.14.0) also provides macOS and Windows installers, and Linux x64 Debian/RPM packages. The remaining steps use the local executable downloaded above.

### 2. Start without a wallet

Run the executable from the same directory. Clear any wallet key left in your shell environment so this process starts without one:

{% tabs %}
{% tab title="macOS / Linux" %}
```bash
unset AUTONOMI_WALLET_KEY
./antd
```

{% endtab %}
{% tab title="Windows" %}
```powershell
$env:AUTONOMI_WALLET_KEY = $null
.\antd.exe
```

{% endtab %}
{% endtabs %}

Wait until the output includes `REST server listening on 127.0.0.1:8082`, then leave this terminal open while your application uses the service. Startup connects to network peers before the API becomes available. Without wallet configuration, you can retrieve data but cannot use wallet-backed uploads.

The APIs listen on your own computer by default. Keep that setting unless you add access controls: antd has no built-in authentication, and its API includes wallet and local-file operations.

### 3. Check the connection

Open another terminal and request the health endpoint:

{% tabs %}
{% tab title="macOS / Linux" %}
```bash
curl --fail --show-error http://localhost:8082/health
```

{% endtab %}
{% tab title="Windows" %}
```powershell
Invoke-RestMethod -Uri http://localhost:8082/health | ConvertTo-Json
```

{% endtab %}
{% endtabs %}

Look for these fields in the JSON response:

```json
{
  "status": "ok",
  "version": "0.14.0"
}
```

`status: "ok"` means the local API is responding. The other fields describe network connectivity and payment configuration; see the [health reference](reference/rest-api.md#health) when you need them.

### 4. Download your first file

Keep the first terminal running. In the second terminal, download this public image to `downloaded.jpg` in your current directory. Use a different output name if you already have a file with that name.

{% tabs %}
{% tab title="macOS / Linux" %}
```bash
curl --fail --show-error \
  'http://localhost:8082/v1/data/public/711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a/stream' \
  --output downloaded.jpg
```

{% endtab %}
{% tab title="Windows" %}
```powershell
Invoke-WebRequest -UseBasicParsing `
  -Uri 'http://localhost:8082/v1/data/public/711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a/stream' `
  -OutFile downloaded.jpg
```

{% endtab %}
{% endtabs %}

Open `downloaded.jpg` to see the image. It is a 138,931-byte JPEG. Your local service retrieved it from the Autonomi Network; no payment wallet was needed.

## What happened

You installed and started a local service, checked its API, and used it to retrieve a file. Applications can use the same service through a language client or its REST/gRPC API. Press Ctrl+C in the first terminal when you want to stop it.

## Build from source instead

As an alternative to the download, install [Rust](https://www.rust-lang.org/tools/install) (which includes Cargo) and [protoc](https://protobuf.dev/installation/) (the Protocol Buffers compiler), with both tools on your `PATH`. The following Bash commands are for macOS or Linux. Run them in a separate working directory, then continue with step 2 from the `ant-sdk/antd` directory containing the built executable:

```bash
git clone --depth 1 --branch v0.14.0 https://github.com/WithAutonomi/ant-sdk.git ant-sdk
cd ant-sdk
test "$(git rev-parse HEAD)" = "dbf6a7d3d9511da6518ed369a2d1e4dba2c9ae51" || exit 1
printf 'ant-sdk v0.14.0\n'
cd antd
cargo build --release --locked
cp target/release/antd ./antd
./antd --version
```

Expected version output: `antd 0.14.0 (build dbf6a7d3d951)`.

## Next steps

- Use the service from [Python](reference/language-bindings/python.md), [JavaScript](reference/language-bindings/javascript.md), or [TypeScript](reference/language-bindings/typescript.md).
- [Retrieve Data from the Network](retrieve-data-from-the-network.md) when you already have a file address
- [Store Data on the Network](store-data-on-the-network.md)
- [Prepare a Wallet for Uploads](../guides/prepare-a-wallet-for-uploads.md)
- [Use External Signers for Upload Payments](how-to-guides/use-external-signers-for-upload-payments.md)
- [Set Up a Local Network](../guides/set-up-a-local-network.md)
- [SDK Overview](../sdk/reference/overview.md)
- [REST API](../sdk/reference/rest-api.md)
- [Use the CLI](../cli/use-the-cli.md)
