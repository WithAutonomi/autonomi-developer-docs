# Zig SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the Zig SDK to store and retrieve data through a local daemon, a background service called antd. The client uses REST.

## Install

Use Zig 0.14 and reference the exact ant-sdk v0.12.1 release source as a local dependency. This workflow does not use a registry package.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
```

Place your Zig project beside `ant-sdk` and use this `build.zig.zon` dependency:

```zig
.{
    .name = .autonomi_example,
    .version = "0.0.0",
    .minimum_zig_version = "0.14.0",
    .paths = .{ "build.zig", "build.zig.zon", "src" },
    .dependencies = .{
        .antd = .{
            .path = "../ant-sdk/antd-zig",
        },
    },
}
```

Import the dependency in your `build.zig`:

```zig
const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const antd_dependency = b.dependency("antd", .{
        .target = target,
        .optimize = optimize,
    });

    const executable = b.addExecutable(.{
        .name = "autonomi-example",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    executable.root_module.addImport("antd", antd_dependency.module("antd"));
    b.installArtifact(executable);
}
```

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```zig
const std = @import("std");
const antd = @import("antd");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    var client = antd.Client.init(allocator, antd.default_base_url);
    defer client.deinit();

    const status = try client.health();
    defer status.deinit(allocator);
    std.debug.print("antd version: {s}\n", .{status.version});
}
```

Expected output:

```text
antd version: <version>
```

## Store and retrieve data

Start **antd** in a write-enabled mode before you upload. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```zig
const std = @import("std");
const antd = @import("antd");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    var client = antd.Client.init(allocator, antd.default_base_url);
    defer client.deinit();

    const payload = "Hello, Autonomi!";
    const result = try client.dataPutPublic(payload, .auto);
    defer result.deinit(allocator);
    std.debug.print("Stored at: {s}\n", .{result.address});

    const data = try client.dataGetPublic(result.address);
    defer allocator.free(data);
    if (!std.mem.eql(u8, data, payload)) return error.DataMismatch;
    std.debug.print("Retrieved: {s}\n", .{data});
}
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello, Autonomi!
```

## Type mappings

| Autonomi type | Zig type |
|------|------|
| `HealthStatus` | Zig struct |
| `PutResult` | Zig struct |
| Raw data | `[]const u8` |

## Error handling

`antd 0.14.0` reports a valid address with no stored data as not found. Handle `error.NotFound` for this case. The client source is pinned independently to `v0.12.1`.

```zig
const std = @import("std");
const antd = @import("antd");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    var client = antd.Client.init(allocator, antd.default_base_url);
    defer client.deinit();

    const missing_address = "0000000000000000000000000000000000000000000000000000000000000000";
    const data = client.dataGetPublic(missing_address) catch |err| switch (err) {
        error.NotFound => {
            std.debug.print("No data is stored at that address\n", .{});
            return;
        },
        else => return err,
    };
    defer allocator.free(data);
    std.debug.print("Retrieved {d} bytes\n", .{data.len});
}
```

Output when the valid address is not stored:

```text
No data is stored at that address
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
