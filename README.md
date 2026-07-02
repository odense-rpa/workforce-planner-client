# workforce-planner-client

Python-bibliotek der automatiserer brugeradministration i Workforce Planner via en Playwright-drevet Chromium-browser med Odense IDP-godkendelse.

> Denne klient er ikke officielt støttet eller godkendt af leverandøren bag Workforce Planner. Brug på eget ansvar.

## Nuværende funktionalitet

- **Slet personressource** (`slet_personressource`): Søger en bruger op via e-mail og sletter den tilknyttede personressource
- **Deaktiver bruger** (`deaktiver_bruger`): Søger en bruger op i brugeradministrationen via e-mail, åbner brugerposten, fjerner fluebenet i "Aktiv" og gemmer

## Installation

```bash
uv add git+https://github.com/odense-rpa/workforce-planner-client
```

Installer desuden Chromium-browseren:

```bash
uv run playwright install chromium
```

## Forudsætninger

- Python ≥ 3.13
- Adgang til Workforce Planner-instansen
- Brugernavn og adgangskode til Odense IDP

## Brug

```python
import asyncio
from workforce_planner_client import WorkforcePlannerClient

async def main():
    async with WorkforcePlannerClient(
        base_url="https://workforce.example.dk",
        username="brugernavn",
        password="adgangskode",
    ) as client:
        # Slet en personressource
        await client.slet_personressource("medarbejder@kommune.dk")

        # Deaktiver en bruger
        await client.deaktiver_bruger("medarbejder@kommune.dk")

asyncio.run(main())
```

## Licens

MIT
