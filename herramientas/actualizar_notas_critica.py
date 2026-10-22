"""
Descarga de Wikidata (licencia CC0) la nota de la crítica de OpenCritic (sobre 100)
de los juegos de PS5, PS4, PS3 y PS Vita, y la guarda en datos/notas-critica.json.
Platinum Hunter la usa en «La comunidad dice» mientras un juego no tiene votos.
"""
import json, re, sys, urllib.parse, urllib.request, datetime, pathlib

CONSULTA = """
SELECT ?juego ?nota ?titulo WHERE {
  ?juego wdt:P31 wd:Q7889; wdt:P400 ?consola.
  VALUES ?consola { wd:Q63184502 wd:Q5014725 wd:Q10683 wd:Q188808 }
  ?juego p:P444 ?valoracion. ?valoracion ps:P444 ?nota; pq:P447 wd:Q21039459.
  { ?juego rdfs:label ?titulo } UNION { ?juego skos:altLabel ?titulo }
  FILTER(LANG(?titulo) IN ("en","es","fr","de","it","pt","ja","ko","zh"))
}
"""

def main():
    url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(CONSULTA)
    req = urllib.request.Request(url, headers={"User-Agent": "PlatinumHunter/1.0 (https://nxplosion-lab.github.io; duk3x.dev@gmail.com)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        filas = json.load(r)["results"]["bindings"]
    juegos = {}
    for f in filas:
        m = re.match(r"^\s*(\d{1,3})\s*/\s*100\s*$", f["nota"]["value"])  # «87/100»; el «97%» es otra métrica
        if not m:
            continue
        nota = int(m.group(1))
        g = juegos.setdefault(f["juego"]["value"].rsplit("/", 1)[-1], {"nota": nota, "titulos": set()})
        g["nota"] = max(g["nota"], nota)
        g["titulos"].add(f["titulo"]["value"].strip())
    salida = {
        "fuente": "OpenCritic vía Wikidata (CC0)",
        "actualizado": datetime.date.today().isoformat(),
        "juegos": sorted(
            ({"id": k, "nota": v["nota"], "titulos": sorted(v["titulos"])} for k, v in juegos.items()),
            key=lambda x: x["id"],
        ),
    }
    if len(salida["juegos"]) < 1000:
        sys.exit(f"Muy pocos juegos ({len(salida['juegos'])}): no se sobrescribe la lista")
    destino = pathlib.Path(__file__).resolve().parent.parent / "datos" / "notas-critica.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(salida['juegos'])} juegos con nota guardados en {destino.name}")

if __name__ == "__main__":
    main()
