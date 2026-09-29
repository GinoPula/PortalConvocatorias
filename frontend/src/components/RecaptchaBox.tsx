import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import { RECAPTCHA_SITE_KEY } from "../api/client";

export interface RecaptchaHandle {
  reset: () => void;
}

interface Props {
  onToken: (token: string) => void;
}

// Casilla "No soy un robot" de Google reCAPTCHA v2. El script se carga en index.html;
// aqui solo se renderiza el widget cuando ese script ya esta listo (puede tardar
// unos milisegundos mas que React) y se avisa al padre con el token via onToken.
const RecaptchaBox = forwardRef<RecaptchaHandle, Props>(function RecaptchaBox({ onToken }, ref) {
  const contenedorRef = useRef<HTMLDivElement>(null);
  const widgetId = useRef<number | null>(null);
  const [errorRender, setErrorRender] = useState("");

  useImperativeHandle(ref, () => ({
    reset() {
      if (widgetId.current !== null) window.grecaptcha?.reset(widgetId.current);
    },
  }));

  useEffect(() => {
    let cancelado = false;
    let intentos = 0;

    function intentarRenderizar() {
      if (cancelado || widgetId.current !== null || !contenedorRef.current) return;
      const g = window.grecaptcha;
      if (!g || !g.render) {
        intentos += 1;
        if (intentos > 50) {
          // Mas de 10s esperando: el script de Google no cargo (bloqueado, sin internet, etc.)
          setErrorRender("No se pudo cargar el verificador de Google (reCAPTCHA). Revisa tu conexion y recarga la pagina.");
          return;
        }
        setTimeout(intentarRenderizar, 200);
        return;
      }
      try {
        widgetId.current = g.render(contenedorRef.current, { sitekey: RECAPTCHA_SITE_KEY, callback: onToken });
      } catch (e) {
        // Clave invalida, o el dominio actual no esta autorizado para esta clave en el panel de Google.
        setErrorRender(
          `No se pudo mostrar la verificacion de Google: ${e instanceof Error ? e.message : "clave o dominio no valido"}. ` +
            "Verifica que este dominio este autorizado para RECAPTCHA_SITE_KEY en el panel de Google.",
        );
      }
    }

    intentarRenderizar();
    return () => {
      cancelado = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!RECAPTCHA_SITE_KEY) {
    return <p className="text-xs text-red-600">Falta configurar la clave de reCAPTCHA (RECAPTCHA_SITE_KEY).</p>;
  }
  if (errorRender) {
    return <p className="text-xs text-red-600">{errorRender}</p>;
  }

  return <div ref={contenedorRef} />;
});

export default RecaptchaBox;
