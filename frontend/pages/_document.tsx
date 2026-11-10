
import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* Load Google Fonts asynchronously to never block FOUC removal script */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        {/* Use media="print" + onLoad trick for async font loading — prevents render-blocking */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;1,400;1,600&family=JetBrains+Mono:wght@400;500;600&display=swap"
          media="print"
          // @ts-ignore
          onLoad="this.media='all'"
        />
        {/* Fallback for no-JS: system fonts already defined in globals.css */}
        <noscript>
          <link
            rel="stylesheet"
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;1,400;1,600&family=JetBrains+Mono:wght@400;500;600&display=swap"
          />
        </noscript>
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
