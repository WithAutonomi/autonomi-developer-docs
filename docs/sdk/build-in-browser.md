# Browser SDK

<!-- verification:
  source_repo: ant-browser-sdk
  source_ref: v0.1.4
  source_commit: 5199100c15527bf657ae4a795c2bdf5d086981f7
  verified_date: 2026-10-27
  verification_mode: target-manifest
-->

{% hint style="info" %}
**Experimental SDK.** The browser SDK and its direct-browser protocol are experimental.
{% endhint %}

Use the browser SDK to build web applications that read, display and store data directly on the Autonomi Network. Your application uses JavaScript or TypeScript to call a network client that runs inside the browser; visitors do not need to install a local daemon or command-line tool.

The browser SDK is part of the [Autonomi SDKs](install.md). Its package, `@withautonomi/ant-browser-sdk`, is designed for browser applications. The [Node.js SDK](native/nodejs.md) runs in a server-side JavaScript application, while [local-daemon clients](use-antd.md) call a separate background service.

## What you can build

The SDK gives your web application access to stored content. You choose how to present it and what your users can do with it.

| Application | How it can use the browser SDK |
|-------------|--------------------------------|
| Book or document reader | Retrieve a book or document by its address, then pass its bytes to your application's reader or document renderer |
| Image gallery | Retrieve images and display them with ordinary browser elements |
| Audio or video player | Read media progressively and support seeking without downloading the entire file first |
| Data viewer | Retrieve a stored dataset or JSON file and present it as tables, charts or another application view |
| File-sharing application | Let users retrieve public files or authorize paid uploads from the browser |

These are application patterns, not ready-made interfaces included in the SDK. For example, a book reader still needs code that understands the book's format and displays its pages. The SDK supplies access to the file's data.

## How the browser connects

Two technologies make the direct connection possible:

- **WebAssembly (WASM)** runs the compiled Rust network client inside the browser. Your JavaScript or TypeScript calls the SDK rather than implementing networking, storage and encryption itself.
- **WebRTC** provides browser-to-node connections. The browser communicates directly with compatible Autonomi nodes rather than sending file data through your application's backend or a storage gateway.

```text
Your web application's interface
              |
       Browser SDK calls
              |
   WebAssembly network client
              |
      WebRTC connections
              |
        Autonomi nodes
```

You still serve the web application's HTML, JavaScript and WASM assets from a web host. The stored content comes from the Autonomi Network. Hosting the interface and storing its content are separate concerns.

The SDK includes mainnet connection information, so an application can connect without asking its users to find node addresses or run nodes themselves.

## Reading and displaying data

Public files are retrieved by address, without a wallet or payment. The SDK returns bytes and a browser `Blob`, which your application can turn into an image, a download or input for a document renderer.

Private files require their DataMap, the information needed to locate and decrypt the file. Your application must keep it private and retain it for future access; a wallet is not a substitute for that DataMap.

For a complete working example, follow [Retrieve Data in the Browser](how-to-guides/retrieve-data-in-browser.md). It downloads a public image and displays it in a small web page.

## Streaming and larger files

You do not have to load every file into memory before using it. The SDK provides range reads and streams, so an application can request parts of a file as it needs them.

For seekable audio and video, the SDK provides a service worker: a browser-managed script that connects a media element's requests to the SDK's file reader. This setup requires HTTPS or localhost and the application's page to remain open. Applications with an existing service worker must integrate the media handling with it.

Browser SDK 0.1.4 accepts uploads from 3 bytes up to 1 GB (1,000,000,000 bytes).

`download()` and `downloadAndSave()` buffer the whole file and use a default 1 GB `maxMemoryBytes` budget. You can pass a different budget, but the returned bytes and `Blob`, the resolved DataMap, caches and transport buffers need additional memory.

Streaming downloads and media do not have a fixed 1 GB cap. For bounded-memory downloads, use `client.streamAndSave(source, options)` or `client.openFile(file, options)` followed by `reader.pipeTo(destination, options)`. Use `reader.stream(options)` to consume a bounded stream in your application. Browser memory, storage and safe-integer limits remain practical constraints. Uploads from byte arrays may run out of memory before reaching the upload cap. The [browser SDK API documentation](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#stream-directly-to-disk) covers streaming saves, range reads, media setup and file-size limits.

## Uploading from a browser

The SDK also accepts browser files and byte arrays for public or private uploads. Your application supplies a payment provider to authorize storage payments; supported integrations include Ethers and Wagmi/Viem. A read-only application does not need these wallet integrations.

File uploads have additional browser requirements, including a worker for file processing and IndexedDB for temporary storage. Use the [browser SDK's upload documentation](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#upload-files) when adding uploads and payment handling.

## Network compatibility

The SDK and nodes must use compatible browser protocols—the rules they use to communicate. If a network upgrade makes those protocols incompatible, your application needs an SDK release that supports the changed protocol to keep connecting. Check the [browser SDK release notes](https://github.com/WithAutonomi/ant-browser-sdk/releases) when updating your application.

## Browser compatibility

The application needs a browser with the APIs used by its features, including WebAssembly and WebRTC. Media playback and file uploads need additional browser capabilities. The SDK provides a capability check, but available APIs alone do not guarantee that a browser can reach the nodes or has enough memory or storage for the operation.

The retrieval tutorial uses Chromium. Check the browsers you intend to support before depending on the same behavior elsewhere, particularly while the SDK is experimental.

## Related pages

- [Retrieve Data in the Browser](how-to-guides/retrieve-data-in-browser.md): build and run a public-image example.
- [Build with the SDKs](install.md): choose a library and connection arrangement for your application.
- [Node.js SDK](native/nodejs.md): connect directly from server-side JavaScript.
- [Keys, Addresses, and DataMaps](../core-concepts/keys-addresses-and-datamaps.md): public and private access to stored data.
