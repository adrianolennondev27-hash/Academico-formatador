"use client";

import { useState } from "react";
import Logo from "@/components/Logo";
import StepText from "@/components/StepText";
import StepConfig from "@/components/StepConfig";
import StepResult from "@/components/StepResult";
import {
  AlertaOrtografia,
  AlertaGramatica,
  AlertaEstrutura,
  MetadadosABNT,
} from "@/lib/api";

const APP_NAME = "FVA";
const APP_SUBTITLE = "Formatador e Validador Acadêmico";
const APP_TAGLINE =
  "Converta formatos, formate em ABNT e valide seu texto em segundos. " +
  "Gratuito, privado, sem armazenamento de dados.";

export default function Home() {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [textoLimpo, setTextoLimpo] = useState("");
  const [tipoTrabalho, setTipoTrabalho] = useState("resenha");
  const [metadados, setMetadados] = useState<MetadadosABNT>({
    instituicao: "",
    curso: "",
    titulo: "",
    aluno: "",
    professor: "",
    cidade: "",
    ano: new Date().getFullYear().toString(),
    incluir_folha_rosto: false,
    natureza_trabalho: "",
    incluir_sumario: false,
  });
  const [alertasOrtografia, setAlertasOrtografia] = useState<AlertaOrtografia[]>([]);
  const [alertasGramatica, setAlertasGramatica] = useState<AlertaGramatica[]>([]);
  const [alertasEstrutura, setAlertasEstrutura] = useState<AlertaEstrutura[]>([]);
  const [resetKey, setResetKey] = useState(0);

  function handleReset() {
    setStep(1);
    setTextoLimpo("");
    setTipoTrabalho("resenha");
    setMetadados({
      instituicao: "",
      curso: "",
      titulo: "",
      aluno: "",
      professor: "",
      cidade: "",
      ano: new Date().getFullYear().toString(),
      incluir_folha_rosto: false,
      natureza_trabalho: "",
      incluir_sumario: false,
    });
    setAlertasOrtografia([]);
    setAlertasGramatica([]);
    setAlertasEstrutura([]);
    setResetKey((k) => k + 1);
  }

  const steps = [
    { n: 1, label: "Upload" },
    { n: 2, label: "Configuração" },
    { n: 3, label: "Resultado" },
  ];

  return (
    <main className="min-h-screen flex flex-col">
      <header className="w-full border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Logo size={44} />
          <div className="hidden md:flex items-center gap-2 text-xs text-slate-500">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Processamento local e privado
          </div>
        </div>
      </header>

      <div className="flex-1 max-w-6xl w-full mx-auto px-6 py-10">
        <div className="text-center mb-10 animate-slide-up">
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 mb-3 tracking-tight">
            {APP_NAME}{" "}
            <span className="bg-gradient-to-r from-blue-700 to-red-600 bg-clip-text text-transparent">
              {APP_SUBTITLE}
            </span>
          </h1>
          <p className="text-slate-600 max-w-2xl mx-auto">{APP_TAGLINE}</p>
        </div>

        <div className="flex justify-center items-center gap-4 mb-10">
          {steps.map((s, i) => (
            <div key={s.n} className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                    step === s.n
                      ? "bg-blue-700 text-white shadow-lg shadow-blue-700/30 scale-110"
                      : step > s.n
                      ? "bg-green-500 text-white"
                      : "bg-slate-200 text-slate-500"
                  }`}
                >
                  {step > s.n ? "✓" : s.n}
                </div>
                <span
                  className={`text-sm font-medium ${
                    step >= s.n ? "text-slate-900" : "text-slate-400"
                  }`}
                >
                  {s.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`h-0.5 w-12 rounded ${
                    step > s.n ? "bg-green-500" : "bg-slate-200"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 p-8 md:p-10 animate-slide-up">
          {step === 1 && (
            <StepText
              key={`step-text-${resetKey}`}
              onNext={(texto) => {
                setTextoLimpo(texto);
                setStep(2);
              }}
            />
          )}
          {step === 2 && (
            <StepConfig
              key={`step-config-${resetKey}`}
              tipoTrabalho={tipoTrabalho}
              setTipoTrabalho={setTipoTrabalho}
              metadados={metadados}
              setMetadados={setMetadados}
              onBack={() => setStep(1)}
              onNext={(ortografia, gramatica, estrutura) => {
                setAlertasOrtografia(ortografia);
                setAlertasGramatica(gramatica);
                setAlertasEstrutura(estrutura);
                setStep(3);
              }}
              textoLimpo={textoLimpo}
            />
          )}
          {step === 3 && (
            <StepResult
              key={`step-result-${resetKey}`}
              textoLimpo={textoLimpo}
              metadados={metadados}
              alertasOrtografia={alertasOrtografia}
              alertasGramatica={alertasGramatica}
              alertasEstrutura={alertasEstrutura}
              onBack={() => setStep(2)}
              onReset={handleReset}
            />
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className="bg-white rounded-xl p-4 border border-slate-100 text-center">
            <p className="text-2xl font-black text-blue-700">100%</p>
            <p className="text-xs text-slate-500 mt-1">Gratuito</p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-100 text-center">
            <p className="text-2xl font-black text-blue-700">&lt; 30s</p>
            <p className="text-xs text-slate-500 mt-1">Para gerar o documento</p>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-100 text-center">
            <p className="text-2xl font-black text-red-600">Zero</p>
            <p className="text-xs text-slate-500 mt-1">Dados armazenados</p>
          </div>
        </div>
      </div>

      <footer className="text-center text-xs text-slate-400 py-6">
        {APP_NAME} — {APP_SUBTITLE} · Processamento stateless em memória
      </footer>
    </main>
  );
}