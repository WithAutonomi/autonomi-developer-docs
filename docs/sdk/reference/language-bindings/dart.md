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

Use Dart 3.0 or later, but earlier than Dart 4.0. Create a project and add the [antd_client package](https://pub.dev/packages/antd_client) from pub.dev:

```bash
dart create autonomi_example
cd autonomi_example
dart pub add antd_client
```

`dart pub add` records `antd_client` as a hosted dependency in `pubspec.yaml` and resolves it. The pub.dev package named `antd` is unrelated. Save each example as `bin/autonomi_example.dart`, replacing the generated file, and run it with `dart run`. Examples on this page use `antd_client` 0.2 with antd 0.14.

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```dart
import 'package:antd_client/antd_client.dart';

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

import 'package:antd_client/antd_client.dart';

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

An address with no stored data throws `NotFoundError`, a subclass of `AntdError`.

```dart
import 'package:antd_client/antd_client.dart';

Future<void> main() async {
  final client = AntdClient();
  try {
    final missingAddress = List.filled(64, '0').join();
    final data = await client.dataGetPublic(missingAddress);
    print(data.length);
  } on NotFoundError {
    print('No data is stored at that address');
  } on AntdError catch (error) {
    print(error);
  } finally {
    client.close();
  }
}
```

Output when the valid address is not stored:

```text
No data is stored at that address
```

External-signer finalize methods throw `PartialUploadError`, a subclass of `NetworkError`, when some chunks remain unstored; it carries `chunksStored`, `chunksFailed`, `totalChunks`, `retryable`, and `retentionKnown`. When `retryable` is `true`, repeating the same finalize call with the same upload ID stores the remainder without paying again; see the [external-signer guide](../../how-to-guides/use-external-signers-for-upload-payments.md) for the other cases.

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
