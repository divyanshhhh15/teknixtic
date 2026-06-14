# Teknixtic fix: input not going / output not coming

- [ ] Confirm static JS is loaded from `{% static 'js/index.js' %}` and that browser console shows no 404.
- [x] Copy/restore JS to `app/static/js/index.js` so template can load it.
- [x] Make JS robust when backend returns only `{ response: ... }`.
- [ ] If still failing: inspect network tab for `/chatbot/` POST, and check backend errors (GROQ_API_KEY / JSON parsing).

