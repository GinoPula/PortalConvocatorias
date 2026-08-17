import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { DocumentoPostulante, ExperienciaLaboral, FormacionAcademica, Postulante, ResumenExperiencia } from "../api/types";

export default function Perfil() {
  const [postulante, setPostulante] = useState<Postulante | null>(null);
  const [formacion, setFormacion] = useState<FormacionAcademica[]>([]);
  const [experiencia, setExperiencia] = useState<ExperienciaLaboral[]>([]);
  const [resumen, setResumen] = useState<ResumenExperiencia | null>(null);
  const [documentos, setDocumentos] = useState<DocumentoPostulante[]>([]);
  const [mensaje, setMensaje] = useState("");

  async function cargarTodo() {
    setPostulante(await api.get("/api/postulante/profile"));
    setFormacion(await api.get("/api/postulante/academic-records"));
    setExperiencia(await api.get("/api/postulante/work-experiences"));
    setResumen(await api.get("/api/postulante/work-experiences/resumen"));
    setDocumentos(await api.get("/api/postulante/documents"));
  }

  useEffect(() => {
    cargarTodo();
  }, []);

  async function guardarDatos(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!postulante) return;
    const form = new FormData(e.currentTarget);
    await api.put("/api/postulante/profile", {
      departamento: form.get("departamento"),
      provincia: form.get("provincia"),
      distrito: form.get("distrito"),
      direccion: form.get("direccion"),
      telefono: form.get("telefono"),
    });
    setMensaje("Datos personales actualizados.");
    cargarTodo();
  }

  async function agregarFormacion(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    await api.post("/api/postulante/academic-records", {
      nivel: form.get("nivel"),
      institucion: form.get("institucion"),
      carrera: form.get("carrera"),
      estado: "CONCLUIDO",
    });
    e.currentTarget.reset();
    cargarTodo();
  }

  async function agregarExperiencia(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const fecha_fin = form.get("fecha_fin");
    await api.post("/api/postulante/work-experiences", {
      institucion: form.get("institucion"),
      sector: form.get("sector"),
      cargo: form.get("cargo"),
      fecha_inicio: form.get("fecha_inicio"),
      fecha_fin: fecha_fin || null,
    });
    e.currentTarget.reset();
    cargarTodo();
  }

  async function subirDocumento(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setMensaje("");
    const form = new FormData(e.currentTarget);
    const archivo = form.get("archivo") as File;
    if (!archivo || archivo.size === 0) return;
    const body = new FormData();
    body.append("archivo", archivo);
    try {
      await api.post("/api/postulante/documents?document_type_id=1", body);
      e.currentTarget.reset();
      cargarTodo();
    } catch (err) {
      setMensaje(err instanceof ApiError ? String(err.detail) : "Error al subir el documento");
    }
  }

  if (!postulante) return <p className="text-gray-500">Cargando...</p>;

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-bold text-blue-900">
        Mi perfil &mdash; {postulante.nombres} {postulante.apellidos}
      </h1>
      {mensaje && <div className="text-blue-800 bg-blue-50 border border-blue-200 rounded p-3 text-sm">{mensaje}</div>}

      <section className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="font-semibold text-blue-900 mb-3">Datos personales</h2>
        <p className="text-sm text-gray-500 mb-3">
          {postulante.tipo_documento}: {postulante.numero_documento}
        </p>
        <form onSubmit={guardarDatos} className="grid grid-cols-2 gap-3">
          <input name="departamento" placeholder="Departamento" defaultValue={postulante.departamento} className="border border-gray-300 rounded px-3 py-2" />
          <input name="provincia" placeholder="Provincia" defaultValue={postulante.provincia} className="border border-gray-300 rounded px-3 py-2" />
          <input name="distrito" placeholder="Distrito" defaultValue={postulante.distrito} className="border border-gray-300 rounded px-3 py-2" />
          <input name="telefono" placeholder="Telefono" defaultValue={postulante.telefono} className="border border-gray-300 rounded px-3 py-2" />
          <input name="direccion" placeholder="Direccion" defaultValue={postulante.direccion} className="border border-gray-300 rounded px-3 py-2 col-span-2" />
          <button className="bg-blue-700 text-white rounded py-2 col-span-2">Guardar datos personales</button>
        </form>
      </section>

      <section className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="font-semibold text-blue-900 mb-3">Formacion academica</h2>
        <ul className="mb-3 text-sm text-gray-700 list-disc list-inside">
          {formacion.map((f) => (
            <li key={f.id}>
              {f.nivel} &mdash; {f.carrera} ({f.institucion})
            </li>
          ))}
        </ul>
        <form onSubmit={agregarFormacion} className="flex gap-2 flex-wrap">
          <select name="nivel" className="border border-gray-300 rounded px-3 py-2">
            <option>Secundaria</option>
            <option>Tecnico</option>
            <option>Bachiller</option>
            <option>Titulo</option>
            <option>Maestria</option>
            <option>Doctorado</option>
          </select>
          <input name="institucion" placeholder="Institucion" className="border border-gray-300 rounded px-3 py-2" required />
          <input name="carrera" placeholder="Carrera" className="border border-gray-300 rounded px-3 py-2" />
          <button className="bg-blue-100 text-blue-800 rounded px-4 py-2">Agregar</button>
        </form>
      </section>

      <section className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="font-semibold text-blue-900 mb-3">Experiencia laboral</h2>
        {resumen && (
          <div className="bg-gray-50 rounded p-3 text-sm mb-3">
            Total: <strong>{resumen.anios} anios, {resumen.meses} meses</strong> &middot; Sector publico: {resumen.meses_sector_publico} meses &middot; Sector privado: {resumen.meses_sector_privado} meses
          </div>
        )}
        <ul className="mb-3 text-sm text-gray-700 list-disc list-inside">
          {experiencia.map((exp) => (
            <li key={exp.id}>
              {exp.cargo} en {exp.institucion} ({exp.sector}) &mdash; {exp.fecha_inicio} a {exp.fecha_fin || "actualidad"}
            </li>
          ))}
        </ul>
        <form onSubmit={agregarExperiencia} className="flex gap-2 flex-wrap items-center">
          <input name="institucion" placeholder="Institucion" className="border border-gray-300 rounded px-3 py-2" required />
          <select name="sector" className="border border-gray-300 rounded px-3 py-2">
            <option value="PUBLICO">Publico</option>
            <option value="PRIVADO">Privado</option>
          </select>
          <input name="cargo" placeholder="Cargo" className="border border-gray-300 rounded px-3 py-2" />
          <input name="fecha_inicio" type="date" className="border border-gray-300 rounded px-3 py-2" required />
          <input name="fecha_fin" type="date" className="border border-gray-300 rounded px-3 py-2" />
          <button className="bg-blue-100 text-blue-800 rounded px-4 py-2">Agregar</button>
        </form>
      </section>

      <section className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="font-semibold text-blue-900 mb-3">Documentos</h2>
        <ul className="mb-3 text-sm text-gray-700">
          {documentos.map((d) => (
            <li key={d.id}>
              <a href={api.fileUrl(`/api/postulante/documents/${d.id}/descargar`)} target="_blank" className="text-blue-700 hover:underline">
                {d.nombre_original}
              </a>{" "}
              ({(d.tamano_bytes / 1024).toFixed(0)} KB)
            </li>
          ))}
        </ul>
        <form onSubmit={subirDocumento} className="flex gap-2 items-center">
          <input name="archivo" type="file" accept="application/pdf" className="text-sm" />
          <button className="bg-blue-100 text-blue-800 rounded px-4 py-2">Subir CV (PDF)</button>
        </form>
      </section>
    </div>
  );
}
