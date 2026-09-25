# C++ SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the C++ SDK to store and retrieve data through a local daemon, a background service called antd. The client uses REST, with optional gRPC support.

## Install

Use CMake 3.14 or later, a C++20 compiler, and the exact ant-sdk v0.12.1 release source as a local subdirectory. This workflow does not use a registry package.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
```

Place your application beside `ant-sdk` and use this complete `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.14)
project(autonomi_example LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(../ant-sdk/antd-cpp ${CMAKE_BINARY_DIR}/antd-cpp)
add_executable(autonomi_example main.cpp)
target_link_libraries(autonomi_example PRIVATE antd)
```

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```cpp
#include "antd/antd.hpp"
#include <exception>
#include <iostream>

int main() {
    try {
        antd::Client client("http://localhost:8082");
        const auto health = client.health();
        std::cout << "antd version: " << health.version << '\n';
        return health.ok ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "antd request failed: " << error.what() << '\n';
        return 1;
    }
}
```

Expected output:

```text
antd version: <version>
```

## Store and retrieve data

Start **antd** in a write-enabled mode before you upload. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```cpp
#include "antd/antd.hpp"
#include <cstdint>
#include <exception>
#include <iostream>
#include <string>
#include <stdexcept>
#include <vector>

int main() {
    try {
        antd::Client client;
        const std::string message = "Hello, Autonomi!";
        const std::vector<uint8_t> data(message.begin(), message.end());

        const auto result = client.data_put_public(data);
        std::cout << "Stored at: " << result.address << '\n';

        const auto retrieved = client.data_get_public(result.address);
        if (retrieved != data) {
            throw std::runtime_error("downloaded data did not match the upload");
        }
        std::cout << "Retrieved: "
                  << std::string(retrieved.begin(), retrieved.end()) << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "antd request failed: " << error.what() << '\n';
        return 1;
    }
}
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello, Autonomi!
```

## Type mappings

| Autonomi type | C++ type |
|------|------|
| `HealthStatus` | struct with `ok` and `network` |
| `PutResult` | struct with `cost` and `address` |
| Raw data | `std::vector<uint8_t>` |

## Error handling

`antd v0.13.0` reports a missing DataMap as an internal error instead of not found. Handle `InternalError` for this behavior. The client source is pinned independently to `v0.12.1`.

```cpp
#include "antd/antd.hpp"
#include <iostream>
#include <string>

int main() {
    try {
        antd::Client client;
        const std::string missing_address(64, '0');
        const auto data = client.data_get_public(missing_address);
        std::cout << data.size() << '\n';
    } catch (const antd::InternalError&) {
        std::cout << "Missing data returned an internal error\n";
    } catch (const antd::AntdError& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}
```

Output when the valid address is not stored:

```text
Missing data returned an internal error
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
