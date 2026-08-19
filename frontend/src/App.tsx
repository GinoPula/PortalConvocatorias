import { Routes, Route, Navigate } from "react-router-dom";
import PublicLayout from "./components/PublicLayout";
import AdminLayout from "./components/AdminLayout";
import RutaProtegida from "./components/RutaProtegida";
import Login from "./pages/Login";
import Registro from "./pages/Registro";
import Convocatorias from "./pages/Convocatorias";
import ConvocatoriaDetalle from "./pages/ConvocatoriaDetalle";
import Perfil from "./pages/Perfil";
import MisPostulaciones from "./pages/MisPostulaciones";
import AdminConvocatorias from "./pages/admin/AdminConvocatorias";
import AdminConvocatoriaDetalle from "./pages/admin/AdminConvocatoriaDetalle";
import AdminPostulaciones from "./pages/admin/AdminPostulaciones";
import AdminUsuarios from "./pages/admin/AdminUsuarios";

const ROLES_STAFF = ["ADMINISTRADOR", "RRHH", "EVALUADOR", "SUPERVISOR", "AUDITOR"];

function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<Convocatorias />} />
        <Route path="/convocatorias/:id" element={<ConvocatoriaDetalle />} />
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route
          path="/perfil"
          element={
            <RutaProtegida rolesPermitidos={["POSTULANTE"]}>
              <Perfil />
            </RutaProtegida>
          }
        />
        <Route
          path="/mis-postulaciones"
          element={
            <RutaProtegida rolesPermitidos={["POSTULANTE"]}>
              <MisPostulaciones />
            </RutaProtegida>
          }
        />
      </Route>

      <Route
        path="/admin"
        element={
          <RutaProtegida rolesPermitidos={ROLES_STAFF}>
            <AdminLayout />
          </RutaProtegida>
        }
      >
        <Route index element={<Navigate to="convocatorias" replace />} />
        <Route path="convocatorias" element={<AdminConvocatorias />} />
        <Route path="convocatorias/:id" element={<AdminConvocatoriaDetalle />} />
        <Route path="postulaciones" element={<AdminPostulaciones />} />
        <Route
          path="usuarios"
          element={
            <RutaProtegida rolesPermitidos={["ADMINISTRADOR"]}>
              <AdminUsuarios />
            </RutaProtegida>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
