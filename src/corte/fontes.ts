import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

loadFont({ family: "Anton", url: staticFile("fonts/Anton.woff2") });
loadFont({ family: "PoppinsX", url: staticFile("fonts/Poppins-800.woff2"), weight: "800" });
loadFont({ family: "PoppinsS", url: staticFile("fonts/Poppins-600.woff2"), weight: "600" });
loadFont({ family: "PlayfairI", url: staticFile("fonts/Playfair-700i.woff2"), weight: "700", style: "italic" });

export const FONTE_GIGANTE = "Anton, Impact, sans-serif";
export const FONTE_LEGENDA = "PoppinsX, Poppins, Arial Black, sans-serif";
export const FONTE_LEVE = "PoppinsS, Poppins, Arial, sans-serif";
export const FONTE_EMOCAO = "PlayfairI, Georgia, serif";

// estilo "simples" (legenda palavra por palavra, tipo Helvetica Bold)
loadFont({ family: "InterB", url: staticFile("fonts/Inter-Bold.otf"), weight: "700" });
loadFont({ family: "InterS", url: staticFile("fonts/Inter-SemiBold.otf"), weight: "600" });
export const FONTE_SIMPLES = "InterB, Helvetica Neue, Helvetica, Arial, sans-serif";
export const FONTE_MARCA = "InterS, Helvetica Neue, Helvetica, Arial, sans-serif";
