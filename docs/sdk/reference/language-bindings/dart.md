# Dart SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the Dart SDK to store and retrieve data through a local daemon, a background service called antd. The client supports REST and gRPC.

## Install

The pub.dev package named `antd` is unrelated to ant-sdk. Use Dart 3.0 or later, but earlier than Dart 4.0, and reference the exact ant-sdk v0.12.1 release source as a local path dependency.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
```

Place your Dart project beside `ant-sdk` and add the local binding to `pubspec.yaml`:

```yaml
name: autonomi_example
description: Store and retrieve data with antd.
version: 0.1.0

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  antd:
    path: ../ant-sdk/antd-dart
```

Resolve the local dependency:

```bash
dart pub get
```

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```dart
import 'package:antd/antd.dart';

Future<void> main() async {
  final client = AntdClient(baseUrl: 'http://localhost:8082');
  try {
    final health = await client.health();
    print('antd version: ${health.version}');
  } on AntdError catch (error) {
    print('antd request failed: $error');
  } finally {
    client.close();
  }
}
```

Expected output:

```text
antd version: <version>
```

## Store and retrieve data

Start **antd** in a write-enabled mode before you upload. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```dart
import 'dart:convert';
import 'dart:typed_data';

import 'package:antd/antd.dart';

Future<void> main() async {
  final client = AntdClient();
  try {
    final payload = Uint8List.fromList(utf8.encode('Hello, Autonomi!'));
    final result = await client.dataPutPublic(payload);
    print('Stored at: ${result.address}');

    final data = await client.dataGetPublic(result.address);
    final text = utf8.decode(data);
    if (text != 'Hello, Autonomi!') {
      throw StateError('downloaded data did not match the upload');
    }
    print('Retrieved: $text');
  } on AntdError catch (error) {
    print('antd request failed: $error');
  } finally {
    client.close();
  }
}
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello, Autonomi!
```

## Type mappings

| Autonomi type | Dart type |
|------|------|
| `HealthStatus` | Dart model type |
| `PutResult` | Dart model type |
| Raw data | `Uint8List` |

## Error handling

`antd v0.13.0` reports a missing DataMap as an internal error instead of not found. Handle `InternalError` for this behavior. The client source is pinned independently to `v0.12.1`.

```dart
import 'package:antd/antd.dart';

Future<void> main() async {
  final client = AntdClient();
  try {
    final missingAddress = List.filled(64, '0').join();
    final data = await client.dataGetPublic(missingAddress);
    print(data.length);
  } on InternalError {
    print('Missing data returned an internal error');
  } on AntdError catch (error) {
    print(error);
  } finally {
    client.close();
  }
}
```

Output when the valid address is not stored:

```text
Missing data returned an internal error
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
