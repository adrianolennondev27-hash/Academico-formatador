import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FVA — Formatador e Validador Acadêmico",
  description:
    "Converta formatos, formate trabalhos nas normas ABNT e valide ortografia, gramática e estrutura. Gratuito, privado e sem armazenamento de dados.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>{children}</body>
    </html>
  );
}