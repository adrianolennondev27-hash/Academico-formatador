"use client";

import { useState } from "react";
import {
  MetadadosABNT,
  AlertaOrtografia,
  AlertaGramatica,
  AlertaEstrutura,
  validarTexto,
  validarEstrutura,
} from "@/lib/api";

interface Props {
  tipoTrabalho: string;
  setTipoTrabalho: (v: string) => void;
  metadados: MetadadosABNT;
  setMetadados: (m: MetadadosABNT) => void;
  textoLimpo: string;
  onBack: () => void;
  onNext: (
    ortografia: AlertaOrtografia[],
    gramatica: AlertaGramatica[],
    estrutura: AlertaEstrutura[]
  ) => void;
}

const TIPOS = [
  { value: "resenha", label: "Resenha Crítica", desc: "Análise com posicionamento" },
  { value: "tcc", label: "TCC", desc: "Trabalho de Conclusão de Curso" },
  { value: "artigo", label: "Artigo Científico", desc: "Publicação acadêmica" },
  { value: "resumo", label: "Resumo", desc: "Síntese em terceira pessoa" },
  { value: "trabalho", label: "Trabalho Acadêmico", desc: "Atividade de disciplina" },
];

export default function StepConfig({
  tipoTrabalho,
  setTipoTrabalho,
  metadados,
  setMetadados,
  textoLimpo,
  onBack,
  onNext,
}: Props) {
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  function updateCampo(campo: keyof MetadadosABNT, valor: string | boolean) {
    setMetadados({ ...metadados, [campo]: valor });
  }

  async function handleAnalisar() {
    const obrigatorios: (keyof MetadadosABNT)[] = [
      "instituicao",
      "curso",
      "titulo",
      "aluno",
      "cidade",
      "ano",
    ];
    const faltando = obrigatorios.filter((k) => !String(metadados[k]).trim());
    if (faltando.length > 0) {
      setErro(`Preencha os campos obrigatórios: ${faltando.join(", ")}`);
      return;
    }

    setCarregando(true);
    setErro("");
    try {
      const [val, est] = await Promise.all([
        validarTexto(textoLimpo),
        validarEstrutura(textoLimpo, tipoTrabalho),
      ]);
      onNext(val.ortografia, val.gramatica, est.alertas);
    } catch {
      setErro("Erro na validação. Verifique se o backend está rodando.");
    } finally {
      setCarregando(false);
    }
  }

  const campos: { key: keyof MetadadosABNT; label: string; obrigatorio: boolean }[] = [
    { key: "instituicao", label: "Instituição", obrigatorio: true },
    { key: "curso", label: "Curso", obrigatorio: true },
    { key: "titulo", label: "Título do Trabalho", obrigatorio: true },
    { key: "aluno", label: "Nome do Aluno (separe múltiplos por vírgula)", obrigatorio: true },
    { key: "professor", label: "Professor(a)", obrigatorio: false },
    { key: "cidade", label: "Cidade", obrigatorio: true },
    { key: "ano", label: "Ano", obrigatorio: true },
  ];

  return (
    <div className="space-y-6 animate-slide-up">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-slate-900 mb-1">
          Configuração ABNT
        </h2>
        <p className="text-slate-500 text-sm">
          Escolha o tipo de trabalho e preencha os metadados.
        </p>
      </div>

      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-3">
          Tipo de trabalho
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {TIPOS.map((t) => (
            <button
              key={t.value}
              type="button"
              onClick={() => setTipoTrabalho(t.value)}
              className={`p-4 rounded-xl border-2 text-left transition-all ${
                tipoTrabalho === t.value
                  ? "border-blue-700 bg-blue-50 shadow-md shadow-blue-700/10"
                  : "border-slate-200 bg-white hover:border-blue-300"
              }`}
            >
              <p className={`font-semibold text-sm ${tipoTrabalho === t.value ? "text-blue-800" : "text-slate-800"}`}>
                {t.label}
              </p>
              <p className="text-[10px] text-slate-500 mt-1 leading-tight">{t.desc}</p>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-3">
          Dados do trabalho
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {campos.map((c) => (
            <div key={c.key}>
              <label className="block text-xs font-medium text-slate-600 mb-1">
                {c.label} {c.obrigatorio && <span className="text-red-500">*</span>}
              </label>
              <input
                type="text"
                value={String(metadados[c.key])}
                onChange={(e) => updateCampo(c.key, e.target.value)}
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm"
              />
            </div>
          ))}
        </div>
      </div>

      {/* ÁREA DA FOLHA DE ROSTO */}
      <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-4">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="folha-rosto"
            checked={metadados.incluir_folha_rosto}
            onChange={(e) => updateCampo("incluir_folha_rosto", e.target.checked)}
            className="w-5 h-5 text-blue-700 rounded focus:ring-blue-500 cursor-pointer"
          />
          <label htmlFor="folha-rosto" className="text-sm font-semibold text-slate-800 cursor-pointer">
            Incluir Folha de Rosto
          </label>
        </div>

        {metadados.incluir_folha_rosto && (
          <div className="animate-slide-up">
            <label className="block text-xs font-medium text-slate-600 mb-1">
              Natureza do Trabalho (Ex: Trabalho apresentado à disciplina de História do Direito...)
            </label>
            <textarea
              value={metadados.natureza_trabalho}
              onChange={(e) => updateCampo("natureza_trabalho", e.target.value)}
              rows={3}
              placeholder="Descreva a finalidade do trabalho para constar na Folha de Rosto..."
              className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm resize-y"
            />
          </div>
        )}
      </div>

      {/* ÁREA DO SUMÁRIO */}
      <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-4">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="sumario"
            checked={metadados.incluir_sumario}
            onChange={(e) => updateCampo("incluir_sumario", e.target.checked)}
            className="w-5 h-5 text-blue-700 rounded focus:ring-blue-500 cursor-pointer"
          />
          <label htmlFor="sumario" className="text-sm font-semibold text-slate-800 cursor-pointer">
            Incluir Sumário
          </label>
        </div>

        {metadados.incluir_sumario && (
          <div className="text-xs text-slate-600 animate-slide-up leading-relaxed">
            <strong>Como funciona:</strong> o sistema detecta automaticamente os títulos do texto
            que estiverem numerados (ex: <code className="bg-white px-1 rounded">1. INTRODUÇÃO</code>,{" "}
            <code className="bg-white px-1 rounded">2. DESENVOLVIMENTO</code>,{" "}
            <code className="bg-white px-1 rounded">2.1. Contexto</code>) e gera o sumário.
            Certifique-se de que o texto tenha títulos numerados.
          </div>
        )}
      </div>

      {erro && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {erro}
        </div>
      )}

      <div className="flex justify-between pt-2">
        <button
          onClick={onBack}
          className="px-6 py-3 border border-slate-300 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition"
        >
          ← Voltar
        </button>
        <button
          onClick={handleAnalisar}
          disabled={carregando}
          className="px-8 py-3 bg-gradient-to-r from-blue-700 to-blue-600 text-white rounded-xl font-semibold hover:from-blue-800 hover:to-blue-700 disabled:opacity-50 transition shadow-lg shadow-blue-700/20"
        >
          {carregando ? "Analisando..." : "Analisar e validar →"}
        </button>
      </div>
    </div>
  );
}