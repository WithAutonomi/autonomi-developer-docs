# Use a Local Daemon

A local daemon is a background service that connects your applications to the Autonomi Network. Autonomi's daemon is called `antd`. Start it once, then call it from your application through a client library or its REST/gRPC API.

Use this approach when several applications should share one network service, or when you prefer to work through a local API.

## Start the service

[Start the Local Daemon](start-the-local-daemon.md) takes you through installation and your first connection check. You do not need a payment wallet to retrieve public data.

Keep the API accessible only from your own computer unless you add access controls. It has no built-in authentication: applications that can reach it can call wallet and local-file operations, not only download data.

## Install a client

A client library runs inside your application and turns method calls into requests to the separate service. Installing the library does not install or start `antd`.

| Language | Package |
|----------|-----------------------------------|
| [Python](reference/language-bindings/python.md) | `antd[rest]` on PyPI |
| [JavaScript](reference/language-bindings/javascript.md) / [TypeScript](reference/language-bindings/typescript.md) | `@withautonomi/antd` on npm |
| [Go](reference/language-bindings/go.md) | Go module; follow the version-specific instructions |
| [Rust](reference/language-bindings/rust.md) | `antd-client` from the source checkout described in its guide |

Find other languages in [Language Bindings](reference/language-bindings/README.md). You can also call [REST](reference/rest-api.md) or [gRPC](reference/grpc-services.md) without installing a language client.

## Retrieve or store data

Follow [Retrieve Data from the Network](retrieve-data-from-the-network.md) for client installation and a public-image download. The walkthrough supplies the address, so you do not need to upload anything first.

Follow [Store Data on the Network](store-data-on-the-network.md) for client installation, wallet setup, and a public upload. To keep the signing key outside antd, use [an external signer](how-to-guides/use-external-signers-for-upload-payments.md) instead. Storage and blockchain transactions cost money; review payment settings before submitting an upload.

For local development with test funds, use the component versions in [Set Up a Local Network](../guides/set-up-a-local-network.md). That setup has separate installation and cleanup requirements.

## Related pages

- [Start the Local Daemon](start-the-local-daemon.md)
- [SDK How-To Guides](how-to-guides/README.md)
- [SDK Reference](reference/README.md)
- [Connect from Your Application](native/README.md) for libraries that connect directly without a separate background service
- [Build with AI Tools](../mcp/use-mcp-with-ai-tools.md)
