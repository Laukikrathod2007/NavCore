import React from "react";
import type { NextPage } from "next";
import Head from "next/head";
import { AdminDashboardView } from "../components/admin/AdminDashboardView";

const AdminPage: NextPage = () => {
  return (
    <>
      <Head>
        <title>NavCore Hospital Admin — Facility Management &amp; Telemetry</title>
        <meta name="description" content="Toggle doctor availability, manage hospital floor graph, and view real-time NavCore telemetry" />
        <link rel="icon" type="image/png" href="/assets/brand/navcore-emblem-icon.png" />
      </Head>
      <AdminDashboardView />
    </>
  );
};

export default AdminPage;
