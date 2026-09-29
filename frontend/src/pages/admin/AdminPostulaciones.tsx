import { useEffect, useState } from "react";
import { api, ApiError } from "../../api/client";
import type { EvaluacionPerfil, Evaluacion, Plaza, Postulacion, RankingItem } from "../../api/types";

const PAGINA = 20;

const SIGUIENTE: Record<string, string[]> = {
  RECIBIDA: ["EN_EVALUACION", "RETIRADA"],
  EN_EVALUACION: ["APTA", "NO_APTA"],
  APTA: ["ENTREVISTA", "RETIRADA"],
  NO_APTA: ["APELACION"],
  APELACION: ["EN_EVALUACION"],
  ENTREVISTA: ["SELECCIONADA", "NO_SELECCIONADA"],
};

export default function AdminPostulaciones() {
  const [lista, setLista] = useState<Postulacion[]>([]);
  const [filtroEstado, setFiltroEstado] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [offset, setOffset] = useState(0);
  const [hayMas, setHayMas] = useState(false);
  const [seleccionada, setSeleccionada] = useState<Postulacion | null>(null);
  const [plaza, setPlaza] = useState<Plaza | null>(null);
  const [evaluacion, setEvaluacion] = useState<Evaluacion | null>(null);
  const [ranking, setRanking] = useState<RankingItem[]>([]);
  const [perfil, setPerfil] = useState<Record<string, EvaluacionPerfil> | null>(null);
  const [error, setError] = useState("");

  async function cargar(desdeCero: boolean) {
    const nuevoOffset = desdeCero ? 0 : offset;
    const query = new URLSearchParams({ limit: String(PAGINA), offset: String(nuevoOffset) });
    if (filtroEstado) query.set("estado", filtroEstado);
    if (busqueda) query.set("q", busqueda);
    const pagina = await api.get<Postulacion[]>(`/api/admin/postulaciones?${query}`);
    setLista((prev) => (desdeCero ? pagina : [...prev, ...pagina]));
    setOffset(nuevoOffset + pagina.length);
    setHayMas(pagina.length === PAGINA);
  }

  useEffect(() => {
    cargar(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroEstado, busqueda]);

  async function seleccionar(p: Postulacion) {
    setSeleccionada(p);
    setError("");
    const pl = await api.get<Plaza>(`/api/admin/plazas/${p.position_id}`);
    setPlaza(pl);
    try {
      setEvaluacion(await api.get<Evaluacion>(`/api/admin/postulaciones/${p.id}/evaluacion`));
    } catch {
      setEvaluacion(null);
    }
    try {
      setRanking(await api.get<RankingItem[]>(`/api/admin/plazas/${p.position_id}/ranking`));
    } catch {
      setRanking([]);
    }
    try {
      setPerfil(await api.get<Record<string, EvaluacionPerfil>>(`/api/admin/postulaciones/${p.id}/perfil`));
    } catch {
      setPerfil(null);
    }
  }

  async function transicionar(id: number, estado: string) {
    try {
      await api.post(`/api/admin/postulaciones/${id}/transicion/${estado}`, { comentario: "" });
      await cargar(true);
      if (seleccionada?.id === id) {
        const actualizado = await api.get<Postulacion[]>(`/api/admin/postulaciones`).then((l) => l.find((x) => x.id === id)!);
        seleccionar(actualizado);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al cambiar de estado");
    }
  }

  async function evaluar(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!seleccionada || !plaza) return;
    setError("");
    const form = new FormData(e.currentTarget);
    const resultado = String(form.get("resultado"));

    const items = plaza.requisitos.map((r) => ({
      requirement_id: r.id,
      cumple: form.get(`req_${r.id}`) === "on",
      comentario: "",
    }));
    const puntajes = plaza.criterios_puntaje.map((c) => ({
      scoring_criterion_id: c.id,
      puntaje_obtenido: Number(form.get(`crit_${c.id}`) || 0),
      comentario: "",
    }));

    try {
      const nueva = await api.post<Evaluacion>(`/api/admin/postulaciones/${seleccionada.id}/evaluacion`, {
        resultado,
        observaciones: String(form.get("observaciones") || ""),
        items,
        puntajes,
      });
      setEvaluacion(nueva);
      await cargar(true);
      const actualizado = await api.get<Postulacion[]>(`/api/admin/postulaciones`).then((l) => l.find((x) => x.id === seleccionada.id)!);
      setSeleccionada(actualizado);
      const rk = await api.get<RankingItem[]>(`/api/admin/plazas/${seleccionada.position_id}/ranking`);
      setRanking(rk);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al registrar evaluacion");
    }
  }

  async function aprobar() {
    if (!seleccionada) return;
    try {
      const ev = await api.post<Evaluacion>(`/api/admin/postulaciones/${seleccionada.id}/evaluacion/aprobar`);
      setEvaluacion(ev);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al aprobar");
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-blue-900 mb-4">Postulaciones</h1>

      <div className="flex gap-2 mb-4 text-sm flex-wrap">
        {["", "RECIBIDA", "EN_EVALUACION", "APTA", "NO_APTA", "ENTREVISTA", "SELECCIONADA", "NO_SELECCIONADA", "RETIRADA"].map((e) => (
          <button
            key={e}
            onClick={() => setFiltroEstado(e)}
            className={`px-3 py-1.5 rounded ${filtroEstado === e ? "bg-blue-700 text-white" : "bg-gray-100"}`}
          >
            {e || "Todas"}
          </button>
        ))}
      </div>

      <input
        value={busqueda}
        onChange={(e) => setBusqueda(e.target.value)}
        placeholder="Buscar por nombre, apellido o documento..."
        className="border border-gray-300 rounded px-3 py-2 mb-4 w-full max-w-sm"
      />

      <div className="grid grid-cols-2 gap-6">
        <div>
          <div className="grid gap-2">
            {lista.map((p) => (
              <button
                key={p.id}
                onClick={() => seleccionar(p)}
                className={`text-left bg-white border rounded-lg p-3 w-full ${seleccionada?.id === p.id ? "border-blue-600" : "border-gray-200"}`}
              >
                <div className="font-medium">{p.postulante_nombre}</div>
                <div className="text-xs text-gray-500">
                  {p.postulante_documento} &middot; {p.plaza_cargo} &middot; <strong>{p.estado}</strong>
                </div>
              </button>
            ))}
            {lista.length === 0 && <p className="text-gray-400 text-sm">No hay postulaciones.</p>}
          </div>
          {hayMas && (
            <button onClick={() => cargar(false)} className="mt-3 text-sm bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded">
              Cargar mas
            </button>
          )}
        </div>

        <div>
          {error && <div className="text-red-600 text-sm mb-3">{error}</div>}
          {seleccionada && plaza ? (
            <div className="bg-white border border-gray-200 rounded-lg p-5">
              <h2 className="font-semibold text-blue-900 mb-1">{seleccionada.postulante_nombre}</h2>
              <p className="text-sm text-gray-500 mb-3">
                {plaza.cargo} &middot; Estado: <strong>{seleccionada.estado}</strong>
              </p>

              <div className="flex gap-2 mb-4">
                {(SIGUIENTE[seleccionada.estado] || []).map((sig) => (
                  <button
                    key={sig}
                    onClick={() => transicionar(seleccionada.id, sig)}
                    className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded"
                  >
                    → {sig}
                  </button>
                ))}
              </div>

              {perfil && (
                <div className="border-t border-gray-100 pt-4 mb-4">
                  <h3 className="font-semibold mb-2 text-sm">Cuestionario de perfil declarado</h3>
                  {Object.keys(perfil).length === 0 ? (
                    <p className="text-sm text-gray-400">
                      Esta plaza no exige cuestionario de perfil, o el postulante no completo ninguno.
                    </p>
                  ) : (
                    <div className="grid gap-2">
                      {Object.entries(perfil).map(([codigo, ev]) => (
                        <div
                          key={codigo}
                          className={`text-sm border rounded p-3 ${ev.cumple ? "border-green-300 bg-green-50 text-green-900" : "border-red-300 bg-red-50 text-red-900"}`}
                        >
                          <div className="font-medium">
                            {codigo}: {ev.cumple ? "cumple el perfil" : "no cumple el perfil"}
                          </div>
                          {ev.motivos.length > 0 && (
                            <ul className="list-disc list-inside mt-1">
                              {ev.motivos.map((m) => (
                                <li key={m}>{m}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {seleccionada.estado === "EN_EVALUACION" && (
                <form onSubmit={evaluar} className="border-t border-gray-100 pt-4">
                  <h3 className="font-semibold mb-2 text-sm">Registrar evaluacion</h3>
                  {plaza.requisitos.map((r) => (
                    <label key={r.id} className="flex items-center gap-2 text-sm mb-1">
                      <input type="checkbox" name={`req_${r.id}`} />
                      {r.descripcion || `${r.tipo}: ${r.valor}`}
                    </label>
                  ))}
                  {plaza.criterios_puntaje.map((crit) => (
                    <label key={crit.id} className="flex items-center gap-2 text-sm mb-1">
                      {crit.nombre} (max {crit.puntaje_maximo})
                      <input type="number" step="0.1" name={`crit_${crit.id}`} className="border border-gray-300 rounded px-2 py-1 w-24" />
                    </label>
                  ))}
                  <select name="resultado" className="border border-gray-300 rounded px-3 py-2 mt-2 mr-2" required>
                    <option value="APTO">APTO</option>
                    <option value="NO_APTO">NO APTO</option>
                    <option value="OBSERVADO">OBSERVADO</option>
                  </select>
                  <textarea name="observaciones" placeholder="Observaciones" className="border border-gray-300 rounded px-3 py-2 w-full mt-2" />
                  <button className="bg-blue-700 text-white rounded px-4 py-2 mt-2">Guardar evaluacion</button>
                </form>
              )}

              {evaluacion && (
                <div className="border-t border-gray-100 pt-4 mt-4 text-sm">
                  <h3 className="font-semibold mb-2">Evaluacion registrada</h3>
                  <p>Resultado: <strong>{evaluacion.resultado}</strong> &middot; Puntaje total: {evaluacion.puntaje_total ?? "-"}</p>
                  <p>Aprobado por supervisor: {evaluacion.aprobado_por_supervisor ? "Si" : "No"}</p>
                  {!evaluacion.aprobado_por_supervisor && (
                    <button onClick={aprobar} className="bg-green-100 text-green-800 rounded px-3 py-1.5 mt-2">
                      Aprobar (Supervisor)
                    </button>
                  )}
                </div>
              )}

              {ranking.length > 0 && (
                <div className="border-t border-gray-100 pt-4 mt-4 text-sm">
                  <h3 className="font-semibold mb-2">Ranking de la plaza</h3>
                  <table className="w-full text-left">
                    <thead>
                      <tr className="text-xs text-gray-500">
                        <th>Postulante</th>
                        <th>Puntaje</th>
                        <th>Resultado</th>
                        <th>Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ranking.map((r) => (
                        <tr key={r.application_id}>
                          <td>{r.postulante_nombre}</td>
                          <td>{r.puntaje_total ?? "-"}</td>
                          <td>{r.resultado}</td>
                          <td>{r.estado_postulacion}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">Selecciona una postulacion para ver el detalle.</p>
          )}
        </div>
      </div>
    </div>
  );
}
