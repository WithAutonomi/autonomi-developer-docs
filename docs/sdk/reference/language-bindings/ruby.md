# Ruby SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the Ruby SDK to store and retrieve data through a local daemon, a background service called antd. The client uses REST by default, with an optional gRPC client.

## Install

Use Ruby 3.1 or later. This workflow builds the gem from the exact ant-sdk v0.12.1 release source, rather than using the separately published [antd 0.1.0 gem](https://rubygems.org/gems/antd/versions/0.1.0) on RubyGems.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
cd ant-sdk/antd-ruby
gem build antd.gemspec
gem install ./antd-0.1.0.gem
```

For gRPC, also install the optional runtime dependency:

```bash
gem install grpc --version '~> 1.60'
```

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```ruby
require "antd"

begin
  client = Antd::Client.new(base_url: "http://localhost:8082")
  health = client.health
  puts "antd version: #{health.version}"
rescue Antd::AntdError => e
  abort "antd request failed: #{e.message}"
end
```

Expected output:

```text
antd version: <version>
```

## Store and retrieve data

Start **antd** in a write-enabled mode before you upload. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```ruby
require "antd"

begin
  client = Antd::Client.new
  payload = "Hello, Autonomi!"
  result = client.data_put_public(payload)
  puts "Stored at: #{result.address}"

  data = client.data_get_public(result.address)
  raise "downloaded data did not match the upload" unless data == payload

  puts "Retrieved: #{data}"
rescue Antd::AntdError => e
  abort "antd request failed: #{e.message}"
end
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello, Autonomi!
```

## Type mappings

| Autonomi type | Ruby type |
|------|------|
| `HealthStatus` | model object with `ok` and `network` |
| `PutResult` | model object with `cost` and `address` |
| Raw data | `String` |

## Error handling

`antd v0.13.0` reports a missing DataMap as an internal error instead of not found. Handle `InternalError` for this behavior. The client source is pinned independently to `v0.12.1`.

```ruby
require "antd"

begin
  client = Antd::Client.new
  client.data_get_public("0" * 64)
rescue Antd::InternalError
  puts "Missing data returned an internal error"
rescue Antd::AntdError => e
  puts e.message
end
```

Output when the valid address is not stored:

```text
Missing data returned an internal error
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
