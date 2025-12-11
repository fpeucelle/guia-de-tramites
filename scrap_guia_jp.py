import json
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

# -------------------------------------------------------------------
# Configuración
# -------------------------------------------------------------------

SOURCE_URLS = [
    "https://www.juschubut.gov.ar/index.php/guia-de-tramites",
    "https://www.juschubut.gov.ar/index.php/guia-de-tramites-pm-jppm",
    "https://www.juschubut.gov.ar/index.php/guia-de-tramites-rw-jprw",
    "https://www.juschubut.gov.ar/index.php/guia-de-tramites-sa-jpsa",
]

OUTPUT_FILE = "tramites_contenido.json"

# Títulos de secciones que NO queremos considerar como trámites
STOP_HEADINGS = {
    "sitios de interés",
    "ubicación del stj",
    "circunscripciones",
}


# -------------------------------------------------------------------
# Funciones utilitarias
# -------------------------------------------------------------------

def normalize_heading(text: str) -> str:
    """
    Normaliza un título de heading para comparar de forma robusta
    (minúsculas, sin espacios extra, sin ':' al final).
    """
    if text is None:
        return ""
    cleaned = text.strip().strip(":")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.lower()


def classify_link(href_abs: str) -> str:
    """
    Clasifica un enlace según su tipo:
    - mailto: correo
    - tel: teléfono
    - mismo dominio juschubut: interno
    - otro dominio: externo
    """
    if not href_abs:
        return "desconocido"

    if href_abs.startswith("mailto:"):
        return "mail"

    if href_abs.startswith("tel:"):
        return "telefono"

    parsed = urlparse(href_abs)

    # Sin dominio explícito: lo consideramos interno relativo
    if not parsed.netloc:
        return "interno"

    # Dominio del PJCh
    if "juschubut.gov.ar" in parsed.netloc:
        return "interno"

    return "externo"


def fetch_html(url: str) -> str:
    """
    Descarga el HTML de una URL con un User-Agent amigable.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    # Ajustamos encoding si Requests la detecta mejor
    if resp.apparent_encoding:
        resp.encoding = resp.apparent_encoding
    return resp.text


def get_main_container(soup: BeautifulSoup) -> Tag:
    """
    Intenta ubicar el contenedor principal del artículo.
    Si no lo encuentra, vuelve a body para no perder nada.
    Esta parte es deliberadamente flexible para Joomla.
    """
    # Algunos selectores típicos de Joomla / artículos
    selectors = [
        "article.item-page",
        "div.item-page",
        "div[itemprop='articleBody']",
        "div.blog",
        "main",
    ]

    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return el

    # Último recurso: el body completo
    return soup.body or soup


def extract_juzgado_title(container: Tag) -> str:
    """
    Busca un título tipo 'Guía de trámites del Juzgado de Paz de ...'
    en h1/h2. Si no lo encuentra, devuelve el primer h1/h2 disponible.
    """
    if container is None:
        return ""

    # Primero, uno que contenga explícitamente 'Guía de trámites'
    for tag_name in ("h1", "h2"):
        for tag in container.find_all(tag_name):
            txt = tag.get_text(strip=True)
            if "Guía de trámites" in txt or "Guia de trámites" in txt or "Guia de tramites" in txt:
                return txt

    # Si no, primer h1/h2 que aparezca
    for tag_name in ("h1", "h2"):
        tag = container.find(tag_name)
        if tag:
            return tag.get_text(strip=True)

    return ""


def extract_tramites_from_container(container: Tag, url: str, page_title: str, juzgado_title: str):
    """
    A partir del contenedor principal de la página, arma una lista
    de registros (uno por trámite) con contenido y enlaces.
    """
    records = []

    if container is None:
        return records

    headings = container.find_all("h3")
    if not headings:
        return records

    order = 0

    for h in headings:
        titulo_tramite = (h.get_text(strip=True) or "").strip()
        if not titulo_tramite:
            continue

        norm = normalize_heading(titulo_tramite)

        # Filtramos los headings que el usuario no quiere conservar
        if norm in STOP_HEADINGS:
            continue

        # Tomamos todo lo que viene después del h3 hasta el próximo h2/h3
        content_nodes = []
        for sib in h.next_siblings:
            # Si llegamos a otro h2/h3, termina este bloque
            if isinstance(sib, Tag) and sib.name in ("h2", "h3"):
                break

            # Ignoramos espacios vacíos
            if isinstance(sib, NavigableString):
                if not sib.strip():
                    continue
                # Guardamos texto suelto como nodo
                content_nodes.append(sib)
            elif isinstance(sib, Tag):
                content_nodes.append(sib)

        # Si no hay contenido, lo salteamos (normalmente no debería pasar)
        if not content_nodes:
            continue

        # HTML crudo del tramo
        contenido_html = "".join(str(node) for node in content_nodes).strip()

        # Texto plano (normalizamos saltos de línea)
        tmp_soup = BeautifulSoup(contenido_html, "html.parser")
        texto_con_saltos = tmp_soup.get_text("\n", strip=True)
        # Lo dejo en una sola línea larga para facilitar análisis posterior
        contenido_texto = " ".join(line.strip() for line in texto_con_saltos.splitlines() if line.strip())

        # Enlaces dentro del bloque
        enlaces = []
        for a in tmp_soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href:
                continue
            href_abs = urljoin(url, href)
            texto_enlace = a.get_text(strip=True) or ""
            title_attr = a.get("title") or ""
            tipo = classify_link(href_abs)

            enlaces.append(
                {
                    "href": href,
                    "href_absoluto": href_abs,
                    "texto": texto_enlace,
                    "titulo": title_attr,
                    "tipo": tipo,
                }
            )

        order += 1

        record = {
            "pagina_url": url,
            "pagina_titulo": page_title,
            "juzgado_titulo": juzgado_title,
            "tramite_orden": order,
            "tramite_titulo": titulo_tramite,
            "tramite_contenido_html": contenido_html,
            "tramite_contenido_texto": contenido_texto,
            "enlaces": enlaces,
        }

        records.append(record)

    return records


def process_page(url: str):
    """
    Procesa una página de guía de trámites:
    - Descarga HTML
    - Identifica contenedor principal
    - Extrae título del juzgado
    - Extrae todos los trámites (h3 + contenido + enlaces)
    """
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    page_title = soup.title.get_text(strip=True) if soup.title else ""

    container = get_main_container(soup)
    juzgado_title = extract_juzgado_title(container)

    return extract_tramites_from_container(container, url, page_title, juzgado_title)


# -------------------------------------------------------------------
# Punto de entrada
# -------------------------------------------------------------------

def main():
    all_records = []

    for url in SOURCE_URLS:
        print(f"Procesando: {url}")
        try:
            records = process_page(url)
            print(f"  -> {len(records)} trámites detectados")
            all_records.extend(records)
        except Exception as e:
            print(f"  !! Error procesando {url}: {e}")

    # Guardamos todo en un único JSON listo para análisis posterior
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    print(f"\nListo. Se guardaron {len(all_records)} trámites en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
