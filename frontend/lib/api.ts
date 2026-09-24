const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export interface AlertaOrtografia {
  palavra: string;
  sugestoes: string[];
}

export interface AlertaGramatica {
  tipo: string;
  regra: string;
  trecho: string;
  dica: string;
}

export interface AlertaEstrutura {
  tipo: string;
  regra: string;
  dica: string;
}

export interface MetadadosABNT {
  instituicao: string;
  curso: string;
  titulo: string;
  aluno: string;
  professor: string;
  cidade: string;
  ano: string;
  incluir_folha_rosto: boolean;
  natureza_trabalho: string;
  incluir_sumario: boolean;
}

export async function limparTexto(texto: string): Promise<string> {
  const res = await fetch(`${API_URL}/clean`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!res.ok) throw new Error("Erro ao limpar texto");
  const data = await res.json();
  return data.texto_limpo;
}

export async function uploadPDF(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Erro ao processar PDF");
  const data = await res.json();
  return data.texto_extraido;
}

export async function validarTexto(texto: string) {
  const res = await fetch(`${API_URL}/validar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!res.ok) throw new Error("Erro na validação");
  return res.json();
}

export async function validarEstrutura(texto: string, tipoTrabalho: string) {
  const res = await fetch(`${API_URL}/validar-estrutura`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto, tipo_trabalho: tipoTrabalho }),
  });
  if (!res.ok) throw new Error("Erro na validação estrutural");
  return res.json();
}

export async function gerarABNT(metadados: MetadadosABNT, textoLimpo: string) {
  const res = await fetch(`${API_URL}/gerar-abnt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...metadados, texto_limpo: textoLimpo }),
  });
  if (!res.ok) throw new Error("Erro ao gerar documento");
  return res.blob();
}

export async function gerarABNTPDF(metadados: MetadadosABNT, textoLimpo: string) {
  const res = await fetch(`${API_URL}/gerar-abnt-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...metadados, texto_limpo: textoLimpo }),
  });
  if (!res.ok) throw new Error("Erro ao gerar PDF");
  return res.blob();
}

export async function converterArquivo(
  file: File,
  formatoSaida: "docx" | "pdf" | "odt" | "doc"
): Promise<Blob> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("formato_saida", formatoSaida);

  const res = await fetch(`${API_URL}/converter`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let detalhe = "Erro na conversão";
    try {
      const err = await res.json();
      if (err?.detail) detalhe = err.detail;
    } catch {}
    throw new Error(detalhe);
  }

  return res.blob();
}

export function baixarBlob(blob: Blob, nomeArquivo: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}