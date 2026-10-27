# Retrieve Data in the Browser

<!-- verification:
  source_repo: ant-browser-sdk
  source_ref: v0.1.3
  source_commit: 813aa1817274551e3596038ffc8d2706672eba3b
  verified_date: 2026-10-27
  verification_mode: target-manifest
-->

{% hint style="info" %}
**Experimental SDK.** The browser SDK and its direct-browser protocol are experimental.
{% endhint %}

Retrieve a public image from the Autonomi Network and display it in a web page using the browser SDK. The connection runs in the browser through WebAssembly (WASM) and WebRTC; you do not need a wallet or a local daemon.

Use this example when your application needs to read and display data in a browser. The [Browser SDK overview](../build-in-browser.md) explains other uses. For server-side JavaScript, use the [Node.js SDK](../native/nodejs.md); for a separate network service, use [local-daemon clients](../use-antd.md).

## Prerequisites

- Node.js 22.12 or later and npm on your development computer. Visitors to the finished page do not need Node.js.
- A Chromium-based browser with WebAssembly and WebRTC enabled.
- An internet connection that permits WebRTC connections to public nodes.

This example only reads existing public data. It does not configure a wallet or request payment.

## Steps

### 1. Create the project

Vite serves the JavaScript and WASM assets during development and bundles them for deployment.

This tutorial uses browser SDK 0.1.3 and Vite 8.2.0. The commands save these exact versions so reinstalling the project does not select a different version of either package.

In a terminal, run:

```bash
mkdir autonomi-browser-demo
cd autonomi-browser-demo
npm init -y
npm install --save-exact @withautonomi/ant-browser-sdk@0.1.3
npm install --save-dev --save-exact vite@8.2.0
```

### 2. Add the page

Create `index.html` in the project directory:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Autonomi browser download</title>
  </head>
  <body>
    <h1>Download from Autonomi</h1>
    <button id="download" type="button">Download Lucky</button>
    <p id="status" role="status">Ready.</p>
    <img id="preview" alt="Lucky the dog" hidden style="max-width: 100%;" />
    <script type="module" src="/main.js"></script>
  </body>
</html>
```

### 3. Connect and retrieve the image

Create `main.js` alongside `index.html`:

```javascript
import {
  AutonomiClient,
  getBrowserCapabilities,
} from "@withautonomi/ant-browser-sdk";

const address =
  "711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a";
const button = document.querySelector("#download");
const status = document.querySelector("#status");
const image = document.querySelector("#preview");
let imageUrl;

button.addEventListener("click", async () => {
  button.disabled = true;
  let client;
  const controller = new AbortController();
  const timeout = setTimeout(() => {
    controller.abort(new Error("Download timed out after three minutes."));
  }, 180_000);

  try {
    const support = getBrowserCapabilities().operations.download;
    if (!support.available) {
      throw new Error(`Missing browser features: ${support.missing.join(", ")}`);
    }

    status.textContent = "Connecting to Autonomi…";
    client = await AutonomiClient.connect({ signal: controller.signal });

    status.textContent = "Downloading Lucky…";
    const result = await client.download(address, { signal: controller.signal });

    // This example's known file is a JPEG. Its address does not supply a MIME type.
    const blob = new Blob([result.bytes], { type: "image/jpeg" });
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    imageUrl = URL.createObjectURL(blob);
    image.src = imageUrl;
    image.hidden = false;
    status.textContent = `Downloaded ${result.bytes.length} bytes.`;
  } catch (error) {
    status.textContent = `Download failed: ${
      error instanceof Error ? error.message : String(error)
    }`;
    console.error(error);
  } finally {
    clearTimeout(timeout);
    client?.close();
    button.disabled = false;
  }
});
```

The connection uses the SDK's bundled mainnet addresses. The capability check reports missing browser APIs; it does not test whether your connection can reach the nodes.

This example connects for each download to keep cleanup simple. An application that reads multiple files would usually connect once and reuse the client, then call `close()` when it is no longer needed.

The image's public address identifies its data, not its original filename or media type. The example supplies `image/jpeg` because this particular file is a JPEG.

### 4. Run the app

Start the development server:

```bash
npx vite --host 127.0.0.1 --port 5179 --strictPort
```

Open `http://127.0.0.1:5179` and select **Download Lucky**. The page loads the WASM client, connects, and retrieves the image. The button stays disabled while the operation is running.

On success, Lucky's image appears with:

```text
Downloaded 138931 bytes.
```

The example stops waiting after three minutes and closes its client on both success and failure. That timeout is an application choice, not an SDK limit.

### 5. Build for deployment

Generate the static site and preview it locally:

```bash
npx vite build
npx vite preview --host 127.0.0.1 --port 5180 --strictPort
```

Open `http://127.0.0.1:5180` and repeat the download. To deploy, publish the contents of `dist/` to an HTTPS static host, including the generated WASM and JavaScript assets. Vite's preview command is for checking the build locally, not running a production server.

## Verify it worked

Confirm that Lucky's image appears, the status reads `Downloaded 138931 bytes.`, and the download button becomes available again. The development server and the production preview should display the same image.

The browser retrieves the data directly from Autonomi nodes. Vite serves your application and its WASM assets, not the image file.

## Common errors

**Missing browser features:** use a Chromium-based browser with WebAssembly and WebRTC enabled. The message lists the missing APIs.

**WASM initialization fails:** open the app through the development server rather than opening `index.html` as a local file. In a deployed build, check that the `.wasm` request returns the generated binary, not an HTML fallback page.

**Node protocol not supported:** an error saying `upgrade ant-node to a version advertising chunk_protocol` means the contacted node lacks a capability this SDK needs. On the public Autonomi Network, updating those nodes is not something your application controls. Check the [browser SDK release notes](https://github.com/WithAutonomi/ant-browser-sdk/releases) for compatibility guidance; if they do not resolve the problem, report the full error to the SDK maintainers.

**Connection failure or timeout:** check whether your connection permits WebRTC traffic. A failure to reach nodes or retrieve the file does not establish that the file is missing. Inspect the browser console for the original error, then retry when connectivity is available.

## Next steps

- [Browser SDK documentation](https://github.com/WithAutonomi/ant-browser-sdk/tree/v0.1.3): upload, wallet, private-file and media APIs for the same experimental release.
- [Browser SDK](../build-in-browser.md): capabilities, application ideas and how browser connections work.
- [Build with the SDKs](../install.md): compare application connection options.
- [Keys, Addresses, and DataMaps](../../core-concepts/keys-addresses-and-datamaps.md): understand public addresses and private-file access.
