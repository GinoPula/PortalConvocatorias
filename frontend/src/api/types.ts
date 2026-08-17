export interface Usuario {
  id: number;
  email: string;
  roles: string[];
}

export interface Requisito {
  id: number;
  tipo: string;
  descripcion: string;
  valor: string;
  obligatorio: boolean;
}

export interface CriterioPuntaje {
  id: number;
  nombre: string;
  puntaje_maximo: number;
}

export interface Plaza {
  id: number;
  codigo: string;
  cargo: string;
  numero_plazas: number;
  remuneracion: number | null;
  lugar: string;
  tipo_contrato: string;
  jornada: string;
  requisitos: Requisito[];
  criterios_puntaje: CriterioPuntaje[];
}

export interface Convocatoria {
  id: number;
  codigo: string;
  nombre: string;
  regimen: string;
  dependencia: string;
  es_en_sede: boolean;
  sede: string;
  descripcion: string;
  requisitos_texto: string;
  deseable_texto: string;
  objetivo: string;
  estado: string;
  fecha_publicacion: string | null;
  fecha_inicio: string | null;
  fecha_cierre: string | null;
  plazas: Plaza[];
}

export interface ConvocatoriaListItem {
  id: number;
  codigo: string;
  nombre: string;
  regimen: string;
  sede: string;
  estado: string;
  fecha_cierre: string | null;
}

export interface Postulante {
  id: number;
  tipo_documento: string;
  numero_documento: string;
  nombres: string;
  apellidos: string;
  fecha_nacimiento: string | null;
  sexo: string;
  direccion: string;
  departamento: string;
  provincia: string;
  distrito: string;
  telefono: string;
  ruc: string;
}

export interface FormacionAcademica {
  id: number;
  nivel: string;
  institucion: string;
  carrera: string;
  grado: string;
  fecha_inicio: string | null;
  fecha_fin: string | null;
  estado: string;
}

export interface ExperienciaLaboral {
  id: number;
  institucion: string;
  sector: string;
  cargo: string;
  fecha_inicio: string | null;
  fecha_fin: string | null;
  descripcion: string;
}

export interface ResumenExperiencia {
  total_meses: number;
  anios: number;
  meses: number;
  dias: number;
  meses_sector_publico: number;
  meses_sector_privado: number;
}

export interface DocumentoPostulante {
  id: number;
  document_type_id: number;
  nombre_original: string;
  tamano_bytes: number;
  estado: string;
}

export interface RequisitoValidado {
  requirement_id: number;
  tipo: string;
  descripcion: string;
  valor_requerido: string;
  obligatorio: boolean;
  cumple: boolean;
  motivo: string;
}

export interface ValidacionPrevia {
  puede_postular: boolean;
  requisitos: RequisitoValidado[];
  motivo_bloqueo: string;
}

export interface Postulacion {
  id: number;
  position_id: number;
  estado: string;
  declaracion_jurada_aceptada: boolean;
  declaracion_jurada_fecha: string | null;
  codigo_constancia: string | null;
  creado_en: string;
  postulante_nombre: string | null;
  postulante_documento: string | null;
  plaza_cargo: string | null;
}

export interface HistorialEstado {
  estado_anterior: string | null;
  estado_nuevo: string;
  comentario: string;
  cambiado_en: string;
}

export interface PostulacionDetalle extends Postulacion {
  historial_estados: HistorialEstado[];
}

export interface EvaluationItemOut {
  id: number;
  requirement_id: number;
  cumple: boolean;
  comentario: string;
}

export interface ScoreOut {
  id: number;
  scoring_criterion_id: number;
  puntaje_obtenido: number;
  comentario: string;
}

export interface Evaluacion {
  id: number;
  application_id: number;
  evaluador_id: number | null;
  supervisor_id: number | null;
  resultado: string;
  puntaje_total: number | null;
  observaciones: string;
  aprobado_por_supervisor: boolean;
  creado_en: string;
  items: EvaluationItemOut[];
}

export interface RankingItem {
  application_id: number;
  postulante_nombre: string;
  postulante_documento: string;
  puntaje_total: number | null;
  resultado: string;
  estado_postulacion: string;
}
