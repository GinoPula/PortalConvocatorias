import { useEffect, useState } from "react";
import { api, ApiError } from "../../api/client";
import type { EvaluacionPerfil, PerfilCargo } from "../../api/types";

interface ResultadoCv {
  respuestas_extraidas: Record<string, boolean | number | string | null>;
  evaluacion: EvaluacionPerfil;
  texto_extraido_preview: string;
}

export default function AdminCvScreening() {
  const [perfiles, setPerfiles] = useState<PerfilCargo[]>([]);
  const [perfilCodigo, setPerfilCodigo] = useState("");
  const [archivo, setArchivo] = useState<File | null>(null);
  const [cargando, setCargando] = useState(false);
  const [resultado, setResultado] = useState<ResultadoCv | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get<PerfilCargo[]>("/api/auth/perfiles").then(setPerfiles);
  }, []);

  const perfil = perfiles.find((p) => p.codigo === perfilCodigo);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!perfilCodigo || !archivo) return;
    setError("");
    setResultado(null);
    setCargando(true);
    try {
      const form = new FormData();
      form.append("perfil_codigo", perfilCodigo);
      form.append("archivo", archivo);
      const r = await api.post<ResultadoCv>("/api/admin/cv-screening", form);
      setResultado(r);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al procesar el CV");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-blue-900 mb-1">Pre-filtrado de CV con IA</h1>
      <p className="text-sm text-gray-500 mb-6">
        Adjunta un CV en PDF y el sistema completa el mismo cuestionario de perfil del cargo, a partir del texto del
        documento. Es solo una ayuda de lectura: no crea ninguna cuenta ni postulacion, y la persona debe declarar
        y aceptar su propia informacion cuando se registre.
      </p>

      <form onSubmit={onSubmit} className="bg-white border border-gray-200 rounded-lg p-5 mb-6 grid gap-3 max-w-lg">
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <select
          value={perfilCodigo}
          onChange={(e) => setPerfilCodigo(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2"
          required
        >
          <option value="">Selecciona el cargo</option>
          {perfiles.map((p) => (
            <option key={p.codigo} value={p.codigo}>
              {p.nombre}
            </option>
          ))}
        </select>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setArchivo(e.target.files?.[0] ?? null)}
          className="text-sm"
          required
        />
        <button disabled={cargando} className="bg-blue-700 text-white rounded py-2 font-medium disabled:opacity-50">
          {cargando ? "Procesando..." : "Filtrar CV"}
        </button>
      </form>

      {resultado && (
        <div className="grid gap-4 max-w-2xl">
          <div
            className={`border rounded-lg p-4 ${resultado.evaluacion.cumple ? "border-green-300 bg-green-50 text-green-900" : "border-red-300 bg-red-50 text-red-900"}`}
          >
            <div className="font-semibold mb-1">
              {perfil?.nombre}: {resultado.evaluacion.cumple ? "cumpliria el perfil" : "no cumpliria el perfil"}
            </div>
            {resultado.evaluacion.motivos.length > 0 && (
              <ul className="list-disc list-inside text-sm">
                {resultado.evaluacion.motivos.map((m) => (
                  <li key={m}>{m}</li>
                ))}
              </ul>
            )}
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h2 className="font-semibold text-sm mb-2">Datos que la IA leyo del CV</h2>
            <table className="w-full text-left text-sm">
              <tbody>
                {perfil?.preguntas.map((p) => {
                  const valor = resultado.respuestas_extraidas[p.id];
                  return (
                    <tr key={p.id} className="border-t border-gray-100">
                      <td className="py-1.5 pr-3 text-gray-600">{p.texto}</td>
                      <td className="py-1.5 font-medium">
                        {valor === null || valor === undefined ? (
                          <span className="text-gray-400">No aparece en el CV</span>
                        ) : typeof valor === "boolean" ? (
                          valor ? "Si" : "No"
                        ) : (
                          String(valor)
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <details className="bg-white border border-gray-200 rounded-lg p-4 text-sm">
            <summary className="cursor-pointer font-semibold">Ver texto extraido del PDF (para verificar la lectura)</summary>
            <pre className="whitespace-pre-wrap text-gray-600 mt-2 text-xs">{resultado.texto_extraido_preview}</pre>
          </details>
        </div>
      )}
    </div>
  );
}
