# Ideeën voor ProjectBoard

## Doel
Een persoonlijke tool om mijn projecten, notities en taken te organiseren.  
Niet bedoeld voor meerdere gebruikers, puur voor mijzelf.

---

## Features

### MVP (Minimum Viable Product)
- [ ] Overzichtspagina met projecten
- [ ] Project detailpagina (titel + beschrijving)
- [ ] Notities (markdown support)
- [ ] Takenbord (Open → In Progress → Done)

### Later misschien
- [ ] Deadlines en reminders
- [ ] Labels/tags voor taken
- [ ] Uploads (screenshots, documenten)
- [ ] Sync met GitHub issues
- [ ] Archiveren van projecten
- [ ] Dark mode

---

## Technische keuzes
- Frontend: **SvelteKit 5**
- Backend: **FastAPI**
- Database: **SQLite** (simpel en genoeg voor lokaal gebruik)
- Auth: niet nodig (alleen persoonlijk gebruik)
- Styling: Tailwind CSS (optioneel)

---

## Inspiratie / ideeën
- Kanban style drag & drop (zoals Trello)
- Kleine notitie-editor met markdown
- Export van data naar JSON/Markdown
- Project deadlines visueel in een kleine kalender
- Mobile-friendly layout

---

## Open vragen
- Hoe ga ik data opslaan: direct SQLite of via een ORM zoals SQLModel?
- Hoeveel detail moeten taken hebben (alleen titel of ook beschrijving, deadline)?
- Wil ik projecten kunnen sorteren (datum, naam, status)?
- Hoe ga ik backups maken van de database?
