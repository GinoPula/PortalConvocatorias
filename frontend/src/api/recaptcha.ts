import { RECAPTCHA_SITE_KEY } from "./client";

const TIEMPO_ESPERA_MS = 10000;

/** Pide a Google reCAPTCHA v3 un token para esta accion. No hay casilla que marcar:
 * se ejecuta en segundo plano y el token va oculto en la peticion. */
export function obtenerTokenRecaptcha(action: string): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!RECAPTCHA_SITE_KEY) {
      reject(new Error("Falta configurar la clave de reCAPTCHA (RECAPTCHA_SITE_KEY) en el servidor."));
      return;
    }

    const limite = setTimeout(() => {
      reject(new Error("No se pudo cargar el verificador de Google (reCAPTCHA). Revisa tu conexion y recarga la pagina."));
    }, TIEMPO_ESPERA_MS);

    function intentar() {
      const g = window.grecaptcha;
      if (!g || !g.execute) {
        setTimeout(intentar, 200);
        return;
      }
      g.ready(() => {
        g.execute(RECAPTCHA_SITE_KEY, { action })
          .then((token) => {
            clearTimeout(limite);
            resolve(token);
          })
          .catch(() => {
            clearTimeout(limite);
            reject(new Error("No se pudo verificar con Google reCAPTCHA. Intenta de nuevo."));
          });
      });
    }

    intentar();
  });
}
