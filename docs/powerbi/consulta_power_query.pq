// PATITAS-PETS - Consulta de Power Query para cargar la base consolidada.
// Uso: Inicio > Obtener datos > Consulta en blanco > Editor avanzado > pegar todo > Listo.
// Cambie el nombre de la consulta a: PQRS
//
// Origen: el CSV publicado en el repositorio de GitHub (no hay que cambiar rutas).
// La primera vez, Power BI pide credenciales para el sitio: elija "Anónimo" > Conectar.
//
// ALTERNATIVA SIN INTERNET: comente la línea de Web.Contents y quite el comentario de
// File.Contents, escribiendo la ruta donde está el archivo en su computador.

let
    Archivo = Web.Contents("https://raw.githubusercontent.com/anuarcaldon-sys/patitas-pets-pqrs/main/data/exportaciones/base_consolidada_pqrs.csv"),
    // Archivo = File.Contents("C:\Users\SU_USUARIO\Documents\patitas-pets-pqrs\data\exportaciones\base_consolidada_pqrs.csv"),

    Origen = Csv.Document(Archivo, [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),

    // Quita la marca BOM (U+FEFF) que puede quedar pegada al primer encabezado
    NombresLimpios = Table.TransformColumnNames(Encabezados, each Text.Remove(_, {Character.FromNumber(65279)})),

    // Las celdas vacías (PQRS sin solución o ya solucionadas) se vuelven nulas antes de cambiar el tipo
    Vacios = Table.ReplaceValue(NombresLimpios, "", null, Replacer.ReplaceValue,
        {"fecha_solucion", "dias_respuesta", "dias_para_vencer"}),

    Tipos = Table.TransformColumnTypes(Vacios, {
        {"radicado", type text},
        {"tipo_solicitud", type text},
        {"id", Int64.Type},
        {"tipo_documento", type text},
        {"perfil_solicitante", type text},
        {"fecha_radicacion", type datetime},
        {"canal_recepcion", type text},
        {"asunto_titulo", type text},
        {"tipo_mascota", type text},
        {"campus_relacionado", type text},
        {"fecha_maxima_respuesta", type datetime},
        {"estado_peticion", type text},
        {"usuario_registro", type text},
        {"nombre_registrador", type text},
        {"rol_registrador", type text},
        {"fecha_solucion", type datetime},
        {"dias_respuesta", Int64.Type},
        {"antiguedad_dias", Int64.Type},
        {"dias_para_vencer", Int64.Type},
        {"estado_plazo", type text}
    }, "en-US")
in
    Tipos
