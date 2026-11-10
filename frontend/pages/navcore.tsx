import React from "react";
import type { NextPage } from "next";
import Head from "next/head";
import { NavCoreView } from "../components/navcore/NavCoreView";
import { publicAsset } from "../lib/urls";

const NavCorePage: NextPage = () => {
  return (
    <>
      <Head>
        <title>NavCore — Multilingual Hospital Navigation</title>
        <meta name="description" content="Offline dual-memory touchscreen navigation for Indian hospitals" />
        <link rel="icon" type="image/png" href={publicAsset("/assets/brand/navcore-emblem-icon.png")} />
      </Head>
      <NavCoreView />
    </>
  );
};

export default NavCorePage;

