import React, { useEffect } from "react";
import type { NextPage } from "next";
import Head from "next/head";
import { Navbar } from "../components/layout/Navbar";
import { HeroSection } from "../components/landing/HeroSection";
import { StatsCounterSection } from "../components/landing/StatsCounterSection";
import { TrustBar } from "../components/landing/TrustBar";
import { DualMemorySection } from "../components/landing/DualMemorySection";
import { UseCasesSection } from "../components/landing/UseCasesSection";
import { InteractiveNavCoreDemo } from "../components/landing/InteractiveNavCoreDemo";
import { BenchmarkSection } from "../components/landing/BenchmarkSection";
import { WorkflowPipeline } from "../components/landing/WorkflowPipeline";
import { MultiFloorExplorer } from "../components/landing/MultiFloorExplorer";
import { CodeIntegration } from "../components/landing/CodeIntegration";
import { BentoFeatures } from "../components/landing/BentoFeatures";
import { HardwareSpecs } from "../components/landing/HardwareSpecs";
import { FAQSection } from "../components/landing/FAQSection";
import { Footer } from "../components/layout/Footer";
import { FloatingAgentPill } from "../components/landing/FloatingAgentPill";

const HomePage: NextPage = () => {
  useEffect(() => {
    const sections = document.querySelectorAll<HTMLElement>(".marketing-page > section");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });

    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  return (
    <>
      <Head>
        <title>NavCore | Real-Time Multilingual Spatial Search for Physical Spaces</title>
        <meta
          name="description"
          content="Sub-10ms offline indoor spatial retrieval engine for Indian physical spaces. Speaks Hindi, Marathi, Hinglish, & English with zero Wi-Fi and zero junction hallucinations."
        />
        <link rel="icon" type="image/png" href="/assets/brand/navcore-emblem-icon.png" />
      </Head>

      <div className="marketing-page" style={{ minHeight: "100vh", backgroundColor: "#fafafa", position: "relative" }}>
        {/* Navigation Bar with Top Announcement */}
        <Navbar />

        {/* Hero route story */}
        <HeroSection />

        {/* Stats Section with Scroll Count-Up Animation matching Screenshot 2 */}
        <StatsCounterSection />

        {/* Trust & Hospital Ecosystem */}
        <TrustBar />

        {/* Why NavCore is Fundamentally Different matching Screenshot 3 */}
        <DualMemorySection />

        {/* Use Cases with Tabs & Floating Latency Badge */}
        <UseCasesSection />

        {/* Interactive NavCore Sandbox */}
        <InteractiveNavCoreDemo />

        {/* 200-Query Benchmark Results */}
        <BenchmarkSection />

        {/* 7-Node LangGraph Edge Pipeline */}
        <WorkflowPipeline />

        {/* Multi-Floor Hospital Map Visualizer */}
        <MultiFloorExplorer />

        {/* Developer Experience & Code Integration */}
        <CodeIntegration />

        {/* Physical Infrastructure Bento Grid */}
        <BentoFeatures />

        {/* Edge Hardware Compatibility Specs */}
        <HardwareSpecs />

        {/* Frequently Asked Questions */}
        <FAQSection />

        {/* Moss-style Rich Footer */}
        <Footer />

        <FloatingAgentPill />

      </div>
    </>
  );
};

export default HomePage;
