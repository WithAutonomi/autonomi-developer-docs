# Java SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the Java SDK to store and retrieve data through a local daemon, a background service called antd. The client uses REST by default, with asynchronous and gRPC clients also available.

## Install

The Java binding is not published to Maven Central for ant-sdk v0.12.1. Use JDK 17 or later and publish the exact release source to your local Maven repository.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
cd ant-sdk/antd-java
./gradlew publishToMavenLocal
```

Add `mavenLocal()` to your application's repositories and add the locally built artifact:

```kotlin
plugins {
    application
}

repositories {
    mavenLocal()
    mavenCentral()
}

dependencies {
    implementation("com.autonomi:antd-java:0.1.0")
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

application {
    mainClass.set("Connect")
}
```

The artifact version is `0.1.0` inside the ant-sdk v0.12.1 release source. The command above publishes only to your local Maven repository.

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```java
import com.autonomi.antd.AntdClient;

public class Connect {
    public static void main(String[] args) throws Exception {
        try (var client = new AntdClient()) {
            var health = client.health();
            System.out.println("antd version: " + health.version());
        }
    }
}
```

Expected output:

```text
antd version: <version>
```

The SDK also provides `AsyncAntdClient` and `GrpcAntdClient`.

## Store and retrieve data

Start **antd** in a write-enabled mode before you upload. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```java
import com.autonomi.antd.AntdClient;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public class Connect {
    public static void main(String[] args) throws Exception {
        try (var client = new AntdClient()) {
            byte[] payload = "Hello, Autonomi!".getBytes(StandardCharsets.UTF_8);
            var result = client.dataPutPublic(payload);
            System.out.println("Stored at: " + result.address());

            byte[] data = client.dataGetPublic(result.address());
            if (!Arrays.equals(data, payload)) {
                throw new IllegalStateException("downloaded data did not match the upload");
            }
            System.out.println("Retrieved: " + new String(data, StandardCharsets.UTF_8));
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

| Autonomi type | Java type |
|------|------|
| `HealthStatus` | `com.autonomi.antd.models.HealthStatus` |
| `PutResult` | `com.autonomi.antd.models.PutResult` |
| Raw data | `byte[]` |

## Error handling

`antd 0.14.0` reports a valid address with no stored data as not found. Handle `NotFoundException` for this case. The client source is pinned independently to `v0.12.1`.

```java
import com.autonomi.antd.AntdClient;
import com.autonomi.antd.errors.AntdException;
import com.autonomi.antd.errors.NotFoundException;

public class HandleErrors {
    public static void main(String[] args) throws Exception {
        String missingAddress = "0".repeat(64);

        try (var client = new AntdClient()) {
            client.dataGetPublic(missingAddress);
        } catch (NotFoundException exception) {
            System.out.println("No data is stored at that address");
        } catch (AntdException exception) {
            System.out.println(exception.getMessage());
        }
    }
}
```

Output when the valid address is not stored:

```text
No data is stored at that address
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
