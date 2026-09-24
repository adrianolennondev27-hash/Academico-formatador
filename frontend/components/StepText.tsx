"use client";

import { useState, useRef, DragEvent } from "react";
import { limparTexto, uploadPDF, converterArquivo } from "@/lib/api";

interface Props {
  onNext: (textoLimpo: string) => void;
}

type FormatoSaida = "docx" | "pdf" | "odt";

const FORMATOS_SAIDA: { value: FormatoSaida; label: string }[] = [
  { value: "docx", label: "Word (.docx)" },
  { value: "pdf", label: "PDF" },
  { value: "odt", label: "ODT (LibreOffice)" },
];

export default function StepText({ onNext }: Props) {
  // ====================================================================
  // BLOCO SUPERIOR — CONVERSÃO PURA (PDF↔Word, Word→ODT, etc.)
  // Estado COMPLETAMENTE isolado. Nada daqui desce para o fluxo ABNT.
  // ====================================================================
  const [convArquivo, setConvArquivo] = useState<File | null>(null);
  const [convFormato, setConvFormato] = useState<FormatoSaida>("docx");
  const [convCarregando, setConvCarregando] = useState(false);
  const [convErro, setConvErro] = useState("");
  const [convDragging, setConvDragging] = useState(false);
  const [convBaixado, setConvBaixado] = useState(false);
  const convInputRef = useRef<HTMLInputElement>(null);

  async function handleConverter() {
    if (!convArquivo) {
      setConvErro("Selecione um arquivo para converter.");
      return;
    }
    setConvCarregando(true);
    setConvErro("");
    setConvBaixado(false);
    try {
      const blob = await converterArquivo(convArquivo, convFormato);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `convertido.${convFormato}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setConvBaixado(true);
    } catch {
      setConvErro(
        "Erro na conversão. Verifique se o LibreOffice está instalado e se o backend está rodando."
      );
    } finally {
      setConvCarregando(false);
    }
  }

  function handleConvDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setConvDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setConvArquivo(file);
      setConvBaixado(false);
      setConvErro("");
    }
  }

  // ====================================================================
  // BLOCO INFERIOR — FLUXO ABNT (comportamento existente mantido)
  // Estado COMPLETAMENTE isolado. Nada daqui sobe para a conversão pura.
  // ====================================================================
  const [texto, setTexto] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");
  const [dragging, setDragging] = useState(false);
  const [nomeArquivo, setNomeArquivo] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleLimpar() {
    if (!texto.trim()) {
      setErro("Cole ou envie um arquivo antes de continuar.");
      return;
    }
    setCarregando(true);
    setErro("");
    try {
      const limpo = await limparTexto(texto);
      setTexto(limpo);
      setTimeout(() => onNext(limpo), 300);
    } catch {
      setErro("Erro ao limpar o texto. Verifique se o backend está rodando.");
    } finally {
      setCarregando(false);
    }
  }

  async function processarArquivo(file: File) {
    setCarregando(true);
    setErro("");
    setNomeArquivo(file.name);
    try {
      if (file.name.toLowerCase().endsWith(".pdf")) {
        const extraido = await uploadPDF(file);
        setTexto(extraido);
      } else {
        const conteudo = await file.text();
        setTexto(conteudo);
      }
    } catch {
      setErro("Erro ao processar o arquivo. Verifique se o backend está rodando.");
    } finally {
      setCarregando(false);
    }
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) processarArquivo(file);
  }

  function handleDragOver(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(true);
  }

  function handleDragLeave() {
    setDragging(false);
  }

  return (
    <div className="space-y-10 animate-slide-up">
      {/* ================================================================
          BLOCO 1 — CONVERSÃO PURA (sem ABNT)
          ================================================================ */}
      <section className="rounded-2xl border-2 border-slate-200 bg-slate-50/60 p-6 md:p-8">
        <div className="mb-5">
          <h2 className="text-xl font-bold text-slate-900 mb-1">
            Conversão de formato
          </h2>
          <p className="text-slate-500 text-sm">
            Converta PDF, Word ou ODT de um formato para outro.{" "}
            <strong>Nenhuma formatação ABNT é aplicada aqui.</strong>
          </p>
        </div>

        <div
          onDrop={handleConvDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setConvDragging(true);
          }}
          onDragLeave={() => setConvDragging(false)}
          onClick={() => convInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${
            convDragging
              ? "border-blue-600 bg-blue-50 scale-[1.01]"
              : "border-slate-300 bg-white hover:border-blue-400 hover:bg-blue-50/40"
          }`}
        >
          <input
            ref={convInputRef}
            type="file"
            accept=".pdf,.doc,.docx,.odt"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                setConvArquivo(file);
                setConvBaixado(false);
                setConvErro("");
              }
            }}
            className="hidden"
          />
          <div className="flex flex-col items-center gap-2">
            <div
              className={`w-12 h-12 rounded-full flex items-center justify-center transition ${
                convDragging ? "bg-blue-600" : "bg-blue-100"
              }`}
            >
              <svg
                className={`w-6 h-6 ${convDragging ? "text-white" : "text-blue-700"}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </div>
            <p className="font-semibold text-slate-800 text-sm">
              {convDragging
                ? "Solte o arquivo aqui"
                : "Arraste o arquivo para converter"}
            </p>
            <p className="text-xs text-slate-500">
              ou clique para selecionar · PDF, DOC, DOCX ou ODT
            </p>
            {convArquivo && (
              <span className="mt-2 text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
                📎 {convArquivo.name}
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-col md:flex-row md:items-center gap-3 mt-5">
          <label className="text-sm font-medium text-slate-700">
            Converter para:
          </label>
          <select
            value={convFormato}
            onChange={(e) => {
              setConvFormato(e.target.value as FormatoSaida);
              setConvBaixado(false);
            }}
            className="border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-blue-500 outline-none"
          >
            {FORMATOS_SAIDA.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>
          <button
            onClick={handleConverter}
            disabled={!convArquivo || convCarregando}
            className="md:ml-auto px-6 py-2.5 bg-blue-700 text-white rounded-lg font-semibold text-sm hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-md shadow-blue-700/20"
          >
            {convCarregando ? "Convertendo..." : "Converter e baixar"}
          </button>
        </div>

        {convErro && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {convErro}
          </div>
        )}
        {convBaixado && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
            ✓ Conversão concluída. O download foi iniciado.
          </div>
        )}
      </section>

      {/* ================================================================
          BLOCO 2 — FLUXO ABNT (comportamento original mantido)
          ================================================================ */}
      <section className="rounded-2xl border-2 border-slate-200 bg-white p-6 md:p-8">
        <div className="text-center mb-5">
          <h2 className="text-xl font-bold text-slate-900 mb-1">
            Formatar em ABNT
          </h2>
          <p className="text-slate-500 text-sm">
            Envie o arquivo ou cole o texto. Ele será limpo, validado e
            formatado nas normas ABNT.
          </p>
        </div>

        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => inputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${
            dragging
              ? "border-blue-600 bg-blue-50 scale-[1.01]"
              : "border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/50"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.txt,.docx"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) processarArquivo(file);
            }}
            className="hidden"
          />
          <div className="flex flex-col items-center gap-3">
            <div
              className={`w-14 h-14 rounded-full flex items-center justify-center transition ${
                dragging ? "bg-blue-600 animate-pulse-ring" : "bg-blue-100"
              }`}
            >
              <svg
                className={`w-7 h-7 ${dragging ? "text-white" : "text-blue-700"}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M7 16a4 4 0 01-.88-7.9A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <div>
              <p className="font-semibold text-slate-800">
                {dragging ? "Solte o arquivo aqui" : "Arraste seu arquivo aqui"}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                ou clique para selecionar · PDF, TXT ou DOCX
              </p>
            </div>
            {nomeArquivo && (
              <span className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
                📎 {nomeArquivo}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-400 my-5">
          <div className="flex-1 h-px bg-slate-200" />
          <span>ou cole o texto diretamente</span>
          <div className="flex-1 h-px bg-slate-200" />
        </div>

        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Cole aqui o texto bruto de qualquer fonte..."
          rows={10}
          className="w-full p-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-y text-sm leading-relaxed"
        />

        {erro && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {erro}
          </div>
        )}

        <div className="flex justify-between items-center mt-5">
          <span className="text-xs text-slate-500">
            {texto.length > 0 &&
              `${texto.split(/\s+/).filter(Boolean).length} palavras`}
          </span>
          <button
            onClick={handleLimpar}
            disabled={carregando}
            className="px-8 py-3 bg-gradient-to-r from-blue-700 to-blue-600 text-white rounded-xl font-semibold hover:from-blue-800 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-lg shadow-blue-700/20"
          >
            {carregando ? "Processando..." : "Limpar texto e continuar →"}
          </button>
        </div>
      </section>
    </div>
  );
}