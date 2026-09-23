# Swift SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the Swift SDK to store and retrieve data through a local daemon, a background service called antd. The client supports REST and gRPC.

## Install

The binding is not published as a remote Swift package for ant-sdk v0.12.1. Use Swift 5.9 or later, macOS 15 or later, and reference the exact release source as a local package. The released package declares macOS 13, but its public `DaemonDiscovery` API exposes a macOS-15-only gRPC type without an availability guard, so the combined package does not build with the declared macOS 13 target.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
mkdir AutonomiExample
cd AutonomiExample
swift package init --type executable
rm Sources/main.swift
mkdir -p Sources/AutonomiExample
```

Use this complete `Package.swift` file while `AutonomiExample` and `ant-sdk` share a parent directory:

```swift
// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "AutonomiExample",
    platforms: [.macOS(.v15)],
    dependencies: [
        .package(path: "../ant-sdk/antd-swift"),
    ],
    targets: [
        .executableTarget(
            name: "AutonomiExample",
            dependencies: [
                .product(name: "AntdSdk", package: "antd-swift"),
            ]
        ),
    ]
)
```

For each example below, save the code as `Sources/AutonomiExample/Main.swift`, then run `swift run`.

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```swift
import Foundation
import AntdSdk

@main
struct Connect {
    static func main() async {
        let client = AntdClient.createRest(baseURL: "http://localhost:8082")

        do {
            let status = try await client.health()
            print("antd version: \(status.version)")
        } catch {
            print("antd request failed: \(error)")
        }
    }
}
```

Expected output:

```text
antd version: <version>
```

## Store and retrieve data

Start **antd** in a write-enabled mode before you upload. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```swift
import Foundation
import AntdSdk

@main
struct StoreAndRetrieve {
    static func main() async {
        let client = AntdClient.createRest()
        let payload = Data("Hello, Autonomi!".utf8)

        do {
            let result = try await client.dataPutPublic(payload, paymentMode: .auto)
            print("Stored at: \(result.address)")

            let data = try await client.dataGetPublic(address: result.address)
            guard data == payload else {
                throw NSError(domain: "AutonomiExample", code: 1)
            }
            print("Retrieved: \(String(decoding: data, as: UTF8.self))")
        } catch {
            print("antd request failed: \(error)")
        }
    }
}
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello, Autonomi!
```

## Type mappings

| Autonomi type | Swift type |
|------|------|
| `HealthStatus` | Swift model type |
| `PutResult` | Swift model type |
| Raw data | `Data` |

## Error handling

`antd v0.13.0` reports a missing DataMap as an internal error instead of not found. Handle `InternalError` for this behavior. The client source is pinned independently to `v0.12.1`.

```swift
import Foundation
import AntdSdk

@main
struct HandleErrors {
    static func main() async {
        let client = AntdClient.createRest()
        let missingAddress = String(repeating: "0", count: 64)

        do {
            _ = try await client.dataGetPublic(address: missingAddress)
        } catch is InternalError {
            print("Missing data returned an internal error")
        } catch let error as AntdError {
            print(error.message)
        } catch {
            print(error)
        }
    }
}
```

Output when the valid address is not stored:

```text
Missing data returned an internal error
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
