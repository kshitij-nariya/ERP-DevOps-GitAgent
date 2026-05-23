import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ERP DevOps GitAgent",
  description: "Automated Odoo/ERP code review with GitAgent-defined agents"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
