# PHP SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the PHP SDK to store and retrieve data through a local daemon, a background service called antd. The client uses REST.

## Install

Use PHP 8.2 or later and Composer. In your project directory, add the [autonomi/antd package](https://packagist.org/packages/autonomi/antd) from Packagist:

```bash
composer require autonomi/antd
```

Composer writes `vendor/autoload.php` in your project directory. Save each example as `app.php` in that directory and run it with `php app.php`. Examples on this page use `autonomi/antd` 0.2 with antd 0.14.

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```php
<?php

require_once 'vendor/autoload.php';

use Autonomi\Antd\AntdClient;
use Autonomi\Antd\Errors\AntdError;

try {
    $client = new AntdClient('http://localhost:8082');
    $health = $client->health();
    echo "antd version: {$health->version}" . PHP_EOL;
} catch (AntdError $error) {
    fwrite(STDERR, "antd request failed: {$error->getMessage()}" . PHP_EOL);
    exit(1);
}
```

Expected output:

```text
antd version: <version>
```

## Store and retrieve data

Start **antd** in a write-enabled mode before you upload. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```php
<?php

require_once 'vendor/autoload.php';

use Autonomi\Antd\AntdClient;
use Autonomi\Antd\Errors\AntdError;

try {
    $client = new AntdClient();
    $payload = 'Hello, Autonomi!';
    $result = $client->dataPutPublic($payload);
    echo "Stored at: {$result->address}" . PHP_EOL;

    $data = $client->dataGetPublic($result->address);
    if ($data !== $payload) {
        throw new RuntimeException('downloaded data did not match the upload');
    }
    echo "Retrieved: {$data}" . PHP_EOL;
} catch (AntdError $error) {
    fwrite(STDERR, "antd request failed: {$error->getMessage()}" . PHP_EOL);
    exit(1);
}
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello, Autonomi!
```

## Type mappings

| Autonomi type | PHP type |
|------|------|
| `HealthStatus` | response object |
| `PutResult` | response object |
| Raw data | `string` |

## Error handling

An address with no stored data throws `NotFoundError`, a subclass of `AntdError`.

```php
<?php

require_once 'vendor/autoload.php';

use Autonomi\Antd\AntdClient;
use Autonomi\Antd\Errors\AntdError;
use Autonomi\Antd\Errors\NotFoundError;

try {
    $client = new AntdClient();
    $client->dataGetPublic(str_repeat('0', 64));
} catch (NotFoundError $e) {
    echo "No data is stored at that address" . PHP_EOL;
} catch (AntdError $e) {
    echo $e->getMessage() . PHP_EOL;
}
```

Output when the valid address is not stored:

```text
No data is stored at that address
```

External-signer finalize methods throw `Autonomi\Antd\Errors\PartialUploadError`, a subclass of `NetworkError`, when some chunks remain unstored; it carries `chunksStored`, `chunksFailed`, `totalChunks`, `retryable`, and `retentionKnown`. When `retryable` is `true`, repeating the same finalize call with the same upload ID stores the remainder without paying again; see the [external-signer guide](../../how-to-guides/use-external-signers-for-upload-payments.md) for the other cases.

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
