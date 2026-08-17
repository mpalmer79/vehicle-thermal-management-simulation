import type { Metadata } from "next";
import "./globals.css";
import "./ui5.css";
import { AppShell } from "@/components/app-shell";

export const metadata: Metadata = {
  title: { default: "VTMS | Vehicle Thermal Management Simulation", template: "%s | VTMS" },
  description: "Physics-based automotive thermal-management simulation and validation platform.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><AppShell>{children}</AppShell></body></html>;
}
