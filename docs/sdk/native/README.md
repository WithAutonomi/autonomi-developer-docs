# Connect from Your Application

Connect directly to the Autonomi Network using a Python, Node.js, or .NET library. Install the package for your language, import it into your application, and create a client to retrieve or store data.

## Choose a language

| Language | Package | Language reference |
|----------|---------|--------------------|
| Python | `ant-sdk`, import `ant_ffi` | [Python SDK](python.md) |
| Node.js / TypeScript | `@withautonomi/ant-sdk` | [Node.js SDK](nodejs.md) |
| .NET | `Autonomi.Ffi`, namespace `AntFfi` | [.NET SDK](csharp.md) |

These SDK packages include a compiled network library, which your application loads and uses. The package manager installs it for you; it is not a separate program you need to start.

## Retrieve without a wallet

The Python and Node.js references include a public-image download example alongside their installation, methods, and error handling. You do not need a wallet or payment for those examples.

## Store public or private data

You can upload a file for others to retrieve by its address, or upload it privately and retain its access information. Uploads require storage payment. The [native SDK reference](../reference/native-sdks.md) explains the methods, return values, wallet setup, and payment limits.

If several applications should share a background service, use a client library that calls [a local daemon](../use-antd.md). Autonomi's local daemon is called `antd`. Those client libraries are also part of the SDK toolkit, but use different packages and APIs from the libraries on this page.

## Related pages

- [Python SDK](python.md)
- [Node.js SDK](nodejs.md)
- [.NET SDK](csharp.md)
- [Build with the SDKs](../install.md)
- [Use a Local Daemon](../use-antd.md)
