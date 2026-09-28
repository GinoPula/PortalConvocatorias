import type { PerfilCargo, PerfilPregunta, Respuesta } from "../api/types";

// Solo para la vista previa: el backend vuelve a evaluar las respuestas al guardar.
function incumple(p: PerfilPregunta, valor: Respuesta | undefined): boolean {
  if (!p.eliminatoria) return false;
  if (p.tipo === "si_no") return valor !== true;
  if (p.tipo === "numero") return typeof valor !== "number" || valor < (p.minimo ?? 0);
  return typeof valor !== "string" || !(p.validas ?? []).includes(valor);
}

function preguntasIncumplidas(perfil: PerfilCargo | undefined, respuestas: Record<string, Respuesta>) {
  if (!perfil) return [];
  return perfil.preguntas.filter((p) => incumple(p, respuestas[p.id]));
}

interface Props {
  perfiles: PerfilCargo[];
  perfilCodigo: string;
  respuestas: Record<string, Respuesta>;
  onPerfilChange: (codigo: string) => void;
  onRespuesta: (id: string, valor: Respuesta) => void;
}

export default function CuestionarioPerfil({ perfiles, perfilCodigo, respuestas, onPerfilChange, onRespuesta }: Props) {
  const perfil = perfiles.find((p) => p.codigo === perfilCodigo);
  const faltantes = preguntasIncumplidas(perfil, respuestas);

  return (
    <div className="flex flex-col gap-3">
      <label className="text-sm font-medium text-gray-700">
        Cargo al que postulas
        <select
          value={perfilCodigo}
          onChange={(e) => onPerfilChange(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 w-full mt-1 font-normal"
          required
        >
          <option value="">Selecciona un cargo</option>
          {perfiles.map((p) => (
            <option key={p.codigo} value={p.codigo}>
              {p.nombre}
            </option>
          ))}
        </select>
      </label>

      {perfil && (
        <>
          <p className="text-xs text-gray-500">
            Tus respuestas tienen caracter de declaracion jurada y seran verificadas con tus documentos. Declarar informacion falsa
            constituye delito de falsa declaracion en procedimiento administrativo.
          </p>

          {perfil.preguntas.map((p) => (
            <div key={p.id} className="border border-gray-200 rounded p-3 flex flex-col gap-2">
              <span className="text-sm text-gray-800">{p.texto}</span>

              {p.tipo === "si_no" && (
                <div className="flex gap-4 text-sm">
                  {[true, false].map((v) => (
                    <label key={String(v)} className="flex items-center gap-1">
                      <input
                        type="radio"
                        name={p.id}
                        checked={respuestas[p.id] === v}
                        onChange={() => onRespuesta(p.id, v)}
                        required
                      />
                      {v ? "Si" : "No"}
                    </label>
                  ))}
                </div>
              )}

              {p.tipo === "numero" && (
                <input
                  type="number"
                  min={0}
                  max={80}
                  step="0.5"
                  value={typeof respuestas[p.id] === "number" ? (respuestas[p.id] as number) : ""}
                  onChange={(e) => onRespuesta(p.id, e.target.value === "" ? null : Number(e.target.value))}
                  className="border border-gray-300 rounded px-3 py-2 w-32"
                  required
                />
              )}

              {p.tipo === "opcion" && (
                <select
                  value={typeof respuestas[p.id] === "string" ? (respuestas[p.id] as string) : ""}
                  onChange={(e) => onRespuesta(p.id, e.target.value || null)}
                  className="border border-gray-300 rounded px-3 py-2 w-48"
                  required
                >
                  <option value="">Selecciona</option>
                  {(p.opciones ?? []).map((o) => (
                    <option key={o}>{o}</option>
                  ))}
                </select>
              )}
            </div>
          ))}

          {faltantes.length > 0 ? (
            <div className="text-sm bg-amber-50 border border-amber-300 text-amber-900 rounded p-3">
              Con estas respuestas <strong>no cumples el perfil</strong> de este cargo ({faltantes.length} requisito
              {faltantes.length > 1 ? "s" : ""}). Podras registrarte, pero no podras postular a este cargo.
            </div>
          ) : (
            <div className="text-sm bg-green-50 border border-green-300 text-green-900 rounded p-3">
              Cumples los requisitos minimos declarados para este cargo.
            </div>
          )}
        </>
      )}
    </div>
  );
}
