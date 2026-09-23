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

The `autonomi/antd` package is not published on Packagist for ant-sdk v0.12.1. Use PHP 8.1 or later and Composer inside the exact release source. Save the examples on this page in `ant-sdk/antd-php/` so they can load that source tree's generated autoloader.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
cd ant-sdk/antd-php
composer install --no-dev
```

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

`antd v0.13.0` reports a missing DataMap as an internal error instead of not found. Handle `InternalError` for this behavior. The client source is pinned independently to `v0.12.1`.

```php
<?php

require_once 'vendor/autoload.php';

use Autonomi\Antd\AntdClient;
use Autonomi\Antd\Errors\AntdError;
use Autonomi\Antd\Errors\InternalError;

try {
    $client = new AntdClient();
    $client->dataGetPublic(str_repeat('0', 64));
} catch (InternalError $e) {
    echo "Missing data returned an internal error\n";
} catch (AntdError $e) {
    echo $e->getMessage() . PHP_EOL;
}
```

Output when the valid address is not stored:

```text
Missing data returned an internal error
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
