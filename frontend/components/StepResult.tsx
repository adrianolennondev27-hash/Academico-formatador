"use client";

import { useState } from "react";
import {
  AlertaOrtografia,
  AlertaGramatica,
  AlertaEstrutura,
  MetadadosABNT,
  gerarABNT,
  gerarABNTPDF,
  baixarBlob,
} from "@/lib/api";

interface Props {
  textoLimpo: string;
  metadados: MetadadosABNT;
  alertasOrtografia: AlertaOrtografia[];
  alertasGramatica: AlertaGramatica[];
  alertasEstrutura: AlertaEstrutura[];
  onBack: () => void;
  onReset: () => void;
}

export default function StepResult({
  textoLimpo,
  metadados,
  alertasOrtografia,
  alertasGramatica,
  alertasEstrutura,
  onBack,
  onReset,
}: Props) {
  const [gerandoWord, setGerandoWord] = useState(false);
  const [gerandoPDF, setGerandoPDF] = useState(false);
  const [baixado, setBaixado] = useState(false);
  const [erro, setErro] = useState("");

  const totalAlertas =
    alertasOrtografia.length + alertasGramatica.length + alertasEstrutura.length;

  async function handleGerarWord() {
    setGerandoWord(true);
    setErro("");
    try {
      const blob = await gerarABNT(metadados, textoLimpo);
      const nomeBase = metadados.titulo.trim()
        ? metadados.titulo.replace(/\s+/g, "_")
        : "trabalho";
      baixarBlob(blob, `${nomeBase}_ABNT.docx`);
      setBaixado(true);
    } catch {
      setErro("Erro ao gerar o Word. Verifique se o backend está rodando.");
    } finally {
      setGerandoWord(false);
    }
  }

  async function handleGerarPDF() {
    setGerandoPDF(true);
    setErro("");
    try {
      const blob = await gerarABNTPDF(metadados, textoLimpo);
      const nomeBase = metadados.titulo.trim()
        ? metadados.titulo.replace(/\s+/g, "_")
        : "trabalho";
      baixarBlob(blob, `${nomeBase}_ABNT.pdf`);
      setBaixado(true);
    } catch {
      setErro(
        "Erro ao gerar o PDF. Confirme que o LibreOffice está instalado e configurado."
      );
    } finally {
      setGerandoPDF(false);
    }
  }

  const processando = gerandoWord || gerandoPDF;

  return (
    <div className="space-y-6 animate-slide-up">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-slate-900 mb-1">
          Diagnóstico do texto
        </h2>
        <p className="text-slate-500 text-sm">
          {totalAlertas === 0
            ? "Nenhum alerta encontrado. Seu texto está impecável."
            : `Encontramos ${totalAlertas} ponto(s) de atenção.`}
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="p-4 rounded-xl bg-red-50 border border-red-100 text-center">
          <p className="text-2xl font-black text-red-700">
            {alertasEstrutura.length}
          </p>
          <p className="text-xs text-red-600 mt-1 font-medium">Estruturais</p>
        </div>
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-100 text-center">
          <p className="text-2xl font-black text-amber-700">
            {alertasGramatica.length}
          </p>
          <p className="text-xs text-amber-600 mt-1 font-medium">Gramática</p>
        </div>
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-100 text-center">
          <p className="text-2xl font-black text-blue-700">
            {alertasOrtografia.length}
          </p>
          <p className="text-xs text-blue-600 mt-1 font-medium">Ortografia</p>
        </div>
      </div>

      {alertasEstrutura.length > 0 && (
        <section>
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-600"></span>
            Estruturais ({alertasEstrutura.length})
          </h3>
          <ul className="space-y-2">
            {alertasEstrutura.map((a, i) => (
              <li
                key={i}
                className="p-4 bg-red-50/50 border-l-4 border-red-600 rounded-r-lg"
              >
                <p className="font-semibold text-red-800 text-sm">{a.regra}</p>
                <p className="text-sm text-red-700 mt-1">{a.dica}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {alertasGramatica.length > 0 && (
        <section>
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500"></span>
            Gramática e Pontuação ({alertasGramatica.length})
          </h3>
          <ul className="space-y-2">
            {alertasGramatica.map((a, i) => (
              <li
                key={i}
                className="p-4 bg-amber-50/50 border-l-4 border-amber-500 rounded-r-lg"
              >
                <p className="font-semibold text-amber-800 text-sm">{a.regra}</p>
                <p className="text-sm text-amber-700 mt-1">
                  Trecho:{" "}
                  <code className="bg-white px-2 py-0.5 rounded text-xs font-mono">
                    {a.trecho}
                  </code>
                </p>
                <p className="text-sm text-amber-700 mt-1">{a.dica}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {alertasOrtografia.length > 0 && (
        <section>
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-600"></span>
            Ortografia ({alertasOrtografia.length})
          </h3>
          <ul className="space-y-2">
            {alertasOrtografia.map((a, i) => (
              <li
                key={i}
                className="p-4 bg-blue-50/50 border-l-4 border-blue-600 rounded-r-lg"
              >
                <p className="font-semibold text-blue-800 text-sm">
                  <code className="bg-white px-2 py-0.5 rounded text-xs font-mono">
                    {a.palavra}
                  </code>
                </p>
                {a.sugestoes.length > 0 && (
                  <p className="text-sm text-blue-700 mt-1">
                    Sugestões: {a.sugestoes.join(", ")}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {erro && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {erro}
        </div>
      )}

      {baixado && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-xl animate-slide-up">
          <p className="text-sm font-semibold text-green-800">
            ✅ Documento baixado com sucesso!
          </p>
        </div>
      )}

      <div className="pt-4 border-t border-slate-200">
        <p className="text-sm font-semibold text-slate-700 mb-3 text-center">
          Escolha o formato do arquivo:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <button
            onClick={handleGerarWord}
            disabled={processando}
            className="px-6 py-4 bg-gradient-to-r from-blue-700 to-blue-600 text-white rounded-xl font-bold hover:from-blue-800 hover:to-blue-700 disabled:opacity-50 transition shadow-lg shadow-blue-700/30 flex items-center justify-center gap-2"
          >
            {gerandoWord ? "Gerando Word..." : "📄 Baixar em Word (.docx)"}
          </button>
          <button
            onClick={handleGerarPDF}
            disabled={processando}
            className="px-6 py-4 bg-gradient-to-r from-red-600 to-red-500 text-white rounded-xl font-bold hover:from-red-700 hover:to-red-600 disabled:opacity-50 transition shadow-lg shadow-red-600/30 flex items-center justify-center gap-2"
          >
            {gerandoPDF ? "Gerando PDF..." : "📄 Baixar em PDF"}
          </button>
        </div>
        <p className="text-xs text-slate-500 text-center mt-3">
          Word é editável · PDF é pronto para entrega
        </p>
      </div>

      <div className="flex justify-between pt-4 border-t border-slate-200">
        <button
          onClick={onBack}
          className="px-6 py-3 border border-slate-300 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition"
        >
          ← Voltar
        </button>
        <button
          onClick={onReset}
          className="px-6 py-3 bg-slate-800 text-white rounded-xl font-semibold hover:bg-slate-900 transition"
        >
          + Formatar novo trabalho
        </button>
      </div>
    </div>
  );
}