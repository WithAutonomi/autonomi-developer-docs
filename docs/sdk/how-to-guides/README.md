# SDK How-To Guides

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

<!-- verification:
  source_repo: ant-browser-sdk
  source_ref: v0.1.3
  source_commit: 813aa1817274551e3596038ffc8d2706672eba3b
  verified_date: 2026-10-27
  verification_mode: target-manifest
-->

These guides take you from your first download to storing files and handling upload payments, with practical examples you can adapt to your own application.

If you're still deciding how your application should connect, [Build with the SDKs](../install.md) explains the options.

## In a browser

- [Retrieve Data in the Browser](retrieve-data-in-browser.md): display a public image using the experimental browser SDK, without a wallet or local daemon.

## Through a local daemon

These guides use [antd](../use-antd.md), the local background service. For a first application, start the service, try a free download, then make a paid upload when you are ready. The remaining guides cover broader operations and application setup.

- [Start the Local Daemon](../start-the-local-daemon.md): install and run the service, then check the connection.
- [Retrieve Data from the Network](../retrieve-data-from-the-network.md): download a supplied public image without a wallet or payment.
- [Store Data on the Network](../store-data-on-the-network.md): configure upload payments, store a public payload and retrieve it again.
- [Store and Retrieve Data with the SDKs](store-and-retrieve-data.md): choose individual recipes for public data, private data and files after the introductory walkthroughs.
- [Use the Daemon as a Local Service](use-the-daemon-as-a-local-service.md): keep the background service running with a service manager.
- [Use External Signers for Upload Payments](use-external-signers-for-upload-payments.md): keep the signing key outside the local daemon.

## Next steps

- [Build with the SDKs](../install.md)
- [SDK Reference](../reference/README.md)
