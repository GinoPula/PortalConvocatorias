import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../../api/client";
import type { ConvocatoriaListItem } from "../../api/types";
import { DEPARTAMENTOS_PERU } from "../../data/departamentos";

const REGIMENES_AUTOGENERADOS = new Set(["CAS", "LOCADOR"]);

export default function AdminConvocatorias() {
  const [lista, setLista] = useState<ConvocatoriaListItem[]>([]);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [esEnSede, setEsEnSede] = useState(false);
  const [regimen, setRegimen] = useState("CAS");
  const [codigo, setCodigo] = useState("");
  const [error, setError] = useState("");

  async function cargar() {
    setLista(await api.get("/api/admin/convocatorias"));
  }

  useEffect(() => {
    cargar();
  }, []);

  useEffect(() => {
    if (!mostrarForm) return;
    if (REGIMENES_AUTOGENERADOS.has(regimen)) {
      api.get<{ codigo: string }>(`/api/admin/convocatorias/siguiente-codigo?regimen=${regimen}`).then((r) => setCodigo(r.codigo));
    } else {
      setCodigo("");
    }
  }, [regimen, mostrarForm]);

  async function crear(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      await api.post("/api/admin/convocatorias", {
        codigo: form.get("codigo"),
        nombre: form.get("nombre"),
        regimen: form.get("regimen"),
        dependencia: form.get("dependencia"),
        es_en_sede: form.get("es_en_sede") === "on",
        sede: form.get("es_en_sede") === "on" ? form.get("departamento") : "",
        descripcion: form.get("descripcion"),
        requisitos_texto: form.get("requisitos_texto"),
        deseable_texto: form.get("deseable_texto"),
        objetivo: "",
      });
      setMostrarForm(false);
      setEsEnSede(false);
      setRegimen("CAS");
      setCodigo("");
      cargar();
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Error al crear");
    }
  }

  async function transicionar(id: number, estado: string) {
    await api.post(`/api/admin/convocatorias/${id}/transicion/${estado}`);
    cargar();
  }

  const SIGUIENTE: Record<string, string[]> = {
    BORRADOR: ["PUBLICADA"],
    PUBLICADA: ["ABIERTA"],
    ABIERTA: ["CERRADA"],
    CERRADA: ["EN_EVALUACION"],
    EN_EVALUACION: ["FINALIZADA"],
  };

  const codigoAutogenerado = REGIMENES_AUTOGENERADOS.has(regimen);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-900">Convocatorias</h1>
        <button onClick={() => setMostrarForm(!mostrarForm)} className="bg-blue-700 text-white px-4 py-2 rounded">
          {mostrarForm ? "Cancelar" : "+ Nueva convocatoria"}
        </button>
      </div>

      {mostrarForm && (
        <form onSubmit={crear} className="bg-white border border-gray-200 rounded-lg p-5 mb-6 grid grid-cols-2 gap-3">
          {error && <div className="col-span-2 text-red-600 text-sm">{error}</div>}

          <select
            name="regimen"
            value={regimen}
            onChange={(e) => setRegimen(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2"
            required
          >
            <option value="CAS">CAS</option>
            <option value="LOCADOR">Locador</option>
            <option value="OTROS">Otros</option>
          </select>

          <input
            name="codigo"
            placeholder="Codigo (ej. CAS-2026-002)"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            readOnly={codigoAutogenerado}
            className={`border border-gray-300 rounded px-3 py-2 ${codigoAutogenerado ? "bg-gray-100 text-gray-600" : ""}`}
            required
          />

          <input
            name="nombre"
            placeholder="Nombre de la Convocatoria"
            className="border border-gray-300 rounded px-3 py-2 col-span-2"
            required
          />

          <input name="dependencia" placeholder="Dependencia" className="border border-gray-300 rounded px-3 py-2 col-span-2" />

          <label className="flex items-center gap-2 text-sm col-span-2">
            <input type="checkbox" name="es_en_sede" checked={esEnSede} onChange={(e) => setEsEnSede(e.target.checked)} />
            La convocatoria es en una sede/local del ministerio
          </label>

          {esEnSede && (
            <select name="departamento" className="border border-gray-300 rounded px-3 py-2 col-span-2" required>
              <option value="">Selecciona el departamento</option>
              {DEPARTAMENTOS_PERU.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          )}

          <textarea
            name="descripcion"
            placeholder="Acerca del puesto"
            className="border border-gray-300 rounded px-3 py-2 col-span-2"
            rows={3}
          />
          <textarea
            name="requisitos_texto"
            placeholder="Requisitos"
            className="border border-gray-300 rounded px-3 py-2 col-span-2"
            rows={3}
          />
          <textarea
            name="deseable_texto"
            placeholder="Deseable (Habilidades Tecnicas)"
            className="border border-gray-300 rounded px-3 py-2 col-span-2"
            rows={3}
          />

          <button className="bg-blue-700 text-white rounded py-2 col-span-2">Crear en BORRADOR</button>
        </form>
      )}

      <div className="grid gap-3">
        {lista.map((c) => (
          <div key={c.id} className="bg-white border border-gray-200 rounded-lg p-4 flex items-center justify-between">
            <div>
              <Link to={`/admin/convocatorias/${c.id}`} className="font-semibold text-blue-900 hover:underline">
                {c.nombre}
              </Link>
              <div className="text-sm text-gray-500">
                {c.codigo} &middot; {c.sede || "Remoto"} &middot; <span className="font-medium">{c.estado}</span>
              </div>
            </div>
            <div className="flex gap-2">
              {(SIGUIENTE[c.estado] || []).map((siguiente) => (
                <button
                  key={siguiente}
                  onClick={() => transicionar(c.id, siguiente)}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded"
                >
                  {siguiente}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
