"""Rastrejadors de cercadors i d'IA, agrupats per funció.

Font: documentació pública de cada empresa (OpenAI, Anthropic, Google, Perplexity, Apple, Meta,
Common Crawl). Revisa la llista cada pocs mesos: en surten de nous.

- cerca: indexen per a resultats de cerca (clàssics i amb IA, RAG en viu). Bloquejar-los = no sortir citat.
- usuari: entren quan un usuari demana a l'assistent que llegeixi una URL concreta.
- entrenament: recullen dades per entrenar models. Bloquejar-los no treu de la cerca, però CCBot
  (Common Crawl) alimenta l'entrenament de molts models: si es bloqueja, la marca no entra al corpus.
"""

BOTS = {
    "cerca": {
        "Googlebot": "Google (cerca i AI Overviews)",
        "Bingbot": "Bing (alimenta Copilot i part de ChatGPT)",
        "OAI-SearchBot": "OpenAI · cerca de ChatGPT",
        "Claude-SearchBot": "Anthropic · cerca de Claude",
        "PerplexityBot": "Perplexity · índex de cerca",
        "Applebot": "Apple · Siri i Spotlight",
        "DuckAssistBot": "DuckDuckGo · respostes amb IA",
    },
    "usuari": {
        "ChatGPT-User": "OpenAI · quan l'usuari dona una URL",
        "Claude-User": "Anthropic · quan l'usuari dona una URL",
        "Perplexity-User": "Perplexity · quan l'usuari dona una URL",
        "Google-NotebookLM": "Google NotebookLM",
    },
    "entrenament": {
        "GPTBot": "OpenAI · entrenament",
        "ClaudeBot": "Anthropic · entrenament",
        "Google-Extended": "Google · Gemini (token de robots.txt, no és un rastrejador propi)",
        "Applebot-Extended": "Apple · entrenament (token de robots.txt)",
        "CCBot": "Common Crawl · corpus obert que fan servir molts models",
        "meta-externalagent": "Meta · entrenament",
    },
}

# User-agents aproximats per provar si el servidor o el CDN (Cloudflare, WAF) els bloqueja amb 403.
UA = {
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Bingbot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "OAI-SearchBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot",
    "ChatGPT-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.1; +https://openai.com/gptbot",
    "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "Claude-SearchBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-SearchBot/1.0; +https://www.anthropic.com)",
    "Claude-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-User/1.0; +https://www.anthropic.com)",
    "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "Perplexity-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)",
    "CCBot": "CCBot/2.0 (https://commoncrawl.org/faq/)",
    "Applebot": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15 (Applebot/0.1; +http://www.apple.com/go/applebot)",
}

# Política de robots.txt (lloc.yaml → bots_ia)
#   permetre (per defecte): tothom pot entrar
#   sense-entrenament: es bloquegen els d'entrenament, però NO CCBot ni els de cerca/usuari
#   nomes-cerca: es bloquegen tots els d'entrenament, CCBot inclòs
POLITIQUES = ("permetre", "sense-entrenament", "nomes-cerca")


def bloquejats(politica):
    if politica == "sense-entrenament":
        return [b for b in BOTS["entrenament"] if b != "CCBot"]
    if politica == "nomes-cerca":
        return list(BOTS["entrenament"])
    return []


def tots():
    return {b: (grup, desc) for grup, d in BOTS.items() for b, desc in d.items()}


LOCALES = {"es": "es_ES", "ca": "ca_ES", "en": "en_GB", "fr": "fr_FR", "pt": "pt_PT", "it": "it_IT",
           "de": "de_DE", "eu": "eu_ES", "gl": "gl_ES", "nl": "nl_NL"}
