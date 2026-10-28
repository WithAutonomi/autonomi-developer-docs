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
| File-sharing application | Open or create links and portable collections, then retrieve public or shared private files |
| Updatable catalogue or profile | Keep one lasting address while the content behind it changes |

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

## Sharing files and collections

An `ant://` link can identify one public file or describe a collection of files. The collection form carries a manifest: a portable list of file names and the information needed to retrieve each one. Your application can also open the same kind of collection from a `.ant` file.

A manifest does not upload or publish its files. Your application can create one from files it has already uploaded, then offer the link or `.ant` file to another person. The recipient can open the manifest and choose which entries to retrieve.

Public entries contain an address. An embedded entry contains the DataMap needed to read a private file. Anyone who receives a manifest with an embedded entry receives access to that private file, so protect that manifest as you would protect the DataMap itself.

See the released SDK documentation for [opening manifests and `ant://` links](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#manifests-and-ant-links) and [creating manifests and share links](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#creating-manifests-and-share-links).

## Choosing how to retrieve a file

You do not have to load every file into memory before using it. The SDK provides range reads and streams, so an application can request parts of a file as it needs them.

Choose the approach that matches the file and what your application needs to do with it:

- **Download it in one operation.** `download()` returns the complete file as bytes and a browser `Blob`; `downloadAndSave()` also opens a save flow for the user. Both hold the complete file in memory. They refuse files over 1 GB by default, but you can change that memory budget. The returned `Blob`, resolved DataMap, caches and network buffers need additional memory beyond the byte-array budget.
- **Save it as it arrives.** `streamAndSave()` writes directly to a destination selected by your application or the user. It does not create a complete in-memory copy, and streaming has no fixed file-size cap. The device still needs enough storage for the file.
- **Read only the parts you need.** `openFile()` provides range reads and a stream for applications such as document readers, archives and data viewers. Your application decides where those pieces go and how to present them.

For seekable audio and video, the SDK provides a service worker: a browser-managed script that connects a media element's requests to the SDK's file reader. Deploy the service worker shipped with the same SDK version as your application. This setup requires HTTPS or localhost and the application's page to remain open. Applications with an existing service worker must integrate the media handling with it.

See the released SDK documentation for [whole-file downloads and saves](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#download-and-save), [streaming saves](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#streaming-saves), [range reads](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#random-access-reads) and [seekable media](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#seekable-media).

## Uploading from a browser

The SDK also accepts browser files and byte arrays for public or private uploads. Your application supplies a payment provider to authorize storage payments; supported integrations include Ethers and Wagmi/Viem. A read-only application does not need these wallet integrations.

Uploads can be from 3 bytes up to 1 GB (1,000,000,000 bytes). Uploading a browser `File` or `Blob` processes it in a background worker and stages encrypted records in browser storage. Uploading a byte array holds the complete input in memory, so it may fail before reaching the upload limit.

If an upload stops after the wallet may have paid, do not immediately start the upload again. Keep the page open and let the user resume or discard the failed attempt. The SDK retains the prepared input and payment history, reuses confirmed payment where it can, and stops for explicit authorization if more payment is needed. This recovery state does not survive a page reload.

Use the released SDK's [upload documentation](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#upload-files) and [upload recovery guidance](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#resume-a-failed-upload) when adding uploads and payment handling.

## Keeping a reference up to date

A pointer gives your application one stable address that can refer to changing content. This is useful for a profile, catalogue or other record whose readers need a lasting address while its owner publishes updates.

The owner's secret controls that address, so your application must protect it. Creating or updating the pointer also costs a storage payment. Before the wallet continues, save the SDK's recovery checkpoint somewhere that survives a page reload. When that checkpoint captures the payment evidence, it can let the application finish the original paid update without paying again. It cannot recover evidence that was never saved: if the payment remains unresolved, reconcile it with the original wallet and do not start a new update.

Pointer ownership can also be transferred permanently. A successful write does not by itself prove that enough responsible nodes agree on the result. Applications that depend on that agreement must check the pointer's finality status. See the released SDK's [pointer and recovery documentation](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.4#pointers-and-payment-recovery) before adding pointer writes.

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
