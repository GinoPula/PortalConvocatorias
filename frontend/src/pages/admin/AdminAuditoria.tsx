import { useEffect, useState } from "react";
import { api } from "../../api/client";
import type { AuditLogEntry } from "../../api/types";

const ACCIONES = ["", "LOGIN", "LOGOUT", "CREAR", "EDITAR", "ELIMINAR", "CAMBIO_ESTADO", "EVALUAR"];
const ENTIDADES = ["", "USER", "CONVOCATION", "POSITION", "APPLICATION", "EVALUATION"];
const PAGINA = 30;

export default function AdminAuditoria() {
  const [lista, setLista] = useState<AuditLogEntry[]>([]);
  const [accion, setAccion] = useState("");
  const [entidad, setEntidad] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [offset, setOffset] = useState(0);
  const [hayMas, setHayMas] = useState(false);

  async function cargar(desdeCero: boolean) {
    const nuevoOffset = desdeCero ? 0 : offset;
    const query = new URLSearchParams({ limit: String(PAGINA), offset: String(nuevoOffset) });
    if (accion) query.set("accion", accion);
    if (entidad) query.set("entidad", entidad);
    if (busqueda) query.set("q", busqueda);
    const pagina = await api.get<AuditLogEntry[]>(`/api/admin/auditoria?${query}`);
    setLista((prev) => (desdeCero ? pagina : [...prev, ...pagina]));
    setOffset(nuevoOffset + pagina.length);
    setHayMas(pagina.length === PAGINA);
  }

  useEffect(() => {
    cargar(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accion, entidad, busqueda]);

  return (
    <div>
      <h1 className="text-2xl font-bold text-blue-900 mb-1">Auditoria</h1>
      <p className="text-sm text-gray-500 mb-4">Quien hizo que, sobre que registro, y cuando.</p>

      <div className="flex gap-2 mb-4 flex-wrap">
        <select value={accion} onChange={(e) => setAccion(e.target.value)} className="border border-gray-300 rounded px-3 py-2 text-sm">
          {ACCIONES.map((a) => (
            <option key={a} value={a}>
              {a || "Todas las acciones"}
            </option>
          ))}
        </select>
        <select value={entidad} onChange={(e) => setEntidad(e.target.value)} className="border border-gray-300 rounded px-3 py-2 text-sm">
          {ENTIDADES.map((en) => (
            <option key={en} value={en}>
              {en || "Todas las entidades"}
            </option>
          ))}
        </select>
        <input
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          placeholder="Buscar por correo de quien hizo la accion..."
          className="border border-gray-300 rounded px-3 py-2 text-sm flex-1 min-w-[240px]"
        />
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th className="px-3 py-2">Fecha</th>
              <th className="px-3 py-2">Quien</th>
              <th className="px-3 py-2">Accion</th>
              <th className="px-3 py-2">Entidad</th>
              <th className="px-3 py-2">Detalle</th>
            </tr>
          </thead>
          <tbody>
            {lista.map((r) => (
              <tr key={r.id} className="border-t border-gray-100">
                <td className="px-3 py-2 text-gray-500 whitespace-nowrap">{new Date(r.creado_en).toLocaleString()}</td>
                <td className="px-3 py-2">{r.usuario_email || "(sistema)"}</td>
                <td className="px-3 py-2 font-medium">{r.accion}</td>
                <td className="px-3 py-2">
                  {r.entidad}
                  {r.entidad_id ? ` #${r.entidad_id}` : ""}
                </td>
                <td className="px-3 py-2 text-gray-600">
                  {r.valor_anterior && <span>{r.valor_anterior} &rarr; </span>}
                  {r.valor_nuevo || ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {lista.length === 0 && <p className="text-gray-400 text-sm p-4">No hay registros de auditoria con estos filtros.</p>}
      </div>

      {hayMas && (
        <button onClick={() => cargar(false)} className="mt-4 text-sm bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded">
          Cargar mas
        </button>
      )}
    </div>
  );
}
